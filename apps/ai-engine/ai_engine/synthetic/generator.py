"""Generate a synthetic organization from a spec, reproducibly.

Algorithm, in three phases so side-assignment is settled before any text exists:

  A. **Sides.** For each topic template, draw a group of holders (bounded by
     ``corroboration_range``, preferring the least-loaded participants so coverage
     is even). For a ``contradiction_rate`` share of contradiction-capable topics,
     split off a minority of one who states the denial. With probability
     ``minority_correct_rate`` the MINORITY is the correct side — making the whole
     majority wrong, which is what stops a vote-counting scorer from acing the
     benchmark.
  B. **Coverage.** Any participant still holding nothing is given a topic, so
     ``size`` means "employees interviewed" rather than "employees generated".
     (This can push one topic a single holder above ``corroboration_range``, which
     is treated as a target rather than a hard bound.)
  C. **Text.** Only now are statements built and truth ids minted, so a
     participant's veridicality follows from which side they ended up on.

Everything is driven by one seeded RNG, so the same spec always yields the same org.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field, replace

from ..subjects.simulated import LatentTruth, Persona
from .model import OrgSpec, PlantedContradiction, SyntheticOrg
from .topics import (
    BIAS_AREAS,
    BIAS_CORES,
    BIAS_PREFIXES,
    BIAS_SLOT,
    BIAS_TIER,
    TOPIC_TEMPLATES,
    TopicTemplate,
)

_FIRST_NAMES = (
    "Ana", "Ben", "Cleo", "Dev", "Eve", "Finn", "Gia", "Hal", "Iris", "Jon",
    "Kaya", "Liam", "Mira", "Noor", "Omar", "Pia", "Quinn", "Rhys", "Sana", "Tao",
    "Uma", "Vik", "Wren", "Xan", "Yara", "Zane",
)

_ROLES = (
    "Dispatcher", "Operations Analyst", "Coordinator", "Support Lead", "Planner",
    "Warehouse Lead", "Account Manager", "Scheduler", "Quality Analyst",
    "Shift Supervisor", "Procurement Officer", "Billing Specialist",
)


@dataclass
class _TopicState:
    template: TopicTemplate
    affirmers: list[str] = field(default_factory=list)
    deniers: list[str] = field(default_factory=list)
    minority_correct: bool = False

    @property
    def planted(self) -> bool:
        return bool(self.deniers)

    def holders(self) -> list[str]:
        return self.affirmers + self.deniers

    def is_wrong(self, holder: str) -> bool:
        """Is this holder on the false side of a planted contradiction?"""
        if not self.planted:
            return False
        denies = holder in self.deniers
        return (not denies) if self.minority_correct else denies


def _participant_name(index: int) -> str:
    base = _FIRST_NAMES[index % len(_FIRST_NAMES)]
    cycle = index // len(_FIRST_NAMES)
    return base if cycle == 0 else f"{base}{cycle + 1}"


def _assign_candor(names: list[str], spec: OrgSpec, rng: random.Random) -> dict[str, str]:
    """Deterministic counts from the mix, then shuffled — so even a small org
    reflects the requested distribution instead of sampling noise."""
    weights = spec.candor_weights()
    pool: list[str] = []
    for level, share in weights.items():
        pool.extend([level] * round(share * len(names)))
    while len(pool) < len(names):
        pool.append("neutral")
    pool = pool[: len(names)]
    rng.shuffle(pool)
    return dict(zip(names, pool))


def _pick_least_loaded(
    eligible: list[str], load: dict[str, int], count: int, rng: random.Random
) -> list[str]:
    """Choose ``count`` participants, preferring those holding the fewest topics."""
    shuffled = eligible[:]
    rng.shuffle(shuffled)                     # randomise ties reproducibly
    shuffled.sort(key=lambda n: load[n])      # stable: least-loaded first
    return shuffled[:count]


def generate_org(spec: OrgSpec | None = None, **overrides) -> SyntheticOrg:
    spec = spec or OrgSpec()
    if overrides:
        spec = replace(spec, **overrides)
    rng = random.Random(spec.seed)

    size = max(1, spec.size)
    names = [_participant_name(i) for i in range(size)]
    roles = {n: _ROLES[i % len(_ROLES)] for i, n in enumerate(names)}
    candor = _assign_candor(names, spec, rng)

    load: dict[str, int] = {n: 0 for n in names}
    # Slots, not topic keys: two topics can share an interviewer slot, and a person
    # holding both would only ever be asked once, silently losing the second.
    held: dict[str, set[tuple[str, ...]]] = {n: set() for n in names}

    topic_order = list(TOPIC_TEMPLATES)
    lo, hi = spec.resolved_corroboration_range(len(topic_order))
    rng.shuffle(topic_order)

    # --- Phase A: sides -----------------------------------------------------
    states: list[_TopicState] = []
    for template in topic_order:
        eligible = [
            n for n in names
            if load[n] < spec.topics_per_person and template.slot not in held[n]
        ]
        if not eligible:
            continue

        # Decide the plant BEFORE sizing the group: a contradiction needs two
        # sides, so intending to plant forces at least two holders.
        plant = template.can_contradict and rng.random() < spec.contradiction_rate
        group_size = rng.randint(lo, hi)
        if plant:
            group_size = max(group_size, 2)
        group_size = min(group_size, len(eligible))
        if plant and group_size < 2:
            plant = False

        holders = _pick_least_loaded(eligible, load, group_size, rng)
        state = _TopicState(template=template)
        if plant:
            state.deniers = [holders[-1]]
            state.affirmers = holders[:-1]
            state.minority_correct = rng.random() < spec.minority_correct_rate
        else:
            state.affirmers = holders

        for holder in holders:
            load[holder] += 1
            held[holder].add(template.slot)
        states.append(state)

    # --- Phase B: nobody is mute --------------------------------------------
    for name in names:
        if load[name] > 0:
            continue
        options = [s for s in states if s.template.slot not in held[name]]
        if not options:
            continue
        chosen = rng.choice(options)
        chosen.affirmers.append(name)          # joins the majority side
        load[name] += 1
        held[name].add(chosen.template.slot)

    # --- Phase C: text, ids, and veridicality -------------------------------
    truths: dict[str, list[LatentTruth]] = {n: [] for n in names}
    mistaken: set[str] = set()

    def _add(template: TopicTemplate, holder: str, *, deny: bool, wrong: bool) -> None:
        truth = LatentTruth(
            id=f"{holder.lower()}_{template.key}_{'deny' if deny else 'affirm'}",
            tier=template.tier,
            areas=list(template.areas),
            keywords=list(template.slot),
            statement=template.statement(rng.choice(template.variants), deny=deny),
        )
        truths[holder].append(truth)
        if wrong:
            mistaken.add(truth.id)

    for state in states:
        for holder in state.affirmers:
            _add(state.template, holder, deny=False, wrong=state.is_wrong(holder))
        for holder in state.deniers:
            _add(state.template, holder, deny=True, wrong=state.is_wrong(holder))

    # Bias: unfounded attributions. Always false. Each holder gets a DISTINCT target
    # so they stay single-source — a shared core would make independent bias-holders
    # corroborate each other and manufacture a high-confidence falsehood.
    bias_candidates = [
        n for n in names
        if load[n] < spec.topics_per_person and BIAS_SLOT not in held[n]
    ]
    bias_count = min(round(spec.bias_rate * size), len(bias_candidates))
    bias_holders = _pick_least_loaded(bias_candidates, load, bias_count, rng) if bias_count else []

    # Optionally make some of them share one belief (a correlated misconception).
    correlated_count = round(spec.correlated_bias_rate * len(bias_holders))
    shared_core = BIAS_CORES[0]
    for offset, holder in enumerate(bias_holders):
        if offset < correlated_count:
            core = shared_core
        else:
            core = BIAS_CORES[(offset + 1) % len(BIAS_CORES)]
        truth = LatentTruth(
            id=f"{holder.lower()}_blame_affirm",
            tier=BIAS_TIER,
            areas=list(BIAS_AREAS),
            keywords=list(BIAS_SLOT),
            statement=f"{rng.choice(BIAS_PREFIXES)} {core}",
        )
        truths[holder].append(truth)
        mistaken.add(truth.id)
        load[holder] += 1
        held[holder].add(BIAS_SLOT)

    personas = [
        Persona(
            name=name,
            role=roles[name],
            candor=candor[name],
            background=f"{roles[name]} at {spec.name}.",
            latent_truths=truths[name],
        )
        for name in names
        if truths[name]
    ]

    contradictions = [
        PlantedContradiction(
            topic_key=s.template.key,
            majority=tuple(s.affirmers),
            minority=tuple(s.deniers),
            minority_is_correct=s.minority_correct,
        )
        for s in states if s.planted
    ]

    return SyntheticOrg(
        spec=spec,
        personas=personas,
        mistaken_ids=frozenset(mistaken),
        contradictions=contradictions,
        bias_holders=tuple(bias_holders),
    )
