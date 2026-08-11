"""The interviewer's running belief/coverage state.

Kept deliberately small for the thin slice: a set of target areas we want the
interview to reach, each tracked by how deeply it was reached (the *tier* — the
cost/sensitivity of the truth disclosed). Value density lives in Tiers 2-4, so
the state's job is to notice whether we are actually getting there or circling in
Tier 0-1 small talk.
"""
from __future__ import annotations

from dataclasses import dataclass, field

# The discovery targets for an organizational interview. These are the areas a
# consultant needs covered to produce a decision-grade assessment.
TARGET_AREAS: tuple[str, ...] = (
    "process_reality",   # how work actually happens vs the mandated process
    "workarounds",       # shadow IT, private tools, bypasses (Tier 2)
    "bottlenecks",       # where work stalls, waits, or piles up at handoffs
    "friction",          # managerial / process / political friction (Tier 3)
    "wasted_effort",     # redundant / low-value / duplicated work (Tier 2-3)
    "ai_opportunity",    # repetitive, rules-based, high-volume tasks (signals)
)

# Tier names — the cost/sensitivity ladder. Candor is only meaningful at 2+.
TIER_NAMES: dict[int, str] = {
    0: "neutral-fact",
    1: "process-reality",
    2: "inefficiency/workaround",
    3: "managerial/political",
    4: "self-implicating",
}

# An area counts as "covered" once we've reached at least this tier in it.
COVERAGE_TIER = 2

# How long to leave a topic alone after the subject was guarded about it.
DEFER_TURNS = 2

# Stop pushing an area after this many consecutive vague answers.
MAX_VAGUE_STREAK = 2


@dataclass
class AreaCoverage:
    level: str = "untouched"  # untouched | touched | covered
    max_tier: int = -1
    #: Turns since this area was last asked about. Used to come back to a topic the
    #: subject was guarded about, rather than abandoning it.
    last_asked_turn: int = -1
    #: Set when the subject was guarded here, so the strategy backs off and returns.
    deferred_until_turn: int = -1
    #: Consecutive vague answers in this area — three strikes and it is not worth more.
    vague_streak: int = 0


@dataclass
class TurnRecord:
    """What happened on one exchange, so the strategy can reason over the interview.

    Without this the engine collects assessments and immediately forgets them — it can
    know an answer was vague or guarded and still march on to the next scripted
    question, which is precisely the behaviour that loses candour.
    """

    turn: int
    area: str
    tier_targeted: int
    tier_reached: int
    specificity: str
    candor_signal: str
    answer: str = ""


@dataclass
class InterviewState:
    objective: str
    coverage: dict[str, AreaCoverage] = field(
        default_factory=lambda: {a: AreaCoverage() for a in TARGET_AREAS}
    )
    turn_count: int = 0
    disclosures: int = 0  # count of substantive Tier 2+ disclosures
    history: list[TurnRecord] = field(default_factory=list)
    #: The area the last question aimed at, so its answer can be attributed.
    pending_area: str | None = None
    pending_tier: int = 0

    def record_answer(
        self,
        *,
        areas_touched: list[str],
        tier_reached: int,
        got_disclosure: bool,
        specificity: str = "none",
        candor_signal: str = "neutral",
        answer: str = "",
    ) -> None:
        """Fold an assessment of the subject's last answer into coverage."""
        for area in areas_touched:
            cov = self.coverage.get(area)
            if cov is None:
                continue
            cov.max_tier = max(cov.max_tier, tier_reached)
            if cov.max_tier >= COVERAGE_TIER:
                cov.level = "covered"
            elif cov.level == "untouched":
                cov.level = "touched"
        if got_disclosure and tier_reached >= COVERAGE_TIER:
            self.disclosures += 1

        area = (areas_touched[0] if areas_touched else self.pending_area) or ""
        cov = self.coverage.get(area)
        if cov is not None:
            if specificity == "concrete":
                cov.vague_streak = 0
            else:
                cov.vague_streak += 1
            if candor_signal == "guarded":
                # Back off this area and come back to it, rather than pressing.
                cov.deferred_until_turn = self.turn_count + DEFER_TURNS
        self.history.append(TurnRecord(
            turn=self.turn_count,
            area=area,
            tier_targeted=self.pending_tier,
            tier_reached=tier_reached,
            specificity=specificity,
            candor_signal=candor_signal,
            answer=answer,
        ))

    def note_question(self, area: str, tier: int) -> None:
        """Remember what the question just asked was aiming at."""
        self.pending_area = area
        self.pending_tier = tier
        cov = self.coverage.get(area)
        if cov is not None:
            cov.last_asked_turn = self.turn_count

    def subject_answers(self) -> list[str]:
        return [r.answer for r in self.history if r.answer]

    def uncovered_areas(self) -> list[str]:
        return [a for a, c in self.coverage.items() if c.level != "covered"]

    def saturated(self) -> bool:
        return not self.uncovered_areas()

    def summary(self) -> dict:
        return {
            "objective": self.objective,
            "turns": self.turn_count,
            "disclosures_tier2plus": self.disclosures,
            "coverage": {
                a: {"level": c.level, "max_tier": c.max_tier}
                for a, c in self.coverage.items()
            },
            "areas_covered": sum(
                1 for c in self.coverage.values() if c.level == "covered"
            ),
            "areas_total": len(self.coverage),
        }
