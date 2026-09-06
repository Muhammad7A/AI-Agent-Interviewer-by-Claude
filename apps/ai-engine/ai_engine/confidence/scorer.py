"""Derive confidence from observable structural signals.

Evidence accumulates in **log-odds** space: we start from a prior and add a
documented weight per signal, then convert once to a probability. Log-odds is used
because independent pieces of evidence add there, and because every term stays
individually inspectable (each becomes a ``SignalContribution``).

The weights below are an explicit, debatable starting point — they are NOT tuned
to make numbers look good. Whether they are any use is decided by the calibration
study (``confidence/study.py``), which measures them against known ground truth.
If calibration is poor, that is a reportable result, not something to hide.
"""
from __future__ import annotations

import math

from ..aggregation.model import AggregatedFinding, ParticipantFinding
from .model import ConfidenceScore, SignalContribution

# A finding that already passed grounding AND entailment is slightly more likely
# true than not — but only slightly. Two mechanical gates are not human validation.
PRIOR_P = 0.55

# Independent agreement is the strongest honest signal we have. Diminishing:
# the 2nd voice teaches far more than the 5th.
CORROBORATION_W = 1.30

# A costly disclosure is less likely to be invented *by the subject* (people rarely
# fabricate self-implicating admissions). Small, deliberately.
TIER_BONUS = {0: 0.0, 1: 0.0, 2: 0.20, 3: 0.35, 4: 0.50}

# How exactly the quote matched the immutable source. Interpretive distance is a
# (small) risk signal, not a truth signal.
MATCH_BONUS = {"exact": 0.10, "normalized": 0.0, "flexible": -0.15}

# Direct contradiction by another participant. Strong: if two people flatly
# disagree, at most one of them is right.
CONFLICT_W = 1.60


# Each additional voice from a cohort already represented counts for this much of a
# fresh one. Two people on the same team who talk daily are not two independent
# observations of their team's process; they are closer to one and a bit.
SAME_COHORT_WEIGHT = 0.35

# The ceiling on effective voices when no cohort is known at all. Without structure
# there is no way to tell five independent departments from one talkative team, and
# the honest response to unmodeled correlation is to stop paying for scale: beyond
# this, extra agreement adds nothing to the score. Chosen to sit above the
# corroboration a small engagement can genuinely produce and below the point where
# log() would keep rewarding a single echo chamber.
UNKNOWN_COHORT_CAP = 4.0


def _effective_voices(finding, index: int, agreeing_ix) -> tuple[float, str]:
    """How many *independent* voices back this member, and why that number.

    Agreement was previously counted at face value: ``1 + len(agreeing)`` fed
    straight into ``log()``, so five people on one team scored exactly like five
    people in five departments. In organizational testimony that is the common
    case rather than the edge case — people attend the same meetings and repeat the
    same received wisdom — and it inflated confidence precisely where a consultant
    most needs it not to be inflated.

    Two regimes, because there are two honest answers:

    * **Cohorts known** — the first voice from each cohort counts fully, each
      further voice from a cohort already seen counts :data:`SAME_COHORT_WEIGHT`.
    * **Cohorts unknown** — no discount can be computed, so the total is capped at
      :data:`UNKNOWN_COHORT_CAP`. Unmodeled correlation argues for claiming less.
    """
    members = [finding.members[k] for k in agreeing_ix]
    if not any(m.participant_id == finding.members[index].participant_id for m in members):
        members = [finding.members[index]] + members

    if all(m.cohort is None for m in members):
        return min(float(len(members)), UNKNOWN_COHORT_CAP), (
            "cohorts unknown, so capped" if len(members) > UNKNOWN_COHORT_CAP
            else "cohorts unknown")

    seen: set[str] = set()
    total = 0.0
    for m in members:
        # An unknown cohort is treated as its own — it cannot be shown to be
        # correlated with anything, and assuming correlation would understate a
        # genuine outside voice.
        key = m.cohort if m.cohort is not None else f"~unknown:{m.participant_id}"
        total += 1.0 if key not in seen else SAME_COHORT_WEIGHT
        seen.add(key)
    return total, f"{len(seen)} distinct cohort(s)"


def _logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


PRIOR_LOGIT = _logit(PRIOR_P)


def score_member(finding: AggregatedFinding, index: int) -> ConfidenceScore:
    """Confidence for ONE participant's finding, in the context of its topic.

    Scored per-member rather than per-topic on purpose: in a contested topic the
    majority side and the lone dissenter do not deserve the same confidence.
    """
    member: ParticipantFinding = finding.members[index]
    contributions: list[SignalContribution] = [
        SignalContribution("prior", f"passed grounding + entailment (p={PRIOR_P})", PRIOR_LOGIT)
    ]

    # 1. Corroboration: this member plus everyone who AGREES with them — discounted
    #    for the fact that agreement inside an organization is rarely independent.
    agreeing_ix = finding.agreeing_with(index)
    agreeing = {finding.members[k].participant_id for k in agreeing_ix}
    agreeing.discard(member.participant_id)
    effective, basis = _effective_voices(finding, index, agreeing_ix)
    corr_delta = CORROBORATION_W * math.log(effective)
    contributions.append(SignalContribution(
        "corroboration",
        f"{effective:.2f} effective voice(s) assert this"
        + (f" ({', '.join(sorted(agreeing))} agree; {basis})" if agreeing
           else " (single source)"),
        corr_delta,
    ))

    # 2. Direct contradiction by other participants.
    conflicting = {finding.members[k].participant_id for k in finding.conflicting_with(index)}
    conflicting.discard(member.participant_id)
    if conflicting:
        # Being outnumbered is worse than being one voice among two. Scale the
        # penalty by how much of the disagreement is against this member.
        share = len(conflicting) / (len(conflicting) + len(agreeing) + 1)
        conflict_delta = -CONFLICT_W * share * math.log1p(len(conflicting)) / math.log(2)
        contributions.append(SignalContribution(
            "contradiction",
            f"contradicted by {', '.join(sorted(conflicting))}"
            + (" (minority view)" if len(conflicting) > len(agreeing) else " (contested)"),
            conflict_delta,
        ))

    # 3. Disclosure tier — costly admissions are less likely invented.
    tier_delta = TIER_BONUS.get(member.tier, 0.0)
    if tier_delta:
        contributions.append(SignalContribution(
            "disclosure_tier", f"tier {member.tier} (costly to disclose)", tier_delta))

    # 4. Evidence match exactness.
    match_delta = MATCH_BONUS.get(member.match_kind, 0.0)
    if match_delta:
        contributions.append(SignalContribution(
            "evidence_match", f"quote matched source: {member.match_kind}", match_delta))

    logit = sum(c.logit_delta for c in contributions)
    return ConfidenceScore(value=_sigmoid(logit), logit=logit, contributions=tuple(contributions))


def score_topic(finding: AggregatedFinding) -> list[ConfidenceScore]:
    """Confidence for every member of one topic."""
    return [score_member(finding, i) for i in range(len(finding.members))]


def score_all(findings: list[AggregatedFinding]) -> list[tuple[AggregatedFinding, int, ConfidenceScore]]:
    """Flat list of (topic, member index, score) across an aggregation."""
    out: list[tuple[AggregatedFinding, int, ConfidenceScore]] = []
    for finding in findings:
        for i, score in enumerate(score_topic(finding)):
            out.append((finding, i, score))
    return out
