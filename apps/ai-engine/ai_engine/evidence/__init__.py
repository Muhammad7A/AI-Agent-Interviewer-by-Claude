"""Evidence tagging: turn immutable testimony into evidence-bound claim proposals.

Every claim that survives carries >=1 EvidenceRef that resolves to an exact
immutable transcript span (C1/C5). Ungrounded proposals are rejected by a
deterministic verifier, not trusted — this is the confabulation filter (F4).
Output is always a *proposal* (status = proposed); validation is a later gate
(C3, AI proposes / domain validates).
"""

from .model import (
    Claim,
    ClaimStatus,
    ClaimType,
    EvidenceError,
    GroundedEvidence,
    GroundingReport,
    RawProposal,
    TaggingResult,
)
from .grounding import ground_proposal, ground_proposals
from .entailment import (
    Entailment,
    EntailmentResult,
    HeuristicEntailmentChecker,
    LlmEntailmentChecker,
    apply_entailment,
    make_checker,
)
from .tagger import EvidenceTagger

__all__ = [
    "Claim",
    "ClaimStatus",
    "ClaimType",
    "Entailment",
    "EntailmentResult",
    "EvidenceError",
    "EvidenceTagger",
    "GroundedEvidence",
    "GroundingReport",
    "HeuristicEntailmentChecker",
    "LlmEntailmentChecker",
    "RawProposal",
    "TaggingResult",
    "apply_entailment",
    "ground_proposal",
    "ground_proposals",
    "make_checker",
]
