"""The evaluation laboratory CLI.

    python -m ai_engine.lab                          # run the golden suite, print scores
    python -m ai_engine.lab --repeats 3              # + repeatability analysis
    python -m ai_engine.lab --save-baseline baselines/golden.json
    python -m ai_engine.lab --baseline baselines/golden.json --check
                                                          # exit 1 on regression

Mock mode by default (deterministic, no network, no keys). With a live
provider configured the same suites run against the real model — and the
report says which mode produced every number.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .dataset import load_golden
from .regression import compare
from .runner import run_suite
from .schemas import load_results, write_results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Groundwork evaluation laboratory")
    parser.add_argument("--repeats", type=int, default=2,
                        help="runs per scenario (repeatability analysis)")
    parser.add_argument("--save", metavar="PATH", default=None,
                        help="write this run's results to PATH")
    parser.add_argument("--save-baseline", metavar="PATH", default=None,
                        help="write this run as the regression baseline")
    parser.add_argument("--baseline", metavar="PATH", default=None,
                        help="compare against this baseline")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 when the current run regresses vs --baseline")
    parser.add_argument("--tolerance", type=float, default=0.0,
                        help="allowed total-score drop before it counts as drift")
    args = parser.parse_args(argv)

    from ..config import load_settings

    settings = load_settings()
    _version, scenarios = load_golden()
    result = run_suite(scenarios, settings, suite_id="golden",
                       repeats=args.repeats)

    print(f"# Groundwork evaluation lab — suite=golden mode={result.mode} "
          f"scenarios={len(scenarios)} repeats={args.repeats}")
    print()
    print("| scenario | score | status | latency ms | outputs |")
    print("|---|---|---|---|---|")
    for evaluation in result.evaluations:
        statuses = ",".join(sorted({r.status for r in evaluation.results})) or "-"
        print(f"| {evaluation.scenario_id} | "
              f"{evaluation.total_score if evaluation.total_score is not None else 'unscored'} | "
              f"{statuses} | {evaluation.latency_ms} | "
              f"{evaluation.output_sha[:8]} |")
    print()
    print("## Repeatability")
    print()
    print("| scenario | runs | distinct outputs | failures | score min-max | latency mean±std |")
    print("|---|---|---|---|---|---|")
    for v in result.variance:
        band = (f"{v.score_min}–{v.score_max}" if v.score_min is not None else "—")
        print(f"| {v.scenario_id} | {v.runs} | {v.distinct_outputs} | {v.failures} "
              f"| {band} | {v.latency_ms_mean}±{v.latency_ms_stddev} |")
    print()

    if args.save:
        write_results(result.evaluations, Path(args.save))
        print(f"results written: {args.save}")

    if args.save_baseline:
        write_results(result.evaluations,
                      Path(args.save_baseline))
        print(f"baseline written: {args.save_baseline}")

    if args.baseline and args.check:
        baseline = load_results(args.baseline)
        report = compare(baseline, result.evaluations,
                         score_tolerance=args.tolerance)
        print(report.summary())
        return 1 if report.has_regression else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
