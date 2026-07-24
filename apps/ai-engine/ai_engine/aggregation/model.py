"""The aggregation data model.

A :class:`ParticipantFinding` is one person's finding, carrying its own resolved
evidence and the address of the transcript segment it came from — so cross-
interview provenance survives aggregation. An :class:`AggregatedFinding` is a
topic several findings map to, with its corroboration count and any contradictions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from ..evidence.model import Claim
from ..transcript.model import Transcript

# The offline mock tagger prefixes statements with "[type] ". A real/validated
# finding would not; strip it so labels and contradictions read cleanly.
_TAG_PREFIX = re.compile(r"^\[[a-z_]+\]\s*")


def _clean(statement: str) -> str:
    return _TAG_PREFIX.sub("", statement).strip()


class Relation(str, Enum):
    AGREE = "agree"              # same claim, corroborating
    CONFLICT = "conflict"       # cannot both be true — investigate
    VARIATION = "variation"     # both true, differ by team/context
    COMPLEMENT = "complement"   # both true, additive (different parts)
    UNRELATED = "unrelated"     # not actually about the same thing


@dataclass(frozen=True)
class ParticipantFinding:
    participant_id: str
    participant_name: str
    claim_type: str
    statement: str
    tier: int
    evidence_quote: str   # resolved from the participant's immutable transcript
    segment_id: str
    transcript_id: str


def participant_finding_from_claim(
    claim: Claim, transcript: Transcript, *, participant_id: str, participant_name: str
) -> ParticipantFinding:
    ev = claim.evidence[0]
    return ParticipantFinding(
        participant_id=participant_id,
        participant_name=participant_name,
        claim_type=claim.claim_type.value,
        statement=_clean(claim.statement),
        tier=claim.tier,
        evidence_quote=ev.resolve(transcript),
        segment_id=ev.ref.segment_id,
        transcript_id=transcript.id,
    )


@dataclass(frozen=True)
class Contradiction:
    participant_a: str
    statement_a: str
    participant_b: str
    statement_b: str
    relation: Relation   # CONFLICT or VARIATION (a real disagreement)
    note: str = ""


@dataclass
class AggregatedFinding:
    topic_id: str
    claim_type: str
    label: str                          # a representative statement for the topic
    members: list[ParticipantFinding]
    contradictions: list[Contradiction]

    @property
    def participants(self) -> list[str]:
        return sorted({m.participant_id for m in self.members})

    @property
    def participant_count(self) -> int:
        return len(self.participants)

    @property
    def has_conflict(self) -> bool:
        return any(c.relation is Relation.CONFLICT for c in self.contradictions)

    @property
    def status(self) -> str:
        if self.has_conflict:
            return "contested"
        if self.participant_count >= 2:
            return "corroborated"
        return "single-source"


@dataclass
class AggregationResult:
    findings: list[AggregatedFinding]

    @property
    def corroborated(self) -> list[AggregatedFinding]:
        return [f for f in self.findings if f.status == "corroborated"]

    @property
    def contested(self) -> list[AggregatedFinding]:
        return [f for f in self.findings if f.status == "contested"]

    @property
    def single_source(self) -> list[AggregatedFinding]:
        return [f for f in self.findings if f.status == "single-source"]
