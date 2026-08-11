"""The interview strategy: decide what to do next, from signals already collected.

The engine has always *assessed* each answer — tier reached, specificity, candor
signal — and then thrown that away and asked the next scripted question. This module
makes it act on what it knows:

  * **Candor adaptation.** A guarded answer means back off: drop to a safer area and
    return later. Marching on after someone declines is how an interview loses a person
    for the rest of the session.
  * **Specificity conversion.** A vague answer is not an answer. Stay on the topic and
    ask for the last concrete instance — the difference between "things get delayed"
    and a finding you can act on.
  * **Self-contradiction surfacing.** When an answer conflicts with something the same
    person said earlier, ask about it. Within one interview a contradiction is usually
    a clarification waiting to happen, not a lie.
  * **Value-of-information selection.** Choose the next area by what is still unknown,
    not by a fixed order: untouched areas first, then shallow ones, skipping areas that
    are exhausted or deferred.

The policy is deliberately explicit and testable rather than left implicit in a prompt.
With a live model the chosen move is passed to it as a directive; offline it selects
from a question bank. Both paths run the same decision, so the strategy can be measured
by the existing eval harness instead of being taken on faith.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .state import (
    COVERAGE_TIER,
    MAX_VAGUE_STREAK,
    InterviewState,
    TARGET_AREAS,
)

# Areas ordered by how much commercially useful truth they tend to hold. Used only to
# break ties — coverage need dominates.
_AREA_VALUE = {
    "friction": 5, "workarounds": 4, "wasted_effort": 4,
    "bottlenecks": 3, "ai_opportunity": 3, "process_reality": 1,
}

# The highest tier worth targeting in an area, given what it can plausibly yield.
_AREA_TIER_CEILING = {
    "process_reality": 1, "workarounds": 2, "bottlenecks": 2,
    "wasted_effort": 2, "ai_opportunity": 2, "friction": 4,
}


class Intent(str, Enum):
    OPEN = "open"                                  # first question, establish safety
    LADDER = "ladder"                              # push a step deeper
    CONVERT_SPECIFICITY = "specificity_conversion"  # vague -> concrete instance
    DE_ESCALATE = "de_escalate"                    # guarded -> back off, come back
    SURFACE_CONTRADICTION = "contradiction"        # conflicts with their own earlier answer
    CLOSE = "close"


@dataclass(frozen=True)
class Move:
    intent: Intent
    target_area: str
    target_tier: int
    rationale: str
    #: For SURFACE_CONTRADICTION: the two things the subject said.
    earlier: str = ""
    later: str = ""

    @property
    def technique(self) -> str:
        return self.intent.value


def _information_gain(area: str, state: InterviewState) -> float:
    """How much is still to be learned in this area. Higher is more worth asking."""
    cov = state.coverage[area]
    ceiling = _AREA_TIER_CEILING.get(area, 2)
    remaining = max(0, ceiling - max(cov.max_tier, 0))

    if cov.level == "untouched":
        gain = 3.0                      # never asked: the most uncertain thing we have
    elif cov.max_tier < COVERAGE_TIER:
        gain = 2.0                      # touched but shallow: still below usable depth
    else:
        gain = 0.6 * remaining          # covered: only worth pushing toward its ceiling

    # An area the subject was guarded about is worth less *right now*, not forever.
    if cov.deferred_until_turn > state.turn_count:
        gain *= 0.15
    # Diminishing returns on an area that keeps producing vagueness.
    if cov.vague_streak >= MAX_VAGUE_STREAK:
        gain *= 0.2
    return gain + _AREA_VALUE.get(area, 1) * 0.05


def _best_area(state: InterviewState, exclude: str | None = None) -> tuple[str, float]:
    candidates = [a for a in TARGET_AREAS if a != exclude] or list(TARGET_AREAS)
    scored = sorted(candidates, key=lambda a: (-_information_gain(a, state), a))
    best = scored[0]
    return best, _information_gain(best, state)


def _next_tier(area: str, state: InterviewState) -> int:
    cov = state.coverage[area]
    ceiling = _AREA_TIER_CEILING.get(area, 2)
    return max(1, min(ceiling, max(cov.max_tier, 0) + 1))


def _find_contradiction(state: InterviewState) -> tuple[str, str] | None:
    """A conflict between the latest answer and an earlier one by the same person.

    Reuses the aggregation relation checker rather than growing a second notion of
    what a contradiction is.
    """
    answers = [r.answer for r in state.history if r.answer]
    if len(answers) < 2:
        return None
    try:
        from ..aggregation.model import Relation
        from ..aggregation.relation import make_relation_checker
    except ImportError:  # pragma: no cover
        return None
    checker = make_relation_checker(None)  # heuristic: no model call inside a turn
    latest = answers[-1]
    for earlier in reversed(answers[:-1]):
        if checker.classify(earlier, latest) is Relation.CONFLICT:
            return earlier, latest
    return None


class InterviewStrategy:
    """Chooses the next move. Pure: state in, decision out."""

    def __init__(self, *, max_turns: int = 14, surface_contradictions: bool = True) -> None:
        self._max_turns = max_turns
        self._surface_contradictions = surface_contradictions
        self._contradictions_raised = 0
        self._last_intent: Intent | None = None

    def _remember(self, move: Move) -> Move:
        self._last_intent = move.intent
        return move

    def decide(self, state: InterviewState) -> Move:
        # 1. Opening: establish what the work is before asking anything costly.
        if state.turn_count == 0:
            return self._remember(Move(
                Intent.OPEN, "process_reality", 1,
                "opening: establish the work and the confidentiality frame"))

        last = state.history[-1] if state.history else None
        budget_left = self._max_turns - state.turn_count

        # 2. Out of budget, or nothing left worth asking.
        best_area, best_gain = _best_area(state)
        if budget_left <= 0 or best_gain < 0.25:
            return self._remember(Move(Intent.CLOSE, best_area, 0,
                                       "coverage saturated or budget exhausted"))

        if last is not None:
            # 3. An actual refusal: back off, move somewhere safer, return later.
            #    Never twice running — a second soothing question in a row stops being
            #    reassurance and becomes an interview that has given up.
            if (last.candor_signal == "guarded"
                    and self._last_intent is not Intent.DE_ESCALATE):
                safer, _ = _best_area(state, exclude=last.area)
                return self._remember(Move(
                    Intent.DE_ESCALATE, safer, 1,
                    f"subject declined on {last.area}: moving to a lower-cost topic "
                    f"and returning later"))

            # 4. Vague but not a refusal: stay put and ask for a concrete instance.
            cov = state.coverage.get(last.area)
            if (last.specificity != "concrete"
                    and self._last_intent is not Intent.CONVERT_SPECIFICITY
                    and cov is not None and cov.vague_streak < MAX_VAGUE_STREAK
                    and budget_left > 1):
                return self._remember(Move(
                    Intent.CONVERT_SPECIFICITY, last.area,
                    max(1, last.tier_targeted),
                    "answer was vague: ask for the last concrete instance"))

            # 5. Contradicts something they said earlier: ask about it.
            if self._surface_contradictions and self._contradictions_raised < 2:
                found = _find_contradiction(state)
                if found is not None:
                    self._contradictions_raised += 1
                    return self._remember(Move(
                        Intent.SURFACE_CONTRADICTION, last.area,
                        max(1, last.tier_reached),
                        "conflicts with an earlier answer from the same person",
                        earlier=found[0], later=found[1]))

        # 6. Otherwise: go where the most is still unknown, one tier deeper.
        return self._remember(Move(
            Intent.LADDER, best_area, _next_tier(best_area, state),
            f"highest remaining uncertainty is {best_area}"))
