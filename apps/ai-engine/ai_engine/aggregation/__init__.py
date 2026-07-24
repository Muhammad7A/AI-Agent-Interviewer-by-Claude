"""Multi-interview aggregation with contradiction detection.

The step from a single-interview tool to organizational intelligence: fuse the
findings of many interviews of the SAME organization into an org-level picture.

  * Where independent people say the same thing -> corroboration (raises confidence).
  * Where they disagree -> a contradiction, typed as conflict / variation /
    complementarity (research program Q7/Q8).

Provenance is preserved across interviews: every aggregated finding still traces
to each participant's own immutable transcript segment (C1/C5). Aggregation never
invents a fact — it only relates findings that already carry their own evidence.
"""

from .model import (
    AggregatedFinding,
    AggregationResult,
    Contradiction,
    ParticipantFinding,
    Relation,
    participant_finding_from_claim,
)
from .aggregator import aggregate
from .relation import (
    HeuristicRelationChecker,
    LlmRelationChecker,
    make_relation_checker,
)

__all__ = [
    "AggregatedFinding",
    "AggregationResult",
    "Contradiction",
    "HeuristicRelationChecker",
    "LlmRelationChecker",
    "ParticipantFinding",
    "Relation",
    "aggregate",
    "make_relation_checker",
    "participant_finding_from_claim",
]
