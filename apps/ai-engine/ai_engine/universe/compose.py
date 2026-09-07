"""Compose + render: dimension tables → a scenario the engine runs today.

``compose`` is pure and seed-deterministic: the same spec id always yields the
same materialized dataset record. ``render`` is total: it either returns a
RenderedScenario (Persona + bank + opening + probes + rules + state) or raises
:class:`CompositionError` naming the violated lint rule — a scenario that only
half-works is the Sam-t1 failure mode at scale, and it is refused at authoring
time (merged taxonomy §3.4, rules F1–F7).
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from ..interview.engine import question_area_index
from ..interview.state import InterviewState
from ..subjects.simulated import LatentTruth, Persona
from .tables import DEFAULT_TABLES, TaxonomyTables

ARCHETYPES = ("strong", "mixed", "weak")
CANDOR = ("guarded", "neutral", "open")


class CompositionError(ValueError):
    """A lint rule was violated — nothing partial ships."""


@dataclass
class ScenarioSpec:
    id: str
    domain: str
    level: str
    kind: str
    objective: str
    difficulty: float
    bars: dict
    competencies: list[str]
    archetype: str
    candor: str
    premise: str
    premise_short: str
    seed: int


@dataclass
class RenderedScenario:
    spec: ScenarioSpec
    persona: Persona
    bank: dict                     # (area, tier) -> question text
    opening: str
    probes: dict                   # area -> specificity-probe text
    areas: tuple
    area_params: dict              # area -> {value, ceiling}
    rules: list[dict]
    state: InterviewState
    question_index: dict           # text -> (area, tier)
    premise: str


def _seed_from(spec_id: str) -> int:
    return int(hashlib.sha256(spec_id.encode("utf-8")).hexdigest()[:8], 16)


def compose(domain: str, level: str, kind: str, *,
            tables: TaxonomyTables = DEFAULT_TABLES,
            case_id: str | None = None, archetype: str = "strong",
            candor: str = "open") -> ScenarioSpec:
    """Resolve domain × level × kind into a ScenarioSpec (pure, seeded)."""
    if domain not in tables.domains:
        raise CompositionError(f"unknown domain {domain!r}")
    if level not in tables.levels:
        raise CompositionError(f"unknown level {level!r}")
    if kind not in tables.kinds:
        raise CompositionError(f"unknown kind {kind!r}")
    if archetype not in ARCHETYPES:
        raise CompositionError(f"unknown archetype {archetype!r}")
    if candor not in CANDOR:
        raise CompositionError(f"unknown candor {candor!r}")

    domain_spec = tables.domains[domain]
    comps = domain_spec["competencies"]
    premise = None
    premise_short = (f"{domain_spec['artifacts'][0]} under "
                     f"{domain_spec['stressors'][0]}")
    if kind in ("case", "debugging", "system_design"):
        premise = next((pr for pr in domain_spec["premises"]
                        if case_id in (None, pr["id"])), None)
        if premise is None:
            raise CompositionError(
                f"domain {domain!r} has no premise matching case_id "
                f"{case_id!r} for kind {kind!r}")
        premise_short = premise["short"]
        case_id = premise["id"]

    spec_id = f"sim/{domain}/{level}/{kind}/{case_id or 'core'}"
    seed = _seed_from(spec_id)
    bars = dict(tables.levels[level])
    depth = bars["required_depth"]
    objective = (f"Assess {', '.join(tables.competencies[c]['name'] for c in comps)} "
                 f"for a {level} {domain_spec['role_title']} via a {kind} interview.")
    # Difficulty is computed, never authored (fairness: an auditable function
    # of declared inputs — merged taxonomy D6).
    archetype_factor = {"strong": 0.0, "mixed": 0.2, "weak": 0.4}[archetype]
    candor_factor = {"open": 0.0, "neutral": 0.34, "guarded": 0.6}[candor]
    difficulty = round(min(1.0, max(0.0,
        0.4 * (depth / 4) + 0.3 * (bars["required_breadth"] / 6)
        + 0.2 * archetype_factor + 0.1 * candor_factor + 0.05)), 3)

    return ScenarioSpec(
        id=spec_id, domain=domain, level=level, kind=kind, objective=objective,
        difficulty=difficulty, bars=bars, competencies=list(comps),
        archetype=archetype, candor=candor, premise=premise["text"] if premise else "",
        premise_short=premise_short, seed=seed)


def render(spec: ScenarioSpec, tables: TaxonomyTables = DEFAULT_TABLES
           ) -> RenderedScenario:
    """Materialize the spec into engine-shaped objects, linting loudly (F1–F7)."""
    domain_spec = tables.domains[spec.domain]
    kind_spec = tables.kinds[spec.kind]

    artifacts = domain_spec["artifacts"]
    artifact = artifacts[spec.seed % len(artifacts)]
    stressor = domain_spec["stressors"][spec.seed % len(domain_spec["stressors"])]

    areas: list[str] = []
    bank: dict[tuple[str, int], str] = {}
    seen_texts: set[str] = set()
    depth = min(spec.bars["required_depth"], 4)
    for comp_id in spec.competencies:
        comp = tables.competencies[comp_id]
        ceiling = min(comp["ceiling"], depth)
        for tier in range(1, ceiling + 1):
            template = kind_spec["bank"][tier]
            text = template.format(
                artifact=artifact, stressor=stressor, comp=_noun(comp, tier),
                premise=f"{spec.premise} " if spec.premise else "",
                premise_short=spec.premise_short).strip()
            if text in seen_texts:  # F5 uniqueness
                raise CompositionError(
                    f"duplicate bank text for ({comp_id}, {tier}): {text!r}")
            seen_texts.add(text)
            bank[(comp_id, tier)] = text
        areas.append(comp_id)

    opening = kind_spec["opening"].format(
        artifact=artifact, premise=f"{spec.premise} " if spec.premise else "",
        premise_short=spec.premise_short).strip()
    if opening in seen_texts:  # F5
        raise CompositionError("opening duplicates a bank text")

    probes: dict[str, str] = {}
    for comp_id in spec.competencies:
        probe = kind_spec["probe"].format(
            comp=_noun(tables.competencies[comp_id], 2),
            artifact=artifact).strip()
        if probe in seen_texts:  # F5
            raise CompositionError(
                f"probe for {comp_id!r} duplicates an existing question text")
        seen_texts.add(probe)
        probes[comp_id] = probe

    # F1 fire-pairing: every bank question must be attributable through the
    # index — a question resume can't attribute is a dead truth at scale.
    index = question_area_index(bank, opening, probes)
    for (area, tier), text in bank.items():
        got = index.get(text)
        if got is None or got[0] != area:
            raise CompositionError(
                f"F1 fire-pairing violated: {text!r} does not resolve to its "
                f"area {area!r}")

    persona = _persona_for(spec, tables, bank)

    # F4 flag reachability: candor cap must reach any fired red flag.
    cap = {"guarded": 1, "neutral": 3, "open": 4}[spec.candor]
    if spec.archetype in ("weak", "mixed") and cap < 2:
        raise CompositionError(
            "F4 flag reachability violated: archetype demands a red-flag truth "
            f"but candor {spec.candor!r} caps disclosure below its tier")

    state = InterviewState(objective=spec.objective, areas=tuple(areas))
    area_params = {c: {"value": tables.competencies[c]["value"],
                       "ceiling": min(tables.competencies[c]["ceiling"], depth)}
                   for c in areas}

    return RenderedScenario(
        spec=spec, persona=persona, bank=bank, opening=opening, probes=probes,
        areas=tuple(areas), area_params=area_params, rules=[],
        state=state, question_index=index, premise=spec.premise)


def _noun(comp: dict, tier: int) -> str:
    nouns = comp.get("nouns", {}).get(tier)
    if nouns is None:
        return comp["name"].lower()
    return nouns[0] if isinstance(nouns, list) else nouns


def _persona_for(spec: ScenarioSpec, tables, bank) -> Persona:
    """A candidate persona whose truths pair with the rendered bank (F1/F2).

    Each (competency, tier) cell in the bank gets a matching truth whose
    keywords derive from the QUESTION text — so it deterministically fires on
    it — and whose statement is curated-voice, parameterized by the wording.
    `weak`/`mixed` archetypes plant a red-flag truth at tier 2 that demands
    the evidence probe; the absence of evidence then becomes mechanically
    visible through vague-streak and strikeout.
    """
    domain_spec = tables.domains[spec.domain]
    role = f"{spec.level.title()} {domain_spec['role_title']}"
    truths: list[LatentTruth] = []
    for comp_id in spec.competencies:
        comp = tables.competencies[comp_id]
        ceiling = min(comp["ceiling"], spec.bars["required_depth"])
        for tier in range(1, ceiling + 1):
            text = bank.get((comp_id, tier))
            if text is None:
                continue
            red_flag = (spec.archetype == "weak" and tier == 2) or (
                spec.archetype == "mixed" and tier == 2
                and comp_id == spec.competencies[-1])
            statement = _statement_voice(spec, comp, tier)
            keywords = _derived_keywords(statement, comp["name"])
            if red_flag:
                statement = ("Honestly we did everything right — the vendor "
                             "failed us and nobody escalated; you can't fix "
                             "other people's mess.")
                keywords = _derived_keywords(statement, comp["name"]) or keywords
            truths.append(LatentTruth(
                id=f"{spec.id.replace('/', '_')}_{comp_id}_{tier}",
                tier=tier, areas=[comp_id], keywords=keywords,
                statement=statement))
    first = ["Priya", "Jordan", "Marcus", "Ines", "Theo", "Wren", "Bram"]
    return Persona(name=first[spec.seed % len(first)], role=role,
                   candor=spec.candor,
                   background=(f"A {spec.archetype} candidate for a "
                               f"{spec.level} {domain_spec['role_title']} role."),
                   latent_truths=truths)


def _statement_voice(spec: ScenarioSpec, comp: dict, tier: int) -> str:
    """Curated-voice statement, parameterized by the competency itself."""
    noun = comp["name"].lower()
    voices = {
        1: (f"Sure — in {spec.premise_short or 'this work'}, the {noun} side is "
            f"where most of my time goes; here's exactly how it runs."),
        2: (f"The {noun} part had a real catch: the first approach stalled and "
            f"the second version is what stuck — that's the honest story."),
        3: (f"The {noun} tradeoff cost us real time, and I made that call — "
            f"here's what it actually took."),
        4: (f"If it doubled tomorrow, I'd revisit my own {noun} choices first — "
            f"honestly, that's the part I'd redo."),
    }
    return voices.get(tier, voices[1])


def _derived_keywords(text: str, exclude: str) -> list[str]:
    """Keywords derived from the text they must fire on (merged taxonomy D4):
    distinctive stems, guaranteed present — the dead-truth bug (Sam's tier-1)
    becomes structurally impossible."""
    words = re.findall(r"[a-z]{5,}", text.lower())
    stop = {"about", "there", "would", "their", "because", "which", "should",
            "actually", "really", "things", "where", "here", "exactly",
            "second", "honest"}
    out = [w for w in words if w not in stop and w != exclude.lower()]
    # two distinctive stems, longest first (more specific wins ties)
    return sorted(set(out), key=len, reverse=True)[:3] or [exclude.lower()[:5]]
