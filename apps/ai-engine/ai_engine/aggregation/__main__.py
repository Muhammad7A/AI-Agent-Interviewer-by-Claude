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
from ..privacy import Pseudonymizer, ReleasePolicy, release, render_release_report
from ..subjects.simulated import SimulatedInterviewee
from .aggregator import aggregate
from .model import participant_finding_from_claim
from .relation import make_relation_checker
from .scenario import northwind_org


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Groundwork multi-interview aggregation")
    parser.add_argument("--write", action="store_true", help="write the org report to the data dir")
    parser.add_argument("--candor", default="open", help="persona candor for the demo org")
    parser.add_argument("--audience", choices=("consultant", "employer"),
                        default="employer",
                        help="who the report is for; the employer view is redacted "
                             "through the privacy firewall (default: employer)")
    parser.add_argument("--k", type=int, default=2,
                        help="k-anonymity threshold for the employer view")
    parser.add_argument("--salt", default=None,
                        help="engagement salt for pseudonyms (default: random)")
    args = parser.parse_args(argv)

    settings = load_settings()
    llm = get_llm_client(settings)
    mode = "LIVE model" if llm is not None else "MOCK (deterministic, no API key)"
    print(f"# Groundwork aggregation — {mode}")

    # Pseudonymize at ingest: the real name enters here and goes no further, so
    # every downstream artifact carries only a per-engagement pseudonym (Art. X).
    pseudonymizer = Pseudonymizer(args.salt) if args.salt else Pseudonymizer()

    personas = northwind_org(args.candor)
    all_findings = []
    for persona in personas:
        engine = InterviewEngine(llm=llm, max_turns=settings.max_turns)
        subject = SimulatedInterviewee(persona, llm=llm)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=settings.max_turns)
        claims = EvidenceTagger(llm=llm).tag(result.transcript).claims
        pseudonym = pseudonymizer.pseudonym(persona.name)
        for claim in claims:
            all_findings.append(participant_finding_from_claim(
                claim, result.transcript,
                participant_id=pseudonym, participant_name=pseudonym,
            ))
        print(f"  interviewed {persona.name} → {pseudonym} ({persona.role}), "
              f"{len(claims)} findings")

    aggregation = aggregate(all_findings, make_relation_checker(llm))

    policy = (ReleasePolicy.for_consultant() if args.audience == "consultant"
              else ReleasePolicy.for_employer(k_anonymity=args.k))
    package = release(aggregation, policy=policy)
    report = render_release_report(package, org_name="Northwind",
                                   interview_count=len(personas))

    print("\n" + "=" * 60)
    print(report)

    if args.write:
        from ..persistence.reports import save_report

        cipher = settings.cipher()
        path = save_report(settings.data_dir, f"org_report.{args.audience}", report,
                           cipher)
        print(f"\nWrote {path}"
              + ("" if cipher.protects_at_rest else "  ⚠ PLAINTEXT (dev only)"))
        # The re-identification key is written separately — its own restricted
        # directory, never beside the deliverables — never with the report.
        from ..privacy.identity import restricted_dir

        key_path = pseudonymizer.write_key(
            restricted_dir(settings.data_dir) / "identity-key.RESTRICTED.json")
        print(f"Wrote {key_path}  (RESTRICTED — consultant only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
