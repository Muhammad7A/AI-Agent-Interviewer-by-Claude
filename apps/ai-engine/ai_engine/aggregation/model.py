"""The aggregation data model.

A :class:`ParticipantFinding` is one person's finding, carrying its own resolved
evidence and the address of the transcript segment it came from — so cross-
interview provenance survives aggregation. An :class:`AggregatedFinding` is a
topic several findings map to, with its corroboration count and any contradictions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
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
    # How exactly the quote matched the source ("exact" | "normalized" | "flexible").
    # Carried through because interpretive distance is a confidence signal.
    match_kind: str = "exact"
    #: The team, department or reporting line this person sits in, when known.
    #:
    #: Confidence treats agreement as independent evidence, and in an organization
    #: it frequently is not: five people on one team saying "the approval takes
    #: three days" is most likely one fact that circulated through a team, not five
    #: observations. Where the cohort is known the scorer discounts agreement inside
    #: it; where it is ``None`` the scorer caps the corroboration term instead,
    #: because unmodeled correlation is a reason to claim less, not more.
    cohort: str | None = None


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
        match_kind=ev.match_kind,
    )


@dataclass(frozen=True)
class MemberRelation:
    """How two members of one topic relate, by index into ``members``.

    The full pairwise map is kept (not just the contradictions) because
    "who agrees with *this* finding" is the strongest honest confidence signal:
    a finding on the majority side of a disagreement is better supported than the
    lone dissenter, and topic size alone cannot express that.
    """

    i: int
    j: int
    relation: "Relation"


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
    relations: list[MemberRelation] = field(default_factory=list)

    def agreeing_with(self, index: int) -> list[int]:
        """Indices of members that AGREE with ``members[index]``."""
        out: list[int] = []
        for rel in self.relations:
            if rel.relation is not Relation.AGREE:
                continue
            if rel.i == index:
                out.append(rel.j)
            elif rel.j == index:
                out.append(rel.i)
        return out

    def conflicting_with(self, index: int) -> list[int]:
        """Indices of members that CONFLICT with ``members[index]``."""
        out: list[int] = []
        for rel in self.relations:
            if rel.relation is not Relation.CONFLICT:
                continue
            if rel.i == index:
                out.append(rel.j)
            elif rel.j == index:
                out.append(rel.i)
        return out

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
