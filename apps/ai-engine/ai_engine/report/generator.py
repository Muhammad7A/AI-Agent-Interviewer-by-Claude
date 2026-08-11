"""Render validated findings into a consultant-facing Markdown report.

Rules the report obeys:
  * Only human-validated findings appear (accepted or amended). Rejected and
    unvalidated proposals are excluded — the report is validated truth, not AI
    output (C4).
  * Every finding carries a verbatim evidence quote that resolves to the immutable
    transcript, with its segment id. No finding without provenance (C1/C5).
  * If validation was simulated (auto-sim), the header says so loudly, so an
    auto-generated demo can never be mistaken for a real deliverable.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..transcript.model import Transcript
from ..validation.model import ValidatedFinding, Verdict

# Section order and human-readable titles by claim type.
_GROUPS: list[tuple[str, str]] = [
    ("workaround", "Workarounds & Shadow Tooling"),
    ("bottleneck", "Bottlenecks & Delays"),
    ("friction", "Managerial & Process Friction"),
    ("wasted_effort", "Wasted & Redundant Effort"),
    ("ai_opportunity", "Automation / AI Opportunities"),
    ("observation", "Other Observations"),
]


def render_markdown_report(
    *,
    transcript: Transcript,
    findings: list[ValidatedFinding],
    objective: str,
    engagement_id: str,
    interview_id: str,
    validator_kind: str,
    validator_name: str,
    coverage_summary: dict | None = None,
    generated_at: datetime | None = None,
) -> str:
    generated_at = generated_at or datetime.now(timezone.utc)
    reportable = [f for f in findings if f.is_reportable]
    rejected = sum(1 for f in findings if f.verdict is Verdict.REJECTED)
    amended = sum(1 for f in findings if f.verdict is Verdict.AMENDED)
    accepted = sum(1 for f in findings if f.verdict is Verdict.ACCEPTED)

    lines: list[str] = []
    lines.append("# Organizational Assessment — Findings")
    lines.append("")
    if validator_kind != "consultant":
        lines.append(
            f"> ⚠️ **DEMO ONLY — validation was simulated (`{validator_kind}`), "
            "not performed by a human consultant. Not a real deliverable.**"
        )
        lines.append("")
    lines.append(f"- **Engagement:** {engagement_id}")
    lines.append(f"- **Interview:** {interview_id}")
    lines.append(f"- **Generated:** {generated_at.date().isoformat()}")
    lines.append(f"- **Validated by:** {validator_name}")
    lines.append(f"- **Objective:** {objective}")
    lines.append("")
    lines.append(
        "> Every finding below was proposed by AI from interview testimony and "
        "**validated by a human reviewer**. Each carries a verbatim quote that "
        "resolves to the source transcript. Unvalidated and rejected proposals are "
        "excluded."
    )
    lines.append("")

    if not reportable:
        lines.append("_No validated findings from this interview._")
        lines.append("")
    else:
        by_type: dict[str, list[ValidatedFinding]] = {}
        for f in reportable:
            by_type.setdefault(f.claim_type.value, []).append(f)

        for type_key, title in _GROUPS:
            group = by_type.get(type_key)
            if not group:
                continue
            lines.append(f"## {title}")
            lines.append("")
            for f in sorted(group, key=lambda x: x.tier, reverse=True):
                ev = f.claim.evidence[0]
                quote = ev.resolve(transcript)
                tag = "amended" if f.verdict is Verdict.AMENDED else "validated"
                lines.append(f"### {f.statement}")
                lines.append(f"_Tier {f.tier} · {tag}_")
                lines.append("")
                lines.append(
                    f"> \"{quote}\"  \n"
                    f"> — evidence `{ev.ref.segment_id}` [{ev.ref.start}:{ev.ref.end}] "
                    f"({ev.match_kind})"
                )
                lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Validated findings: **{len(reportable)}** "
                 f"({accepted} accepted, {amended} amended)")
    lines.append(f"- Proposals rejected in validation: {rejected}")
    if coverage_summary is not None:
        lines.append(
            f"- Interview coverage: {coverage_summary.get('areas_covered', '?')}/"
            f"{coverage_summary.get('areas_total', '?')} areas reached Tier 2+"
        )
    lines.append("")
    return "\n".join(lines)
