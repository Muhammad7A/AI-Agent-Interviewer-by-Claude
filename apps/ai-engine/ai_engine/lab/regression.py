"""Regression detection: current lab results against a committed baseline.

A regression is any of:
  * a scenario's total score dropping below baseline by more than the
    tolerance (score drift),
  * a criterion that passed in the baseline failing now,
  * a scenario that produced one output in the baseline producing several now
    (behavior variance appearing),
  * an engine failure during a run that previously succeeded (failure rate).

Latency is REPORTED, never failed — hardware noise is not a behavior change.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .schemas import TurnEvaluation


@dataclass
class DriftRow:
    scenario_id: str
    kind: str            # score-drop | criterion-flip | variance-appeared | failure-new | meta
    detail: str
    #: Informational rows (improvements, mode notes) never trip the gate.
    informational: bool = False


@dataclass
class RegressionReport:
    baseline_count: int
    current_count: int
    baseline_mode: str = ""
    current_mode: str = ""
    rows: list[DriftRow] = field(default_factory=list)

    @property
    def has_regression(self) -> bool:
        return any(not r.informational for r in self.rows)

    def summary(self) -> str:
        if not self.rows:
            return (f"no regression ({self.current_count} evaluations vs "
                    f"{self.baseline_count} baseline)")
        lines = [f"REGRESSION ({len(self.rows)} row(s)):"]
        lines += [f"  - [{r.kind}] {r.scenario_id}: {r.detail}" for r in self.rows]
        return "\n".join(lines)


def _by_scenario(evals: list[TurnEvaluation]) -> dict[str, list[TurnEvaluation]]:
    grouped: dict[str, list[TurnEvaluation]] = {}
    for e in evals:
        grouped.setdefault(e.scenario_id, []).append(e)
    return grouped


def _criterion_map(evaluation: TurnEvaluation) -> dict[str, str]:
    return {r.rubric_id: r.status for r in evaluation.results}


def compare(baseline: list[TurnEvaluation], current: list[TurnEvaluation],
            *, score_tolerance: float = 0.0) -> RegressionReport:
    report = RegressionReport(baseline_count=len(baseline),
                              current_count=len(current))
    # A baseline recorded from a broken tree enshrines failure as canonical.
    broken = sorted({e.scenario_id for e in baseline if e.error})
    if broken:
        raise ValueError(
            "the baseline contains failed runs ("
            f"{', '.join(broken[:3])}{'…' if len(broken) > 3 else ''}) — "
            "re-baseline from a healthy tree instead of enshrining the failure")
    base = _by_scenario(baseline)
    curr = _by_scenario(current)
    if baseline and current:
        report.baseline_mode = baseline[0].mode
        report.current_mode = current[0].mode
        if report.baseline_mode != report.current_mode:
            report.rows.append(DriftRow(
                "(meta)", "meta",
                f"mode changed: {report.baseline_mode!r} → "
                f"{report.current_mode!r} — scores are not comparable",
                informational=True))
        if baseline[0].rubric_version != current[0].rubric_version:
            report.rows.append(DriftRow(
                "(meta)", "meta",
                f"rubric version changed: {baseline[0].rubric_version!r} → "
                f"{current[0].rubric_version!r}", informational=True))

    for scenario_id, base_runs in base.items():
        curr_runs = curr.get(scenario_id, [])
        if not curr_runs:
            report.rows.append(DriftRow(
                scenario_id, "criterion-flip",
                "scenario present in baseline but MISSING from the current run"))
            continue
        # Compare the FIRST run of each side per scenario (repeats measure
        # variance; the baseline records the canonical first run).
        b, c = base_runs[0], curr_runs[0]
        if b.error and not c.error:
            report.rows.append(DriftRow(
                scenario_id, "failure-new",
                f"baseline run failed ({b.error.split(':')[0]}) but current "
                f"succeeded — improvement; re-baseline to record it",
                informational=True))
        if c.error and not b.error:
            report.rows.append(DriftRow(
                scenario_id, "failure-new",
                f"current run failed where baseline succeeded: {c.error}"))
            continue
        if b.total_score is not None and c.total_score is not None:
            delta = c.total_score - b.total_score
            if delta < -score_tolerance:
                report.rows.append(DriftRow(
                    scenario_id, "score-drop",
                    f"total {b.total_score} → {c.total_score} "
                    f"(Δ {delta:+.4f}, tolerance -{score_tolerance})"))
        b_statuses, c_statuses = _criterion_map(b), _criterion_map(c)
        for rubric_id, b_status in b_statuses.items():
            c_status = c_statuses.get(rubric_id)
            if c_status is None:
                report.rows.append(DriftRow(
                    scenario_id, "criterion-flip",
                    f"{rubric_id}: present in baseline, REMOVED from the "
                    f"current run"))
                continue
            # pass -> partial is a silent degradation, not a pass.
            if b_status == "pass" and c_status in ("fail", "unscored", "partial"):
                report.rows.append(DriftRow(
                    scenario_id, "criterion-flip",
                    f"{rubric_id}: {b_status} → {c_status}"))
        # In mock mode the produced utterance IS the behavior: any hash change
        # across baseline/current is a behavior change, even at equal scores —
        # a silent question rewording would otherwise sail through.
        if b.mode == "mock" and c.mode == "mock" and not c.error:
            if b.output_sha != c.output_sha:
                report.rows.append(DriftRow(
                    scenario_id, "criterion-flip",
                    f"produced output changed: {b.output_sha} → {c.output_sha} "
                    f"(scores equal — a rewording; review and re-baseline)"))
        b_distinct = len({e.output_sha for e in base_runs})
        c_distinct = len({e.output_sha for e in curr_runs})
        if b_distinct == 1 and c_distinct > 1:
            report.rows.append(DriftRow(
                scenario_id, "variance-appeared",
                f"baseline produced 1 distinct output across {len(base_runs)} "
                f"run(s); current produced {c_distinct} across {len(curr_runs)}"))

    for scenario_id in sorted(set(curr) - set(base)):
        report.rows.append(DriftRow(
            scenario_id, "criterion-flip",
            "scenario is NEW in the current run (add it to the baseline)"))
    return report
