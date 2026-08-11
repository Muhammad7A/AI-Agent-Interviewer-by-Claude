"""Two-layer scoring against known ground truth."""
from __future__ import annotations

from dataclasses import dataclass

from ..evidence.model import Claim
from ..subjects.simulated import LatentTruth, _CANDOR_TIER_CAP
from ..transcript.model import Speaker, Transcript
from .matching import assign_findings_to_truths, truth_in_texts


@dataclass
class CaseMetrics:
    persona: str
    candor: str
    is_ceiling: bool

    # ground-truth sizes
    achievable: int          # latent truths reachable given the candor cap
    elicited: int            # achievable truths that reached the transcript
    claims: int              # grounded claim proposals produced
    matched_claims: int      # claims that map to a real latent truth
    captured: int            # distinct truths captured by a claim
    tier2plus_claims: int    # claims at Tier 2+ (the commercially valuable ones)

    # safety
    confabulation_rate: float  # ungrounded proposals / total (mechanical, F4)
    candor_leak: int           # truths ABOVE the candor cap that leaked (must be 0)

    @property
    def elicitation_recall(self) -> float:
        return self.elicited / self.achievable if self.achievable else 1.0

    @property
    def synthesis_recall(self) -> float:
        return self.captured / self.elicited if self.elicited else 1.0

    @property
    def e2e_recall(self) -> float:
        return self.captured / self.achievable if self.achievable else 1.0

    @property
    def precision(self) -> float:
        # Of the claims produced, how many are real truths (not over-claims)?
        return self.matched_claims / self.claims if self.claims else 1.0

    @property
    def value_density(self) -> float:
        # Of the claims produced, how many carry Tier-2+ value (not Tier 0-1 filler)?
        return self.tier2plus_claims / self.claims if self.claims else 0.0


def score_case(
    *,
    persona: str,
    candor: str,
    is_ceiling: bool,
    gold: list[LatentTruth],
    transcript: Transcript,
    claims: list[Claim],
    confabulation_rate: float,
) -> CaseMetrics:
    cap = _CANDOR_TIER_CAP.get(candor, 3)
    achievable = [t for t in gold if t.tier <= cap]
    above_cap = [t for t in gold if t.tier > cap]

    subject_texts = [s.text for s in transcript.segments if s.speaker is Speaker.SUBJECT]
    elicited = [t for t in achievable if truth_in_texts(t, subject_texts)]
    # A truth above the candor cap should never appear — that would be a candor
    # breach in the simulator (or the persona), not a win.
    leak = [t for t in above_cap if truth_in_texts(t, subject_texts)]

    finding_texts = [
        f"{c.statement} {c.evidence[0].resolve(transcript)}" for c in claims
    ]
    captured_ids, matched_idx = assign_findings_to_truths(finding_texts, gold)

    return CaseMetrics(
        persona=persona,
        candor=candor,
        is_ceiling=is_ceiling,
        achievable=len(achievable),
        elicited=len(elicited),
        claims=len(claims),
        matched_claims=len(matched_idx),
        captured=len(captured_ids),
        tier2plus_claims=sum(1 for c in claims if c.tier >= 2),
        confabulation_rate=confabulation_rate,
        candor_leak=len(leak),
    )
