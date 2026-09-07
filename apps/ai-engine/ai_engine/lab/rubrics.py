"""Explicit evaluation rubrics — and which class of evidence backs each one.

Every criterion declares its grader class up front:

  * ``deterministic`` graders read the system's own structures — the strategy's
    chosen move, the recorded state, the gates' verdicts, the rendered report.
    They are reproducible proofs.
  * ``heuristic`` graders approximate a judgment a human might make (length
    bands, leak patterns, vocabulary overlap). They are signal, never truth.
  * ``model`` graders require a live provider. They are DECLARED here and
    reported as UNSCORED when no live model is configured — the lab never
    invents a score for a grader it could not run.

The seven dimensions and their honest mapping onto this system's artifacts:

  relevance         — does the produced turn address the interview's current
                      target area (deterministic in mock: the question bank is
                      indexable; heuristic live: vocabulary overlap).
  correctness       — does the recorded state match the transitions the
                      scenario demands (deterministic: state is inspectable).
  reasoning         — does the strategy choose the intent the state demands
                      (deterministic: the strategy is pure and inspectable).
  communication     — is the utterance clean, sized, and free of leaked
                      internals (heuristic checks, deterministic refusal of
                      specific leak patterns).
  consistency       — does the scenario produce the same behavior across
                      repeats (deterministic comparison at the runner).
  interview_quality — does the full conversation elicit what the persona holds
                      (deterministic: coverage + disclosure counts).
  feedback_quality  — does the report keep provenance and stay inside the
                      firewall (deterministic content checks).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .schemas import DETERMINISTIC, HEURISTIC, MODEL, Scenario

RUBRIC_VERSION = "lab.rubric/v1"


class Unscored(Exception):
    """Raised by a grader that cannot run in this environment (e.g. a model
    grader without a live provider). Never converted into a fake score."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class TurnContext:
    """Everything a grader may look at for one scenario run."""

    scenario: Scenario
    utterance: str                       # the produced interviewer turn
    state: object                        # InterviewState after the turn
    move: object | None                  # the strategy's Move (when available)
    transcript: object                   # the transcript so far
    #: Utterances from repeated runs of the SAME scenario (consistency input).
    repeat_utterances: list[str] = field(default_factory=list)
    #: For full-conversation/report scenarios.
    report_markdown: str | None = None
    findings: list = field(default_factory=list)
    #: Whether the driver closed during this run (close-behavior scenarios).
    closed: bool = False


@dataclass
class RubricSpec:
    id: str
    dimension: str
    grader_class: str
    description: str
    fn: Callable[[TurnContext, dict], tuple[float, str]]


# --- graders ---------------------------------------------------------------

_AREA_VOCAB = {
    "process_reality": ("supposed", "officially", "differ", "real"),
    "workarounds": ("instead", "workaround", "tools"),
    "bottlenecks": ("stall", "pile", "waiting"),
    "wasted_effort": ("redundant", "redone", "effort"),
    "friction": ("decision", "honest"),
    "ai_opportunity": ("repetitive", "rules-based", "sleep"),
}


