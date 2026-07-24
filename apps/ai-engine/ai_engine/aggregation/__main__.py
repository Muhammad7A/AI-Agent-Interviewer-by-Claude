"""Run a whole organization's interviews and aggregate them.

    python -m ai_engine.aggregation           # mock, offline
    python -m ai_engine.aggregation --write    # also write the org report

Interviews each persona in the demo org, tags the findings, then fuses them into
an org-level picture — corroboration and contradictions. With ANTHROPIC_API_KEY
set, the whole chain uses the live model.
"""
from __future__ import annotations

import argparse
import sys

from ..config import get_llm_client, load_settings
from ..evidence.tagger import EvidenceTagger
from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..persistence.event_log import NullEventLog
from ..subjects.simulated import SimulatedInterviewee
from .aggregator import aggregate
from .model import participant_finding_from_claim
from .relation import make_relation_checker
from .report import render_org_report
from .scenario import northwind_org


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora multi-interview aggregation")
    parser.add_argument("--write", action="store_true", help="write the org report to the data dir")
    parser.add_argument("--candor", default="open", help="persona candor for the demo org")
    args = parser.parse_args(argv)

    settings = load_settings()
    llm = get_llm_client(settings)
    mode = "LIVE model" if llm is not None else "MOCK (deterministic, no API key)"
    print(f"# Ontora aggregation — {mode}")

    personas = northwind_org(args.candor)
    all_findings = []
    for persona in personas:
        engine = InterviewEngine(llm=llm, max_turns=settings.max_turns)
        subject = SimulatedInterviewee(persona, llm=llm)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=settings.max_turns)
        claims = EvidenceTagger(llm=llm).tag(result.transcript).claims
        for claim in claims:
            all_findings.append(participant_finding_from_claim(
                claim, result.transcript,
                participant_id=persona.name, participant_name=persona.name,
            ))
        print(f"  interviewed {persona.name} ({persona.role}) → {len(claims)} findings")

    aggregation = aggregate(all_findings, make_relation_checker(llm))
    report = render_org_report(aggregation, org_name="Northwind", interview_count=len(personas))

    print("\n" + "=" * 60)
    print(report)

    if args.write:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        path = settings.data_dir / "org_report.md"
        path.write_text(report, encoding="utf-8")
        print(f"\nWrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
