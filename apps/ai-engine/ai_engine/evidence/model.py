"""Claim proposals and the grounding report.

A :class:`Claim` is a *proposal* about organizational truth, bound to the exact
transcript span(s) that justify it. The evidence-first invariant (C1/C5) is
enforced in the constructor: a claim cannot be built without at least one piece
of grounded evidence. There is deliberately **no confidence score** at this
stage — truth is not confidence (C2), and a claim carries only its grounding
status until a validation gate earns it more (research program: do not promote a
claim above its evidence).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..transcript.model import EvidenceRef, Speaker, Transcript


class EvidenceError(ValueError):
    """Raised when a claim would exist without resolving evidence."""


class ClaimType(str, Enum):
    OBSERVATION = "observation"
    WORKAROUND = "workaround"
    BOTTLENECK = "bottleneck"
    FRICTION = "friction"
    WASTED_EFFORT = "wasted_effort"
    AI_OPPORTUNITY = "ai_opportunity"

    @classmethod
    def coerce(cls, value: str) -> "ClaimType":
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            return cls.OBSERVATION


class ClaimStatus(str, Enum):
    # A claim is only ever *proposed* here. Validation is a separate gate owned
    # by the domain / a consultant (C3). The type makes that impossible to skip.
    PROPOSED = "proposed"


@dataclass(frozen=True)
class GroundedEvidence:
    """An EvidenceRef plus how it was matched — the audit trail of a tag."""

    ref: EvidenceRef
    quote: str          # the quote the tagger proposed
    match_kind: str     # "exact" | "flexible"

    def resolve(self, transcript: Transcript) -> str:
        """The actual immutable source text this evidence points at."""
        return self.ref.resolve(transcript)


@dataclass(frozen=True)
class Claim:
    id: str
    claim_type: ClaimType
    statement: str
    evidence: tuple[GroundedEvidence, ...]
    speaker: Speaker
    tier: int
    status: ClaimStatus = ClaimStatus.PROPOSED

    def __post_init__(self) -> None:
        if not self.evidence:
            raise EvidenceError(
                f"Claim {self.id!r} has no grounded evidence; a claim without "
                f"provenance is forbidden (C1/C5)."
            )


@dataclass
class RawProposal:
    """What the tagger (model or mock) emits *before* grounding verification."""

    claim_type: str
    statement: str
    quote: str
    tier: int = 0
    segment_hint: str | None = None


@dataclass
class RejectedProposal:
    proposal: RawProposal
    reason: str  # "quote_not_found" | "empty_quote" | "cited_interviewer_not_subject"


@dataclass
class GroundingReport:
    total: int
    grounded: int
    rejected: list[RejectedProposal] = field(default_factory=list)

    @property
    def ungrounded(self) -> int:
        return len(self.rejected)

    @property
    def confabulation_rate(self) -> float:
        """Fraction of proposals whose evidence did not resolve. The F4 metric."""
        return (self.ungrounded / self.total) if self.total else 0.0


@dataclass
class TaggingResult:
    claims: list[Claim]
    report: GroundingReport
