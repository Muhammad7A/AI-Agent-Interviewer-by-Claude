"""The consultant validation gate — where AI proposals become validated truth.

This closes the loop the whole system turns on (C3/C4): the AI *proposes* claims;
a human *validates* them. A validation decision is a first-class, recorded event
carrying the validator's identity and the evidence they reviewed — never a silent
checkbox. It is also the supervised label the learning loop compounds on
(research program Q6), so it is written to its own dataset layer, never fused
with testimony or interpretation (C7).
"""

from .model import (
    Correction,
    ValidatedFinding,
    ValidationDecision,
    ValidationError,
    Validator,
    Verdict,
)
from .gate import AutoValidator, ValidationGate, validate_claims

__all__ = [
    "AutoValidator",
    "Correction",
    "ValidatedFinding",
    "ValidationDecision",
    "ValidationError",
    "ValidationGate",
    "Validator",
    "Verdict",
    "validate_claims",
]
