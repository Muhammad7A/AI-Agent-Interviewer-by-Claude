"""Render an evaluation suite result as text/Markdown, and as machine-readable JSON."""
from __future__ import annotations

from .metrics import CaseMetrics
from .runner import CaseResult, SuiteResult


def _pct_range(stat: tuple[float, float, float]) -> str:
    """Format a (min, mean, max) triple. Collapses to one number if there's no spread."""
    lo, mean, hi = stat
    if abs(hi - lo) < 1e-9:
        return f"{mean:.0%}"
    return f"{mean:.0%} ({lo:.0%}–{hi:.0%})"


def render_eval_report(suite: SuiteResult, *, mode: str) -> str:
    lines: list[str] = []
    lines.append("# Groundwork Evaluation Harness")
    lines.append("")
    lines.append(f"- **Mode:** {mode}")
    lines.append(f"- **Repeats per case:** {suite.repeats}")
    lines.append(f"- **Overall:** {'PASS ✅' if suite.passed else 'FAIL ❌'}")
    lines.append("")
    lines.append("> Two-layer eval against known ground truth (the personas' latent "
                 "truths). Safety gates apply to every case; capability gates apply "
                 "at the candor ceiling (open). A case passes only if it passes on "
                 "every repeat. Numbers are mean (min–max) across repeats. Calibration "
                 "is not scored — no confidence signal exists yet (C2).")
    lines.append("")

    lines.append("## Per-case metrics")
    lines.append("")
    lines.append("| case | elic. recall | e2e recall | precision | value dens. | "
                 "confab (max) | leak | gates |")
    lines.append("|" + "---|" * 8)
    for c in suite.cases:
        lines.append(
            f"| {c.persona}/{c.candor} "
            f"| {_pct_range(c.stat(lambda m: m.elicitation_recall))} "
            f"| {_pct_range(c.stat(lambda m: m.e2e_recall))} "
            f"| {_pct_range(c.stat(lambda m: m.precision))} "
            f"| {_pct_range(c.stat(lambda m: m.value_density))} "
            f"| {c.stat(lambda m: m.confabulation_rate)[2]:.0%} "
            f"| {max(m.candor_leak for m in c.runs)} "
            f"| {'PASS' if c.passed else 'FAIL'} |"
        )
    lines.append("")

    lines.append("## Candor curve (elicitation recall by candor level)")
    lines.append("")
    personas: dict[str, dict[str, float]] = {}
    for c in suite.cases:
        personas.setdefault(c.persona, {})[c.candor] = c.stat(lambda m: m.elicitation_recall)[1]
    for persona, curve in personas.items():
        parts = [f"{lvl} {curve.get(lvl, 0):.0%}" for lvl in ("guarded", "neutral", "open")]
        lines.append(f"- **{persona}:** " + "  →  ".join(parts))
    lines.append("")

    failing = [c for c in suite.cases if not c.passed]
    if failing:
        lines.append("## Failing gates")
        lines.append("")
        for c in failing:
            for g in c.failing_gates():
                lines.append(f"- `{c.persona}/{c.candor}` [{g.scope}] **{g.name}** — {g.detail}")
        lines.append("")

    return "\n".join(lines)


def _metrics_to_dict(m: CaseMetrics) -> dict:
    return {
        "achievable": m.achievable,
        "elicited": m.elicited,
        "claims": m.claims,
        "matched_claims": m.matched_claims,
        "captured": m.captured,
        "tier2plus_claims": m.tier2plus_claims,
        "candor_leak": m.candor_leak,
        "elicitation_recall": round(m.elicitation_recall, 4),
        "synthesis_recall": round(m.synthesis_recall, 4),
        "e2e_recall": round(m.e2e_recall, 4),
        "precision": round(m.precision, 4),
        "value_density": round(m.value_density, 4),
        "confabulation_rate": round(m.confabulation_rate, 4),
    }


def suite_to_dict(suite: SuiteResult, *, mode: str) -> dict:
    """Machine-readable results for saving and diffing runs over time."""
    return {
        "mode": mode,
        "repeats": suite.repeats,
        "passed": suite.passed,
        "cases": [
            {
                "name": c.name,
                "persona": c.persona,
                "candor": c.candor,
                "is_ceiling": c.is_ceiling,
                "passed": c.passed,
                "runs": [_metrics_to_dict(m) for m in c.runs],
            }
            for c in suite.cases
        ],
    }
