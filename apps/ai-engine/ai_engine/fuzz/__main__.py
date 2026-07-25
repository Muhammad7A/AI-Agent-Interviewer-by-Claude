"""Audit the safety gates with generated near-miss inputs.

    python -m ai_engine.fuzz                    # default audit
    python -m ai_engine.fuzz --cases 2000       # deeper
    python -m ai_engine.fuzz --seed 3 --verbose # show every violation

Exit code is 0 only if no property was violated, so this is a CI gate on the two
mechanisms the product's credibility rests on.
"""
from __future__ import annotations

import argparse
import sys

from .runner import run_fuzz


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora safety-gate fuzz audit")
    parser.add_argument("--cases", type=int, default=400, help="quote spans to mutate")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--org-size", type=int, default=6, help="interviews in the corpus")
    parser.add_argument("--verbose", action="store_true", help="list every violation")
    args = parser.parse_args(argv)

    report = run_fuzz(cases=args.cases, seed=args.seed, org_size=args.org_size)

    print("# Safety-Gate Fuzz Audit")
    print()
    print(f"- **Seed:** {args.seed}   **Spans mutated:** {args.cases}   "
          f"**Property checks run:** {report.total_checked}")
    print(f"- **Result:** {'PASS ✅' if report.passed else 'FAIL ❌'}"
          f"   ({len(report.critical_violations)} critical, "
          f"{len(report.violations) - len(report.critical_violations)} other)")
    print()
    print("| property | checks | violations |")
    print("|---|---|---|")
    for prop, count in sorted(report.checked.items()):
        bad = sum(1 for v in report.violations if v.prop == prop)
        mark = f"**{bad}**" if bad else "0"
        print(f"| `{prop}` | {count} | {mark} |")
    print()

    if report.skipped:
        skipped_total = sum(report.skipped.values())
        print(f"_{skipped_total} mutation attempts skipped as inapplicable or as "
              f"coincidental matches (a mutation that still appears in the source "
              f"would be a correct accept, not a bug)._")
        print()

    if report.violations:
        print("## Violations")
        print()
        shown = report.violations if args.verbose else report.violations[:20]
        for v in shown:
            print(f"- **{v.severity}** in `{v.prop}` — {v.detail}")
            if v.original:
                print(f"  - original: `{v.original}`")
                print(f"  - mutated:  `{v.mutated}`")
        if len(report.violations) > len(shown):
            print(f"- _… {len(report.violations) - len(shown)} more "
                  f"(use --verbose)_")
        print()

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
