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

    # 1. Independent corroboration: this member plus everyone who AGREES with them.
    agreeing = {finding.members[k].participant_id for k in finding.agreeing_with(index)}
    agreeing.discard(member.participant_id)
    effective = 1 + len(agreeing)
    corr_delta = CORROBORATION_W * math.log(effective)
    contributions.append(SignalContribution(
        "corroboration",
        f"{effective} independent participant(s) assert this"
        + (f" ({', '.join(sorted(agreeing))} agree)" if agreeing else " (single source)"),
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
