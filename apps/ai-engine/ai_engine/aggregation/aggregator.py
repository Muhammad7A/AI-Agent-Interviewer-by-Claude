"""Cluster findings into topics, then relate the findings within each topic."""
from __future__ import annotations

from collections import Counter

from .model import (
    AggregatedFinding,
    AggregationResult,
    Contradiction,
    MemberRelation,
    ParticipantFinding,
    Relation,
)
from .relation import (
    RelationChecker,
    content_words,
    make_relation_checker,
    overlap_coefficient,
)

# Two findings join the same topic if they share this much of the smaller word set.
_CLUSTER_MIN_OVERLAP = 0.34
_CLUSTER_MIN_SHARED = 2


def _text(f: ParticipantFinding) -> str:
    # Cluster on the claim plus its evidence quote — both carry the topic words.
    return f"{f.statement} {f.evidence_quote}"


def _cluster(findings: list[ParticipantFinding]) -> list[list[ParticipantFinding]]:
    topics: list[list[ParticipantFinding]] = []
    seeds: list[set[str]] = []
    for finding in findings:
        words = content_words(_text(finding))
        placed = False
        for i, seed in enumerate(seeds):
            shared = words & seed
            if len(shared) >= _CLUSTER_MIN_SHARED and overlap_coefficient(words, seed) >= _CLUSTER_MIN_OVERLAP:
                topics[i].append(finding)
                seeds[i] = seed | words  # let the topic grow to catch related wording
                placed = True
                break
        if not placed:
            topics.append([finding])
            seeds.append(words)
    return topics


def _relate_members(
    members: list[ParticipantFinding], checker: RelationChecker
) -> tuple[list[MemberRelation], list[Contradiction]]:
    """Classify every pair once; keep the full map and the disagreements."""
    relations: list[MemberRelation] = []
    contradictions: list[Contradiction] = []
    for i in range(len(members)):
        for j in range(i + 1, len(members)):
            a, b = members[i], members[j]
            if a.participant_id == b.participant_id:
                continue  # a person doesn't corroborate or contradict themselves
            relation = checker.classify(a.statement, b.statement)
            relations.append(MemberRelation(i=i, j=j, relation=relation))
            if relation in (Relation.CONFLICT, Relation.VARIATION):
                contradictions.append(
                    Contradiction(
                        participant_a=a.participant_name,
                        statement_a=a.statement,
                        participant_b=b.participant_name,
                        statement_b=b.statement,
                        relation=relation,
                    )
                )
    return relations, contradictions


def _dominant_type(members: list[ParticipantFinding]) -> str:
    return Counter(m.claim_type for m in members).most_common(1)[0][0]


def _label(members: list[ParticipantFinding]) -> str:
    # The longest statement tends to be the most complete description of the topic.
    return max(members, key=lambda m: len(m.statement)).statement


def aggregate(
    findings: list[ParticipantFinding], checker: RelationChecker | None = None
) -> AggregationResult:
    checker = checker or make_relation_checker(None)
    clusters = _cluster(findings)
    aggregated: list[AggregatedFinding] = []
    for i, members in enumerate(clusters):
        relations, contradictions = _relate_members(members, checker)
        aggregated.append(
            AggregatedFinding(
                topic_id=f"topic-{i + 1}",
                claim_type=_dominant_type(members),
                label=_label(members),
                members=members,
                contradictions=contradictions,
                relations=relations,
            )
        )
    # Most-corroborated and contested topics first.
    aggregated.sort(key=lambda f: (f.has_conflict, f.participant_count), reverse=True)
    return AggregationResult(findings=aggregated)
