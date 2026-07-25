"""The release gate: the only door from aggregated findings to an audience.

Nothing reaches an employer except through :func:`release`. It never mutates the
aggregation — it produces a separate, redacted *view*, so the consultant's copy and
the employer's copy cannot drift, and the redaction can be diffed and audited.

Everything withheld is recorded in a suppression ledger. The employer learns that
*something* was withheld and why the rule exists, but not what — transparency about
the mechanism without leakage of the content.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..aggregation.model import AggregatedFinding, AggregationResult
from .policy import Audience, ReleasePolicy


@dataclass(frozen=True)
class ReleasedStatement:
    """One finding as a given audience may see it."""

    text: str
    tier: int
    attributed_to: str | None = None   # pseudonym, or None when attribution is withheld
    quote: str | None = None           # verbatim source, or None when withheld
    confidence: float | None = None
    withheld: tuple[str, ...] = ()     # what was stripped, for the audit trail


@dataclass(frozen=True)
class ReleasedTopic:
    label: str
    claim_type: str
    participant_count: int
    statements: tuple[ReleasedStatement, ...]
    contested: bool
    confidence: float | None = None
    #: Set when a disagreement exists but its sides are withheld.
    contested_note: str | None = None


@dataclass(frozen=True)
class Suppression:
    label: str
    reason: str
    detail: str


@dataclass
class ReleasePackage:
    policy: ReleasePolicy
    topics: list[ReleasedTopic] = field(default_factory=list)
    suppressions: list[Suppression] = field(default_factory=list)

    @property
    def audience(self) -> Audience:
        return self.policy.audience

    @property
    def released_count(self) -> int:
        return len(self.topics)

    def all_text(self) -> str:
        """Every string a reader of this package could see.

        Used by the tests to assert the hard invariants (no real names, no sensitive
        verbatim quotes) over the *whole* payload rather than one rendering of it.
        """
        parts: list[str] = []
        for topic in self.topics:
            parts += [topic.label, topic.claim_type, topic.contested_note or ""]
            for s in topic.statements:
                parts += [s.text, s.attributed_to or "", s.quote or ""]
        for sup in self.suppressions:
            parts += [sup.label, sup.reason, sup.detail]
        return "\n".join(parts)


def _confidences(finding: AggregatedFinding) -> list[float] | None:
    try:
        from ..confidence.scorer import score_topic
    except ImportError:  # pragma: no cover
        return None
    return [s.value for s in score_topic(finding)]


def _neutral_label(finding: AggregatedFinding) -> str:
    """A topic label built only from vocabulary that several participants share.

    The aggregation's own label is the longest member statement — i.e. one person's
    verbatim words — so it cannot be used outside the firewall. Terms used by two or
    more participants are, by construction, not unique to anyone, which makes them
    safe to name while still identifying the subject.
    """
    from collections import Counter

    from ..aggregation.relation import content_words

    counts: Counter[str] = Counter()
    for member in finding.members:
        for word in content_words(member.statement):
            counts[word] += 1
    threshold = 2 if len(finding.members) > 1 else 1
    shared = [w for w, c in counts.most_common() if c >= threshold][:5]
    kind = finding.claim_type.replace("_", " ")
    if not shared:
        return f"{kind} (specifics withheld)"
    return f"{kind}: {', '.join(shared)}"


def _release_topic(
    finding: AggregatedFinding, policy: ReleasePolicy
) -> tuple[ReleasedTopic | None, Suppression | None]:
    count = finding.participant_count

    if policy.suppress_below_k and count < policy.k_anonymity:
        return None, Suppression(
            label=finding.claim_type,
            reason="below k-anonymity threshold",
            detail=(f"a topic with {count} participant(s) cannot be released at "
                    f"k={policy.k_anonymity}; too few voices to prevent identification"),
        )

    scores = _confidences(finding)

    # Aggregate-only: one group-level item, no per-participant content at all.
    if policy.aggregate_only:
        contested = bool(finding.contradictions)
        note = None
        if contested:
            note = ("Participants do not agree on this topic. The positions and who "
                    "holds them are withheld to protect confidentiality.")
        return ReleasedTopic(
            label=_neutral_label(finding),
            claim_type=finding.claim_type,
            participant_count=count,
            statements=(ReleasedStatement(
                text=(f"{count} participants raised this. "
                      f"Individual responses are withheld."),
                tier=max((m.tier for m in finding.members), default=0),
                attributed_to=None,
                quote=None,
                confidence=None,
                withheld=("individual responses", "attribution", "verbatim quotes",
                          "per-participant confidence"),
            ),),
            contested=contested,
            confidence=max(scores) if scores else None,
            contested_note=note,
        ), None
    statements: list[ReleasedStatement] = []
    for i, member in enumerate(finding.members):
        withheld: list[str] = []

        attributed = member.participant_id
        if member.tier > policy.attribute_max_tier:
            attributed = None
            withheld.append("attribution")

        quote = member.evidence_quote
        if member.tier > policy.verbatim_max_tier:
            # A verbatim quote is a fingerprint, so sensitive tiers are summarised.
            quote = None
            withheld.append("verbatim quote")

        confidence = None
        if scores and policy.reveal_per_member_confidence:
            confidence = scores[i]
        elif scores:
            withheld.append("per-participant confidence")

        statements.append(ReleasedStatement(
            text=member.statement,
            tier=member.tier,
            attributed_to=attributed,
            quote=quote,
            confidence=confidence,
            withheld=tuple(withheld),
        ))

    contested = bool(finding.contradictions)
    note = None
    if contested and not policy.reveal_contradiction_sides:
        # Naming who dissents is the most dangerous disclosure the product can make,
        # and side sizes identify a lone dissenter even without names. Report only
        # that a disagreement exists.
        note = ("Participants do not agree on this topic. The positions and who holds "
                "them are withheld to protect confidentiality.")
        statements = _collapse_contested(statements)

    topic_confidence = max(scores) if scores else None
    return ReleasedTopic(
        label=finding.label,
        claim_type=finding.claim_type,
        participant_count=count,
        statements=tuple(statements),
        contested=contested,
        confidence=topic_confidence,
        contested_note=note,
    ), None


def _collapse_contested(statements: list[ReleasedStatement]) -> list[ReleasedStatement]:
    """Drop per-position detail from a contested topic, keeping the topic itself.

    Without this, "3 say X, 1 says Y" identifies the dissenter to anyone who knows
    the team — the side sizes are the leak, not the names.
    """
    return [
        ReleasedStatement(
            text=statements[0].text if statements else "",
            tier=max((s.tier for s in statements), default=0),
            attributed_to=None,
            quote=None,
            confidence=None,
            withheld=("attribution", "verbatim quote", "positions", "side sizes"),
        )
    ]


def release(
    aggregation: AggregationResult, *, policy: ReleasePolicy
) -> ReleasePackage:
    """Produce the view of ``aggregation`` that ``policy``'s audience may see."""
    package = ReleasePackage(policy=policy)
    for finding in aggregation.findings:
        topic, suppression = _release_topic(finding, policy)
        if topic is not None:
            package.topics.append(topic)
        if suppression is not None:
            package.suppressions.append(suppression)
    return package
