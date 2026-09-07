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


def _information_gain(area: str, state: InterviewState, *,
                      ceiling: int | None = None,
                      value: float | None = None) -> float:
    """How much is still to be learned in this area. Higher is more worth asking."""
    cov = state.coverage[area]
    ceiling = _AREA_TIER_CEILING.get(area, 2) if ceiling is None else ceiling
    value = _AREA_VALUE.get(area, 1) if value is None else value
    remaining = max(0, ceiling - max(cov.max_tier, 0))
    # "Usable depth" is capped by what the area can plausibly yield: an area whose
    # ceiling is below COVERAGE_TIER can never be *covered*, and reading "below
    # coverage tier" without that cap gave it gain 2.0 forever — the strategy then
    # ladder-ed into it until the turn budget died, asking the identical question
    # on the last three turns of a simulated interview.
    usable_ceiling = min(ceiling, COVERAGE_TIER)

    if cov.level == "untouched":
        gain = 3.0                      # never asked: the most uncertain thing we have
    elif cov.max_tier < usable_ceiling:
        gain = 2.0                      # touched but shallow: still below usable depth
    else:
        gain = 0.6 * remaining          # as deep as it can usefully go: only the ceiling beyond

    # An area the subject was guarded about is worth less *right now*, not forever.
    if cov.deferred_until_turn > state.turn_count:
        gain *= 0.15
    # Diminishing returns on an area that keeps producing vagueness.
    if cov.vague_streak >= MAX_VAGUE_STREAK:
        gain *= 0.2
    return gain + value * 0.05


def _best_area(state: InterviewState, exclude: str | None = None,
               candidates: tuple[str, ...] | list[str] | None = None,
               *, gain=None) -> tuple[str, float]:
    gain = gain or _information_gain
    pool = list(candidates) if candidates is not None else list(TARGET_AREAS)
    pool = [a for a in pool if a != exclude] or list(TARGET_AREAS)
    scored = sorted(pool, key=lambda a: (-gain(state, a), a))
    best = scored[0]
    return best, gain(state, best)


