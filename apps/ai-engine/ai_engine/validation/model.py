"""Validation decisions and the validated-finding projection.

A :class:`ValidationDecision` records a human's judgment on one AI-proposed claim.
Its invariants encode C4 (human authority is real, not a rubber stamp):

  * You cannot decide without having reviewed the claim's evidence — a decision
    with no reviewed evidence is forbidden.
  * Rejecting or amending requires a reason (friction against rubber-stamping, F6).
  * Only an amendment may carry a correction; an accept/reject may not.

The claim itself stays immutable (it is a proposal). A correction is expressed as
a separate :class:`Correction` overlay, so the original proposal and the human's
change are both preserved — that difference is the richest learning signal.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from ..evidence.model import Claim, ClaimType
from ..transcript.model import EvidenceRef


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ValidationError(ValueError):
    """Raised when a validation decision violates an invariant."""


class Verdict(str, Enum):
    ACCEPTED = "accepted"   # true and decision-relevant as stated
    REJECTED = "rejected"   # not true / not supported / not useful
    AMENDED = "amended"     # true, but the statement/type/tier needed correction


@dataclass(frozen=True)
class Validator:
    id: str
    display_name: str
    # "consultant" is a real human authority. "auto-sim" is a simulated reviewer
    # for demos/tests and MUST be excluded from any real learning signal.
    kind: str = "consultant"


@dataclass(frozen=True)
class Correction:
    new_statement: str | None = None
    new_type: ClaimType | None = None
    new_tier: int | None = None

    def is_empty(self) -> bool:
        return self.new_statement is None and self.new_type is None and self.new_tier is None


@dataclass(frozen=True)
class ValidationDecision:
    id: str
    claim_id: str
    verdict: Verdict
    validator: Validator
    reviewed_evidence: tuple[EvidenceRef, ...]
    reason: str = ""
    correction: Correction | None = None
    decided_at: datetime = field(default_factory=_now)

    def __post_init__(self) -> None:
        if not self.reviewed_evidence:
            raise ValidationError(
                "A decision must reference the evidence that was reviewed "
                "(C4: evidence is presented before judgment)."
            )
        if self.verdict in (Verdict.REJECTED, Verdict.AMENDED) and not self.reason.strip():
            raise ValidationError(f"A {self.verdict.value} decision requires a reason.")
        if self.verdict is Verdict.AMENDED:
            if self.correction is None or self.correction.is_empty():
                raise ValidationError("An amendment must carry a non-empty correction.")
        elif self.correction is not None:
            raise ValidationError("Only an amendment may carry a correction.")


@dataclass(frozen=True)
class ValidatedFinding:
    """A claim joined to its decision. The report reads the *effective* values."""

    claim: Claim
    decision: ValidationDecision

    @property
    def verdict(self) -> Verdict:
        return self.decision.verdict

    @property
    def is_reportable(self) -> bool:
        # Only human-validated truth reaches the report; rejects are excluded.
        return self.verdict in (Verdict.ACCEPTED, Verdict.AMENDED)

    @property
    def statement(self) -> str:
        c = self.decision.correction
        if c is not None and c.new_statement:
            return c.new_statement
        return self.claim.statement

    @property
    def claim_type(self) -> ClaimType:
        c = self.decision.correction
        if c is not None and c.new_type is not None:
            return c.new_type
        return self.claim.claim_type

    @property
    def tier(self) -> int:
        c = self.decision.correction
        if c is not None and c.new_tier is not None:
            return c.new_tier
        return self.claim.tier
