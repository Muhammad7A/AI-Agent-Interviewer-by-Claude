"""Render an evaluation suite result as a text/Markdown report."""
from __future__ import annotations

from .runner import SuiteResult


def render_eval_report(suite: SuiteResult, *, mode: str) -> str:
    lines: list[str] = []
    lines.append("# Ontora Evaluation Harness")
    lines.append("")
    lines.append(f"- **Mode:** {mode}")
    lines.append(f"- **Overall:** {'PASS ✅' if suite.passed else 'FAIL ❌'}")
    lines.append("")
    lines.append("> Two-layer eval against known ground truth (the personas' latent "
                 "truths). Safety gates apply to every case; capability gates apply "
                 "at the candor ceiling (open). Calibration is not scored — no "
                 "confidence signal exists yet (C2).")
    lines.append("")

    # Per-case table.
    lines.append("## Per-case metrics")
    lines.append("")
    header = ("| case | elic. recall | e2e recall | precision | value dens. | "
              "confab | leak | gates |")
    lines.append(header)
    lines.append("|" + "---|" * 8)
    for c in suite.cases:
        m = c.metrics
        lines.append(
            f"| {m.persona}/{m.candor} "
            f"| {m.elicited}/{m.achievable} ({m.elicitation_recall:.0%}) "
            f"| {m.captured}/{m.achievable} ({m.e2e_recall:.0%}) "
            f"| {m.precision:.0%} "
            f"| {m.value_density:.0%} "
            f"| {m.confabulation_rate:.0%} "
            f"| {m.candor_leak} "
            f"| {'PASS' if c.passed else 'FAIL'} |"
        )
    lines.append("")

    # Candor curve — elicitation recall rising with candor, per persona.
    lines.append("## Candor curve (elicitation recall by candor level)")
    lines.append("")
    personas: dict[str, dict[str, float]] = {}
    for c in suite.cases:
        personas.setdefault(c.metrics.persona, {})[c.metrics.candor] = c.metrics.elicitation_recall
    for persona, curve in personas.items():
        parts = [f"{lvl} {curve.get(lvl, 0):.0%}" for lvl in ("guarded", "neutral", "open")]
        lines.append(f"- **{persona}:** " + "  →  ".join(parts))
    lines.append("")

    # Gate detail for any failing case.
    failing = [c for c in suite.cases if not c.passed]
    if failing:
        lines.append("## Failing gates")
        lines.append("")
        for c in failing:
            for g in c.gates:
                if not g.passed:
                    lines.append(f"- `{c.metrics.persona}/{c.metrics.candor}` "
                                 f"[{g.scope}] **{g.name}** — {g.detail}")
        lines.append("")

    return "\n".join(lines)