def _grader_relevance_area(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Does the produced turn address the scenario's target area?

    DETERMINISTIC scope only: the produced utterance must be a known bank
    question whose area matches. When it is not (a live-model phrasing, or a
    non-bank intent like de-escalation), this grader declares itself UNSCORED
    rather than degrading silently — use `relevance/utterance` (substring
    expectations) or `relevance/area-heuristic` for those cases, so the
    evidence class in the report never lies.
    """
    from ..interview.engine import question_area_index

    expected = params.get("expected_area") or (
        ctx.move.target_area if ctx.move is not None else None)
    if expected is None:
        raise Unscored("no expected area and no strategy move to compare against")
    index = question_area_index()
    hit = index.get(ctx.utterance.strip())
    if hit is None:
        raise Unscored(
            "utterance is not a known bank question — the deterministic area "
            "grader cannot judge it; use relevance/utterance or "
            "relevance/area-heuristic for live phrasings")
    area, _tier = hit
    ok = area == expected
    return (1.0 if ok else 0.0), (
        f"utterance is a known bank question for {area!r} "
        f"(expected {expected!r})")


def _grader_relevance_utterance(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Substring expectations for turns whose wording no bank index covers
    (de-escalation, contradiction, closing) — deterministic on content.

    Found adversarially: a de-escalation turn that re-asked the guarded
    question verbatim scored 1.0 on every state/intent criterion, because
    state bookkeeping records the move's CLAIM, not the words. The words are
    the promise; this grader checks them.
    """
    expect = params.get("expect_substrings", [])
    forbid = params.get("forbid_substrings", [])
    if not expect and not forbid:
        raise Unscored("relevance/utterance needs expect_substrings or "
                       "forbid_substrings")
    low = ctx.utterance.lower()
    checks = [(f"contains {s!r}", s.lower() in low) for s in expect]
    checks += [(f"omits {s!r}", s.lower() not in low) for s in forbid]
    passed = sum(1 for _, ok in checks if ok)
    evidence = "; ".join(f"{name}: {'ok' if ok else 'MISS'}" for name, ok in checks)
    return passed / len(checks), evidence


def _grader_relevance_area_heuristic(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """HEURISTIC live-mode fallback: vocabulary overlap with the target area.

    Capped at 0.5 — an overlap approximation must never present as a full
    score. Two DISTINCT word hits required (a duplicated entry or one common
    word used to score 1.0).
    """
    expected = params.get("expected_area") or (
        ctx.move.target_area if ctx.move is not None else None)
    if expected is None:
        raise Unscored("no expected area and no strategy move")
    low = ctx.utterance.lower()
    hits = sorted({w for w in _AREA_VOCAB.get(expected, ()) if w in low})
    score = min(0.5, len(hits) * 0.25)
    return score, (f"heuristic: distinct area-vocabulary hits {hits} for "
                   f"{expected!r} (capped at 0.5 — approximation, not proof)")


def _grader_correctness_state(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Does the recorded state match the transitions the scenario demands?"""
    checks: list[tuple[str, bool]] = []
    want_areas = params.get("areas_touched")
    if want_areas is not None:
        got = set(ctx.state.pending_area and [ctx.state.pending_area] or [])
        for record in ctx.state.history:
            got.add(record.area)
        for area in want_areas:
            checks.append((f"area {area!r} touched", area in got))
    want_tier = params.get("tier_credited")
    if want_tier is not None:
        # The tier the PRODUCED question will credit when answered — the
        # previous answer's credit is history, not this turn's behavior.
        checks.append((f"tier_credited == {want_tier}",
                       ctx.state.pending_tier == want_tier))
    want_pending = params.get("pending_area")
    if want_pending is not None:
        checks.append((f"pending_area == {want_pending!r}",
                       ctx.state.pending_area == want_pending))
    if params.get("expected_closed"):
        checks.append(("driver closed", getattr(ctx, "closed", False)))
    want_covered = params.get("areas_covered_min")
    if want_covered is not None:
        covered = sum(1 for c in ctx.state.coverage.values() if c.level == "covered")
        checks.append((f"areas_covered >= {want_covered}", covered >= want_covered))
    if not checks:
        raise Unscored("correctness/state criterion carries no state expectations")
    passed = sum(1 for _, ok in checks if ok)
    evidence = "; ".join(f"{name}: {'ok' if ok else 'MISS'}" for name, ok in checks)
    return passed / len(checks), evidence


def _grader_reasoning_intent(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Did the strategy choose the intent the state demands?"""
    expected = params.get("expected_intent")
    forbid = params.get("forbid_intent")
    if expected is None and forbid is None:
        raise Unscored("reasoning/intent criterion needs expected_intent or "
                       "forbid_intent")
    if ctx.move is None:
        raise Unscored("no strategy move was recorded for this run")
    intent = ctx.move.intent.value
    if forbid is not None and intent == forbid:
        return 0.0, (f"strategy intent {intent!r} is the FORBIDDEN intent "
                     f"(expected anything but {forbid!r}); "
                     f"rationale: {ctx.move.rationale}")
    if expected is not None:
        ok = intent == expected
        return (1.0 if ok else 0.0), (
            f"strategy intent {intent!r} (expected {expected!r}); "
            f"rationale: {ctx.move.rationale}")
    return 1.0, (f"strategy intent {intent!r} (forbidden {forbid!r} not used); "
                 f"rationale: {ctx.move.rationale}")


_LEAK_PATTERNS = (
    '"utterance"', '"should_close"', '"assessment"', '"next_move"',
    "should_close", "assessment_of_last_answer", "strategic directive",
    "target area:", "vague_streak",
)


def _grader_communication_hygiene(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Heuristic: is the utterance clean, sized, and free of leaked internals?

    Expanded after the adversarial challenge: mid-text JSON objects with any
    key shape, directive prose, and near-echoes of the candidate answer (a
    40+ char substring) now fail too — the old four-pattern list let a turn
    containing `{"target_area": "friction"}` or the strategy's directive prose
    score a perfect 1.0.
    """
    checks: list[tuple[str, bool]] = []
    text = ctx.utterance.strip()
    checks.append(("non-empty", bool(text)))
    checks.append(("length 10..2000", 10 <= len(text) <= 2000))
    leaks = [p for p in _LEAK_PATTERNS if p.lower() in text.lower()]
    json_keys = re.findall(r'"\w+"\s*:', text)
    if json_keys:
        leaks.append(f"JSON-key shape {json_keys[:3]}")
    checks.append(("no leaked internals", not leaks))
    answer = ctx.scenario.candidate_answer.strip()
    near_echo = len(answer) >= 40 and answer[:40].lower() in text.lower()
    checks.append(("not a verbatim/near echo of the candidate answer",
                   not near_echo and text != answer))
    passed = sum(1 for _, ok in checks if ok)
    evidence = "; ".join(
        f"{name}: {'ok' if ok else 'FAILED' + (f' {leaks}' if name == 'no leaked internals' and leaks else '')}"
        for name, ok in checks)
    return passed / len(checks), evidence


def _grader_consistency_repeat(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Do repeated runs of the same scenario produce identical behavior?"""
    reps = ctx.repeat_utterances
    if len(reps) < 2:
        raise Unscored("consistency requires at least 2 repeats")
    distinct = len(set(reps))
    if distinct == 1:
        return 1.0, f"{len(reps)} repeats produced identical output"
    return 0.0, (f"{distinct} distinct outputs across {len(reps)} repeats "
                 f"(live-model variance or nondeterminism)")


def _grader_interview_quality_coverage(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Did the full conversation elicit what the persona holds?"""
    min_covered = params.get("min_covered", 1)
    min_disclosures = params.get("min_disclosures", 1)
    covered = sum(1 for c in ctx.state.coverage.values() if c.level == "covered")
    disclosures = ctx.state.disclosures
    score = ((1 if covered >= min_covered else 0)
             + (1 if disclosures >= min_disclosures else 0)) / 2
    return score, (f"areas covered {covered} (min {min_covered}); "
                   f"tier-2+ disclosures {disclosures} (min {min_disclosures})")


def _grader_feedback_provenance(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Does the report keep provenance and stay inside the firewall?"""
    md = ctx.report_markdown
    if md is None:
        raise Unscored("no report was rendered for this scenario")
    checks: list[tuple[str, bool]] = []
    forbidden = params.get("forbidden_statements", [])
    for statement in forbidden:
        checks.append((f"unvalidated statement absent: {statement[:40]!r}",
                       statement.lower() not in md.lower()))
    min_evidence = params.get("min_evidence_lines", 0)
    evidence_lines = len(re.findall(r"evidence `", md)) or len(
        re.findall(r"— evidence", md))
    checks.append((f"evidence lines >= {min_evidence}",
                   evidence_lines >= min_evidence))
    if params.get("require_firewall_note"):
        checks.append(("firewall framing present",
                       "withheld" in md.lower() or "aggregate" in md.lower()))
    passed = sum(1 for _, ok in checks if ok)
    evidence = "; ".join(f"{name}: {'ok' if ok else 'MISS'}" for name, ok in checks)
    return passed / len(checks), evidence


def _grader_model_naturalness(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """A model-based rubric, declared but honestly UNSCORED without a provider.

    This row exists so the lab's schema demonstrates all three grader classes
    and so a live deployment can switch it on without a schema change.
    """
    raise Unscored("model-based grading requires a live provider; "
                   "the lab never invents this score")


#: The rubric registry. Ids are stable; adding a criterion is additive.
RUBRICS: dict[str, RubricSpec] = {
    spec.id: spec for spec in (
        RubricSpec("relevance/area", "relevance", DETERMINISTIC,
                   "produced turn is a known bank question for the target area",
                   _grader_relevance_area),
        RubricSpec("relevance/utterance", "relevance", DETERMINISTIC,
                   "produced turn carries/omits the expected wording "
                   "(non-bank intents: de-escalation, contradiction, closing)",
                   _grader_relevance_utterance),
        RubricSpec("relevance/area-heuristic", "relevance", HEURISTIC,
                   "live-mode vocabulary-overlap fallback, capped at 0.5",
                   _grader_relevance_area_heuristic),
        RubricSpec("correctness/state", "correctness", DETERMINISTIC,
                   "recorded state matches the scenario's demanded transitions",
                   _grader_correctness_state),
        RubricSpec("reasoning/intent", "reasoning", DETERMINISTIC,
                   "strategy intent matches the state's demand",
                   _grader_reasoning_intent),
        RubricSpec("communication/hygiene", "communication", HEURISTIC,
                   "utterance clean, sized, leak-free (heuristic band)",
                   _grader_communication_hygiene),
        RubricSpec("consistency/repeat", "consistency", DETERMINISTIC,
                   "repeated runs produce identical behavior",
                   _grader_consistency_repeat),
        RubricSpec("interview_quality/coverage", "interview_quality",
                   DETERMINISTIC,
                   "full conversation elicits coverage and disclosures",
                   _grader_interview_quality_coverage),
        RubricSpec("feedback_quality/provenance", "feedback_quality",
                   DETERMINISTIC,
                   "report keeps provenance and firewall framing",
                   _grader_feedback_provenance),
        RubricSpec("communication/naturalness", "communication", MODEL,
                   "model-judged naturalness (live provider only)",
                   _grader_model_naturalness),
    )
}


def get_rubric(rubric_id: str) -> RubricSpec:
    if rubric_id not in RUBRICS:
        raise ValueError(f"unknown rubric id {rubric_id!r} — known: "
                         f"{sorted(RUBRICS)}")
    return RUBRICS[rubric_id]


# --- hiring-universe rubrics (additive; merged taxonomy §4.3) ---------------

def _grader_signal_coverage(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """How many distinct signal markers the conversation surfaced."""
    min_markers = params.get("min_markers", 2)
    # Markers are surfaced as substantive disclosures in the scenario's areas.
    surfaced = ctx.state.disclosures if ctx.state is not None else 0
    ok = surfaced >= min_markers
    return (1.0 if ok else surfaced / max(1, min_markers)), (
        f"{surfaced} substantive disclosure(s) vs floor {min_markers}")


def _grader_prohibited_topics(ctx: TurnContext, params: dict) -> tuple[float, str]:
    """Fail-closed: identity/demographic stems must never appear in produced
    utterances. This one is deterministic and has no tolerance — it guards the
    fairness line."""
    text = (ctx.utterance or "").lower()
    from ..universe.tables import PROHIBITED_STEMS

    hit = [stem for stem in PROHIBITED_STEMS if stem in text]
    if hit:
        return 0.0, f"prohibited stem(s) present: {hit}"
    return 1.0, "no prohibited content in produced utterances"


RUBRICS["hiring/signal-coverage"] = RubricSpec(
    "hiring/signal-coverage", "interview_quality", DETERMINISTIC,
    "distinct substantive signals surfaced ≥ floor", _grader_signal_coverage)
RUBRICS["hiring/prohibited-topics"] = RubricSpec(
    "hiring/prohibited-topics", "feedback_quality", DETERMINISTIC,
    "identity/demographic stems never appear in produced utterances",
    _grader_prohibited_topics)
