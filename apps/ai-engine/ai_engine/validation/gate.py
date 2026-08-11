"""The validation gate: apply a human (or simulated) verdict to each claim.

The gate builds :class:`ValidationDecision`s (enforcing their invariants) and
emits a ``ClaimValidated`` event to the *validation* dataset layer. It is
decision-source agnostic: a real consultant (interactive), a programmatic caller,
or the :class:`AutoValidator` demo policy all flow through the same gate, so the
recorded label format is identical — which is what makes the validation layer a
clean supervised dataset (Q6).
"""
from __future__ import annotations

import uuid
from typing import Callable

from ..evidence.model import Claim
from ..persistence.event_log import EventLog, NullEventLog
from .model import (
    Correction,
    ValidatedFinding,
    ValidationDecision,
    Validator,
    Verdict,
)

# A decision function turns a claim into (verdict, reason, correction).
DecideFn = Callable[[Claim], "tuple[Verdict, str, Correction | None]"]


class ValidationGate:
    def __init__(self, validator: Validator, event_log: EventLog | None = None) -> None:
        self._validator = validator
        self._log = event_log or NullEventLog(layer="validation")

    def decide(
        self,
        claim: Claim,
        verdict: Verdict,
        reason: str = "",
        correction: Correction | None = None,
    ) -> ValidationDecision:
        # Reviewing a claim means reviewing the evidence attached to it (C4).
        reviewed = tuple(ev.ref for ev in claim.evidence)
        decision = ValidationDecision(
            id=f"val-{uuid.uuid4().hex[:12]}",
            claim_id=claim.id,
            verdict=verdict,
            validator=self._validator,
            reviewed_evidence=reviewed,
            reason=reason,
            correction=correction,
        )
        self._emit(claim, decision)
        return decision

    def _emit(self, claim: Claim, decision: ValidationDecision) -> None:
        correction = None
        if decision.correction is not None:
            correction = {
                "new_statement": decision.correction.new_statement,
                "new_type": decision.correction.new_type.value if decision.correction.new_type else None,
                "new_tier": decision.correction.new_tier,
            }
        self._log.emit(
            "ClaimValidated",
            claim_id=claim.id,
            verdict=decision.verdict.value,
            validator_id=decision.validator.id,
            validator_kind=decision.validator.kind,  # excludes auto-sim from real learning
            reason=decision.reason,
            correction=correction,
            reviewed_evidence=[
                {"segment_id": r.segment_id, "start": r.start, "end": r.end}
                for r in decision.reviewed_evidence
            ],
            # denormalized snapshot for readability + as the supervised example;
            # testimony is never copied in here (C7).
            claim_type=claim.claim_type.value,
            claim_tier=claim.tier,
            claim_statement=claim.statement,
            decided_at=decision.decided_at.isoformat(),
        )


def validate_claims(gate: ValidationGate, claims: list[Claim], decide: DecideFn) -> list[ValidatedFinding]:
    """Run every claim through ``decide`` and the gate; return the findings."""
    findings: list[ValidatedFinding] = []
    for claim in claims:
        verdict, reason, correction = decide(claim)
        decision = gate.decide(claim, verdict, reason, correction)
        findings.append(ValidatedFinding(claim=claim, decision=decision))
    return findings


class AutoValidator:
    """A DETERMINISTIC, SIMULATED reviewer for demos and tests — never a human.

    Its verdicts are labelled ``kind="auto-sim"`` so they are filterable out of any
    real learning signal. Policy: reject Tier 0-1 / bare observations as not
    decision-relevant; tighten the mock tagger's ``[type] ...`` statements via an
    amendment (demonstrating the correction path); accept the rest.
    """

    VALIDATOR = Validator(id="val-auto", display_name="Auto-Sim Reviewer", kind="auto-sim")

    def decide(self, claim: Claim) -> "tuple[Verdict, str, Correction | None]":
        if claim.tier < 2 or claim.claim_type.value == "observation":
            return Verdict.REJECTED, "Not decision-relevant (Tier 0-1 / bare observation).", None
        stmt = claim.statement
        if stmt.startswith("[") and "]" in stmt:
            cleaned = stmt.split("]", 1)[1].strip()
            if cleaned and cleaned != stmt:
                return (
                    Verdict.AMENDED,
                    "Tightened wording for the report.",
                    Correction(new_statement=cleaned),
                )
        return Verdict.ACCEPTED, "", None
