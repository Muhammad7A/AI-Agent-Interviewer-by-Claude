"""Run the evaluation suite.

    python -m ai_engine.eval            # mock mode (deterministic, offline)
    python -m ai_engine.eval --write    # also write the report to the data dir

With ANTHROPIC_API_KEY set, the interviewer, subject, and tagger all use the live
model — this is the first *real* measurement of the system.

Exit code is 0 if all gates pass, 1 otherwise — so this doubles as a CI gate.
"""
from __future__ import annotations

import argparse
import sys

from ..config import get_llm_client, load_settings
from .report import render_eval_report
from .runner import run_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora evaluation harness")
    parser.add_argument("--write", action="store_true", help="write the report to the data dir")
    args = parser.parse_args(argv)

    settings = load_settings()
    llm = get_llm_client(settings)
    mode = "LIVE model" if llm is not None else "MOCK (deterministic, no API key)"

    suite = run_suite(llm=llm)
    report = render_eval_report(suite, mode=mode)
    print(report)

    if args.write:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        path = settings.data_dir / "eval_report.md"
        path.write_text(report, encoding="utf-8")
        print(f"\nWrote {path}")

    return 0 if suite.passed else 1


if __name__ == "__main__":
    sys.exit(main())
