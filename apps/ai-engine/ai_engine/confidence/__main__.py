"""Run the confidence calibration study.

    python -m ai_engine.confidence              # offline, deterministic
    python -m ai_engine.confidence --write      # also write calibration_study.md

With ANTHROPIC_API_KEY set, the whole chain (interview, tagging, entailment,
relation classification) uses the live model — the first real test of whether
derived confidence tracks truth.
"""
from __future__ import annotations

import argparse
import sys

from ..config import get_llm_client, load_settings
from .study import render_study_report, run_study


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora confidence calibration study")
    parser.add_argument("--write", action="store_true", help="write the report to the data dir")
    parser.add_argument("--candor", default="open", help="persona candor (default: open)")
    parser.add_argument("--generate", type=int, metavar="N", default=None,
                        help="study a GENERATED org of N employees instead of the "
                             "hand-written one (statistically meaningful n)")
    parser.add_argument("--seed", type=int, default=0, help="generator seed (with --generate)")
    parser.add_argument("--contradiction-rate", type=float, default=None,
                        help="fraction of deniable topics that get a planted disagreement")
    parser.add_argument("--minority-correct-rate", type=float, default=None,
                        help="fraction of contradictions where the MINORITY is right")
    args = parser.parse_args(argv)

    settings = load_settings()
    llm = get_llm_client(settings)
    mode = "LIVE model" if llm is not None else "MOCK (deterministic, no API key)"

    org = None
    if args.generate:
        from ..synthetic import OrgSpec
        from .study import synthetic_study_org

        overrides = {}
        if args.contradiction_rate is not None:
            overrides["contradiction_rate"] = args.contradiction_rate
        if args.minority_correct_rate is not None:
            overrides["minority_correct_rate"] = args.minority_correct_rate
        org = synthetic_study_org(OrgSpec(size=args.generate, seed=args.seed, **overrides))

    study = run_study(org=org, llm=llm, candor=args.candor, max_turns=settings.max_turns)
    report = render_study_report(study, mode=mode)
    print(report)

    if args.write:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        path = settings.data_dir / "calibration_study.md"
        path.write_text(report, encoding="utf-8")
        print(f"\nWrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
