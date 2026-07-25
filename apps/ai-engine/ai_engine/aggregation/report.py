"""Render an org-level aggregation as Markdown."""
from __future__ import annotations

from .model import AggregatedFinding, AggregationResult, Relation

_RELATION_MARK = {Relation.CONFLICT: "⚠ CONFLICT", Relation.VARIATION: "≈ VARIATION"}


def _provenance(member, score=None) -> str:
    conf = f" — _confidence {score.value:.2f} ({score.band.value})_" if score else ""
    return (f"    - **{member.participant_name}:** \"{member.evidence_quote}\"{conf}  \n"
            f"      _(interview `{member.transcript_id}`, segment `{member.segment_id}`)_")


def _topic_confidence(finding: AggregatedFinding):
    """Best per-member confidence in the topic, or None if scoring is unavailable.

    Imported lazily so the aggregation module stays usable without the confidence
    module, and so confidence remains an *added* read rather than a dependency.
    """
    try:
        from ..confidence.scorer import score_topic
    except ImportError:  # pragma: no cover
        return None, None
    scores = score_topic(finding)
    return scores, (max(s.value for s in scores) if scores else None)


def render_org_report(
    result: AggregationResult,
    *,
    org_name: str,
    interview_count: int,
) -> str:
    lines: list[str] = []
    lines.append(f"# Organizational Intelligence — {org_name}")
    lines.append("")
    lines.append(f"- **Interviews aggregated:** {interview_count}")
    lines.append(f"- **Topics found:** {len(result.findings)} "
                 f"({len(result.corroborated)} corroborated, "
                 f"{len(result.contested)} contested, "
                 f"{len(result.single_source)} single-source)")
    lines.append("")
    lines.append("> Findings fused across interviews. Agreement across independent "
                 "people raises confidence; disagreement is surfaced, not hidden. "
                 "Every statement still resolves to its own interview's transcript.")
    lines.append("")

    if result.contested:
        lines.append("## ⚠ Contested — investigate first")
        lines.append("")
        lines.append("People disagree here. A contradiction is a *signal*, not noise.")
        lines.append("")
        for f in result.contested:
            scores, _ = _topic_confidence(f)
            lines.append(f"### {f.label}")
            lines.append(f"_{f.claim_type} · {f.participant_count} participants_")
            lines.append("")
            for c in f.contradictions:
                mark = _RELATION_MARK.get(c.relation, c.relation.value)
                lines.append(f"- **{mark}**")
                lines.append(f"  - **{c.participant_a}:** \"{c.statement_a}\"")
                lines.append(f"  - **{c.participant_b}:** \"{c.statement_b}\"")
            if scores:
                lines.append("")
                lines.append("  Confidence per side (a lone dissenter scores lowest):")
                for m, s in zip(f.members, scores):
                    lines.append(f"  - {m.participant_name}: **{s.value:.2f}** ({s.band.value})")
            lines.append("")

    if result.corroborated:
        lines.append("## ✓ Corroborated — multiple independent sources")
        lines.append("")
        for f in result.corroborated:
            scores, best = _topic_confidence(f)
            conf = f" · confidence **{best:.2f}**" if best is not None else ""
            lines.append(f"### {f.label}")
            lines.append(f"_{f.claim_type} · corroborated by {f.participant_count} "
                         f"participants{conf}_")
            lines.append("")
            for i, m in enumerate(f.members):
                lines.append(_provenance(m, scores[i] if scores else None))
            lines.append("")

    if result.single_source:
        lines.append("## Single-source — one person, needs corroboration")
        lines.append("")
        for f in result.single_source:
            m = f.members[0]
            lines.append(f"- _{f.claim_type}_ — **{m.participant_name}:** {f.label}")
        lines.append("")

    return "\n".join(lines)
