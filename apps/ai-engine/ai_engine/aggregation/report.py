"""Render an org-level aggregation as Markdown."""
from __future__ import annotations

from .model import AggregatedFinding, AggregationResult, Relation

_RELATION_MARK = {Relation.CONFLICT: "⚠ CONFLICT", Relation.VARIATION: "≈ VARIATION"}


def _provenance(member) -> str:
    return (f"    - **{member.participant_name}:** \"{member.evidence_quote}\"  \n"
            f"      _(interview `{member.transcript_id}`, segment `{member.segment_id}`)_")


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
            lines.append(f"### {f.label}")
            lines.append(f"_{f.claim_type} · {f.participant_count} participants_")
            lines.append("")
            for c in f.contradictions:
                mark = _RELATION_MARK.get(c.relation, c.relation.value)
                lines.append(f"- **{mark}**")
                lines.append(f"  - **{c.participant_a}:** \"{c.statement_a}\"")
                lines.append(f"  - **{c.participant_b}:** \"{c.statement_b}\"")
            lines.append("")

    if result.corroborated:
        lines.append("## ✓ Corroborated — multiple independent sources")
        lines.append("")
        for f in result.corroborated:
            lines.append(f"### {f.label}")
            lines.append(f"_{f.claim_type} · corroborated by {f.participant_count} participants_")
            lines.append("")
            for m in f.members:
                lines.append(_provenance(m))
            lines.append("")

    if result.single_source:
        lines.append("## Single-source — one person, needs corroboration")
        lines.append("")
        for f in result.single_source:
            m = f.members[0]
            lines.append(f"- _{f.claim_type}_ — **{m.participant_name}:** {f.label}")
        lines.append("")

    return "\n".join(lines)
