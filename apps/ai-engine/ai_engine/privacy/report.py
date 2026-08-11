"""Render a release package as Markdown, honouring the audience.

There is exactly one renderer for released content, so an employer-facing document
cannot be produced by a code path that skipped the gate.
"""
from __future__ import annotations

from .policy import Audience
from .release import ReleasePackage


def render_release_report(
    package: ReleasePackage, *, org_name: str, interview_count: int
) -> str:
    policy = package.policy
    employer = policy.audience is Audience.EMPLOYER

    lines: list[str] = []
    lines.append(f"# Organizational Findings — {org_name}")
    lines.append("")
    lines.append(f"- **Audience:** {policy.audience.value}")
    lines.append(f"- **Interviews:** {interview_count}")
    lines.append(f"- **Topics released:** {package.released_count}"
                 + (f" · **withheld:** {len(package.suppressions)}"
                    if package.suppressions else ""))
    lines.append("")
    lines.append(f"> {policy.summary()}")
    lines.append("")

    if employer:
        lines.append("> **What you are not seeing, and why.** Individual responses are "
                     "confidential to the interviewing consultant. Names are never "
                     "released. Verbatim quotes are withheld for sensitive topics "
                     "because the wording itself can identify who spoke. Where "
                     "participants disagreed, the disagreement is reported but the "
                     "positions are not. These limits are what make candid answers "
                     "possible in the first place.")
        lines.append("")

    if not package.topics:
        lines.append("_No topics met the release threshold._")
        lines.append("")

    contested = [t for t in package.topics if t.contested]
    settled = [t for t in package.topics if not t.contested]

    if contested:
        lines.append("## Disputed — worth investigating")
        lines.append("")
        for topic in contested:
            conf = f" · confidence {topic.confidence:.2f}" if topic.confidence else ""
            lines.append(f"### {topic.label}")
            lines.append(f"_{topic.claim_type} · {topic.participant_count} participants{conf}_")
            lines.append("")
            if topic.contested_note:
                lines.append(f"> {topic.contested_note}")
                lines.append("")
            else:
                for s in topic.statements:
                    who = f"**{s.attributed_to}:** " if s.attributed_to else ""
                    lines.append(f"- {who}{s.text}")
                    if s.quote:
                        lines.append(f"  - evidence: \"{s.quote}\"")
                lines.append("")

    if settled:
        lines.append("## Findings")
        lines.append("")
        for topic in settled:
            conf = f" · confidence {topic.confidence:.2f}" if topic.confidence else ""
            lines.append(f"### {topic.label}")
            lines.append(f"_{topic.claim_type} · {topic.participant_count} "
                         f"participants{conf}_")
            lines.append("")
            for s in topic.statements:
                who = f"**{s.attributed_to}:** " if s.attributed_to else ""
                bits = f"- {who}{s.text}"
                if s.confidence is not None:
                    bits += f" _(confidence {s.confidence:.2f})_"
                lines.append(bits)
                if s.quote:
                    lines.append(f"  - evidence: \"{s.quote}\"")
                elif s.withheld:
                    lines.append(f"  - _withheld: {', '.join(s.withheld)}_")
            lines.append("")

    if package.suppressions:
        lines.append("## Withheld to protect confidentiality")
        lines.append("")
        lines.append(f"{len(package.suppressions)} topic(s) were not released. The "
                     f"reason is shown; the content is not.")
        lines.append("")
        for sup in package.suppressions:
            lines.append(f"- **{sup.reason}** — {sup.detail}")
        lines.append("")

    return "\n".join(lines)