def _next_tier(area: str, state: InterviewState, *,
               ceiling: int | None = None) -> int:
    cov = state.coverage[area]
    ceiling = _AREA_TIER_CEILING.get(area, 2) if ceiling is None else ceiling
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

    def __init__(self, *, max_turns: int = 14, surface_contradictions: bool = True,
                 areas: tuple | None = None, area_params: dict | None = None,
                 rules: list | None = None) -> None:
        self._max_turns = max_turns
        self._surface_contradictions = surface_contradictions
        self._contradictions_raised = 0
        self._last_intent: Intent | None = None
        # Universe seam S2: composed scenarios inject their own areas, per-area
        # {value, ceiling} params, and follow-up rules. None keeps the discovery
        # defaults, so every existing caller behaves exactly as before.
        self._areas = tuple(areas) if areas else TARGET_AREAS
        self._area_params = dict(area_params or {})
        self._rules = sorted(rules or [], key=lambda r: r.get("priority", 10))
        self._rule_fires: dict[str, int] = {}
        self._consumed: set[tuple] = set()
        # Areas that already had their specificity conversion: one conversion
        # per area per interview — asking the same probe twice is a repeat,
        # and a second vague answer after a converted probe means strikeout.
        self._converted: set[str] = set()

    def _remember(self, move: Move) -> Move:
        self._last_intent = move.intent
        return move

    # -- universe seam S2 helpers (injected tables; defaults unchanged) ------
    def _params(self, area: str) -> dict:
        return self._area_params.get(area, {})

    def _gain(self, state: InterviewState, area: str) -> float:
        p = self._params(area)
        return _information_gain(area, state, ceiling=p.get("ceiling"),
                                 value=p.get("value"))

    def _best(self, state: InterviewState, exclude: str | None = None,
              candidates: list[str] | None = None) -> tuple[str, float]:
        pool = candidates if candidates is not None else list(self._areas)
        return _best_area(state, exclude, candidates=pool, gain=self._gain)

    def _next_tier_for(self, area: str, state: InterviewState) -> int:
        return _next_tier(area, state, ceiling=self._params(area).get("ceiling"))

    @property
    def _first_area(self) -> str:
        return self._areas[0]

    def _rule_pass(self, state: InterviewState,
                   last) -> "Move | None":
        """Composed follow-up rules (universe seam S2).

        ``if the candidate shows signal X, probe deeper; if red flag Y appears,
        demand evidence`` as data: each rule fires at most ``max_fires`` times,
        each (rule, answer) pair is consumed once, and every action compiles to
        an existing Move so the loop, event log, and resume are unchanged.
        No rules -> no-op (the discovery default).
        """
        if not self._rules or last is None:
            return None
        for rule in self._rules:
            rid = rule.get("id", "rule")
            if self._rule_fires.get(rid, 0) >= rule.get("max_fires", 1):
                continue
            key = (rid, last.turn)
            if key in self._consumed:
                continue
            trigger = rule.get("trigger", {})
            kind = trigger.get("kind")
            if kind == "marker_fired":
                low = (last.answer or "").lower()
                if not any(stem.lower() in low
                           for stem in trigger.get("stems", [])):
                    continue
            elif kind == "coverage_gap":
                if state.turn_count < trigger.get("after_turn", 0):
                    continue
                if all(state.coverage[a].level == "covered"
                       for a in self._areas):
                    continue
            else:
                continue
            action = rule.get("action", {})
            if action.get("kind") == "probe":
                area = action.get("area", last.area)
                self._rule_fires[rid] = self._rule_fires.get(rid, 0) + 1
                self._consumed.add(key)
                return self._remember(Move(
                    Intent.CONVERT_SPECIFICITY, area,
                    max(1, last.tier_targeted),
                    f"scenario rule {rid} (evidence probe): "
                    f"{rule.get('rationale', '')}"))
            if action.get("kind") == "intent":
                intent = Intent(action["intent"])
                area = action.get("area", last.area)
                tier = max(1, int(action.get("tier", 1)))
                self._rule_fires[rid] = self._rule_fires.get(rid, 0) + 1
                self._consumed.add(key)
                return self._remember(Move(
                    intent, area, tier,
                    f"scenario rule {rid}: {rule.get('rationale', '')}"))
        return None

    def decide(self, state: InterviewState) -> Move:
        # 1. Opening: establish what the work is before asking anything costly.
        # The opening targets the scenario's FIRST area (universe seam S2);
        # the discovery default is process_reality.
        if state.turn_count == 0:
            first = self._areas[0]
            return self._remember(Move(
                Intent.OPEN, first, 1,
                "opening: establish the work and the confidentiality frame"))

        last = state.history[-1] if state.history else None
        budget_left = self._max_turns - state.turn_count

        # 1.5. Scenario follow-up rules (universe seam S2) run before the
        # discovery defaults: composed logic overrides the built-in ladder.
        rule_move = self._rule_pass(state, last)
        if rule_move is not None:
            return rule_move

        # 2. Out of budget, or nothing left worth asking.
        best_area, best_gain = self._best(state)
        if budget_left <= 0 or best_gain < 0.25:
            return self._remember(Move(Intent.CLOSE, best_area, 0,
                                       "coverage saturated or budget exhausted"))

        if last is not None:
            # 3. An actual refusal: back off, move somewhere safer, return later.
            #    Never twice running — a second soothing question in a row stops being
            #    reassurance and becomes an interview that has given up.
            if (last.candor_signal == "guarded"
                    and self._last_intent is not Intent.DE_ESCALATE):
                safer, _ = self._best(state, exclude=last.area)
                return self._remember(Move(
                    Intent.DE_ESCALATE, safer, 1,
                    f"subject declined on {last.area}: moving to a lower-cost topic "
                    f"and returning later"))

            # 4. Vague but not a refusal: stay put and ask for a concrete instance.
            cov = state.coverage.get(last.area)
            if (last.specificity != "concrete"
                    and self._last_intent is not Intent.CONVERT_SPECIFICITY
                    and last.area not in self._converted
                    and cov is not None and cov.vague_streak < MAX_VAGUE_STREAK
                    and budget_left > 1):
                self._converted.add(last.area)
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

        # 6. Otherwise: go where the most is still unknown, one tier deeper — but
        # only where there is something left to get. An area whose vague streak has
        # maxed out is struck out ("three strikes and it is not worth more",
        # state.py), and one already at its tier ceiling has no deeper tier to
        # offer; ladder-ing into either re-asked the identical question until the
        # budget died. Better to close than to grind.
        askable = [a for a in self._areas
                   if state.coverage[a].vague_streak < MAX_VAGUE_STREAK
                   and state.coverage[a].max_tier
                   < self._params(a).get("ceiling", _AREA_TIER_CEILING.get(a, 2))]
        if askable:
            area, gain = self._best(state, candidates=askable)
            if gain >= 0.25:
                return self._remember(Move(
                    Intent.LADDER, area, self._next_tier_for(area, state),
                    f"highest remaining uncertainty is {area}"))
        return self._remember(Move(
            Intent.CLOSE, best_area, 0,
            "coverage saturated, budget exhausted, or only struck-out areas remain"))
