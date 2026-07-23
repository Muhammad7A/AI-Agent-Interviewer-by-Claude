"""Command-line runner for the interview loop.

    python -m ai_engine.cli                      # live interview at the terminal
    python -m ai_engine.cli --simulated          # fully automated (persona vs engine)
    python -m ai_engine.cli --simulated --candor guarded

Runs in mock mode with no ANTHROPIC_API_KEY; set the key (and install the 'live'
extra) to use a real model for the interviewer and/or the simulated subject.
"""
from __future__ import annotations

import argparse
import sys

from .config import get_llm_client, load_settings
from .interview.engine import InterviewEngine
from .interview.session import DEFAULT_OBJECTIVE, run_interview
from .persistence.event_log import EventLog
from .subjects.human import HumanInterviewee
from .subjects.simulated import CANDOR_LEVELS, SimulatedInterviewee, default_persona
from .transcript.model import Transcript


def _print_exchange(speaker: str, text: str) -> None:
    if speaker == "interviewer":
        print(f"\n\033[1;36montora>\033[0m {text}")
    else:
        print(f"\033[0;33msubject>\033[0m {text}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ontora interview loop")
    parser.add_argument("--simulated", action="store_true", help="run against a simulated persona")
    parser.add_argument("--candor", choices=CANDOR_LEVELS, default="neutral",
                        help="simulated persona candor level (default: neutral)")
    parser.add_argument("--max-turns", type=int, default=None, help="override max interviewer turns")
    parser.add_argument("--objective", default=DEFAULT_OBJECTIVE, help="interview objective")
    parser.add_argument("--engagement-id", default="eng-demo")
    parser.add_argument("--tenant-id", default="tenant-demo")
    parser.add_argument("--no-log", action="store_true", help="do not write the testimony event log")
    args = parser.parse_args(argv)

    settings = load_settings()
    max_turns = args.max_turns or settings.max_turns
    llm = get_llm_client(settings)

    mode = "LIVE model" if llm is not None else "MOCK (no ANTHROPIC_API_KEY)"
    print(f"# Ontora interview loop — interviewer: {mode}")

    engine = InterviewEngine(llm=llm, max_turns=max_turns, temperature=settings.temperature)

    transcript = Transcript(engagement_id=args.engagement_id, tenant_id=args.tenant_id)
    transcript.interview_id = transcript.id

    if args.simulated:
        # The simulated subject uses the live model too when available.
        subject = SimulatedInterviewee(default_persona(args.candor), llm=llm)
        print(f"# Simulated subject: {subject.persona.name} "
              f"({subject.persona.role}), candor={args.candor}\n")
    else:
        subject = HumanInterviewee()
        print("# Live interview. Type your answers; Ctrl-D to end early.\n")

    event_log = None if args.no_log else EventLog(settings.data_dir, transcript.id)

    result = run_interview(
        engine=engine,
        subject=subject,
        objective=args.objective,
        transcript=transcript,
        event_log=event_log,
        max_turns=max_turns,
        emit=_print_exchange,
    )

    print("\n" + "=" * 60)
    summary = result.state.summary()
    print(f"Turns: {result.turns}   "
          f"Areas covered (Tier 2+): {summary['areas_covered']}/{summary['areas_total']}   "
          f"Tier-2+ disclosures: {summary['disclosures_tier2plus']}")
    for area, cov in summary["coverage"].items():
        print(f"  - {area:16s} {cov['level']:9s} max_tier={cov['max_tier']}")
    if event_log is not None:
        print(f"\nTestimony log: {event_log.path}")
    print(f"Transcript segments: {len(result.transcript.segments)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
