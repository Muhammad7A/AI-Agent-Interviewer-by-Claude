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
from .persistence.transcript_store import TranscriptStore
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
    parser.add_argument("--no-log", action="store_true", help="do not write event logs")
    parser.add_argument("--no-tag", action="store_true", help="skip post-interview evidence tagging")
    parser.add_argument("--validate", action="store_true",
                        help="validate findings by hand (default: auto-sim reviewer)")
    args = parser.parse_args(argv)

    settings = load_settings()
    # Refuse to serve real interviews from an unsafe configuration (mock cognition
    # or plaintext testimony). No-op in dev.
    settings.assert_deployable()
    max_turns = args.max_turns or settings.max_turns
    llm = get_llm_client(settings)

    print(f"# Ontora interview loop — {settings.posture_banner()}")
    if not settings.is_production and llm is None:
        print("#   ⚠ mock cognition: answers are scripted, not a real interview")

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

    # Persist the transcript, so every EvidenceRef in the report stays resolvable
    # after this process exits. Without this the provenance chain dies at exit.
    if not args.no_log:
        store = TranscriptStore(settings.data_dir, settings.cipher())
        path = store.save(result.transcript)
        print(f"Transcript stored: {path}"
              + ("" if store.encrypted else "  ⚠ PLAINTEXT (dev only)"))

    if not args.no_tag:
        claims = _tag(result.transcript, llm, settings, args)
        findings = _validate(result.transcript, claims, settings, args)
        _report(result.transcript, findings, result.state, args, settings)
    return 0


def _tag(transcript, llm, settings, args):
    """Post-interview: extract evidence-tagged claim proposals from the transcript."""
    from .evidence.tagger import EvidenceTagger
    from .evidence.prompts import TAGGER_PROMPT_VERSION

    tagging = EvidenceTagger(llm=llm).tag(transcript)
    report = tagging.report

    print("\n" + "-" * 60)
    print(f"PROPOSED FINDINGS (evidence-tagged) — {len(tagging.claims)} verified, "
          f"{report.ungrounded} unsourced, {len(tagging.entailment_rejected)} unsupported, "
          f"confabulation rate {tagging.confabulation_rate:.0%}")
    for claim in tagging.claims:
        ev = claim.evidence[0]
        resolved = ev.resolve(transcript)
        print(f"\n  • ({claim.claim_type.value}, tier {claim.tier}, {claim.status.value})")
        print(f"    {claim.statement}")
        print(f"    └─ evidence [{ev.ref.segment_id} {ev.ref.start}:{ev.ref.end} "
              f"{ev.match_kind}] → \"{resolved}\"")
    for rej in report.rejected:
        print(f"\n  ✗ UNSOURCED ({rej.reason}): \"{rej.proposal.quote[:60]}...\"")
    for erej in tagging.entailment_rejected:
        print(f"\n  ✗ UNSUPPORTED ({erej.reason}): \"{erej.claim.statement[:60]}...\"")

    if not args.no_log:
        interp = EventLog(settings.data_dir, transcript.id, layer="interpretation")
        for claim in tagging.claims:
            ev = claim.evidence[0]
            interp.emit(
                "ClaimProposed",
                claim_id=claim.id,
                claim_type=claim.claim_type.value,
                tier=claim.tier,
                status=claim.status.value,
                statement=claim.statement,
                evidence_segment_id=ev.ref.segment_id,
                evidence_span=[ev.ref.start, ev.ref.end],
                match_kind=ev.match_kind,
                prompt_version=TAGGER_PROMPT_VERSION,
            )
        interp.emit(
            "GroundingReport",
            total=report.total,
            grounded=report.grounded,
            ungrounded=report.ungrounded,
            confabulation_rate=round(report.confabulation_rate, 4),
        )
        print(f"\nInterpretation log: {interp.path}")
    return tagging.claims


def _validate(transcript, claims, settings, args):
    """The AI-proposes / human-validates gate."""
    from .validation.gate import AutoValidator, ValidationGate, validate_claims

    event_log = None if args.no_log else EventLog(
        settings.data_dir, transcript.id, layer="validation"
    )

    if args.validate:
        validator = _interactive_validator_identity()
        gate = ValidationGate(validator, event_log)
        print("\n" + "-" * 60)
        print("VALIDATION — review each proposed finding: [a]ccept / [r]eject / "
              "[e]dit. Evidence is shown first.")
        findings = validate_claims(gate, claims, _interactive_decide(transcript))
    else:
        auto = AutoValidator()
        gate = ValidationGate(auto.VALIDATOR, event_log)
        findings = validate_claims(gate, claims, auto.decide)
        print("\n" + "-" * 60)
        print("VALIDATION — auto-sim reviewer (NOT human; demo only). "
              "Pass --validate to review by hand.")

    from .validation.model import Verdict
    for f in findings:
        mark = {"accepted": "✓", "amended": "✎", "rejected": "✗"}[f.verdict.value]
        print(f"  {mark} {f.verdict.value:8s} {f.statement[:70]}")
    if event_log is not None:
        print(f"\nValidation log: {event_log.path}")
    return findings


def _report(transcript, findings, state, args, settings) -> None:
    from .report.generator import render_markdown_report

    kind = "consultant" if args.validate else "auto-sim"
    name = "Human consultant" if args.validate else "Auto-Sim Reviewer (demo)"
    md = render_markdown_report(
        transcript=transcript,
        findings=findings,
        objective=args.objective,
        engagement_id=args.engagement_id,
        interview_id=transcript.id,
        validator_kind=kind,
        validator_name=name,
        coverage_summary=state.summary(),
    )
    if args.no_log:
        print("\n" + "=" * 60 + "\n" + md)
        return
    path = settings.data_dir / f"{transcript.id}.report.md"
    path.write_text(md, encoding="utf-8")
    print(f"\nReport: {path}")


def _interactive_validator_identity():
    from .validation.model import Validator

    name = input("\nValidator name> ").strip() or "consultant"
    return Validator(id=f"val-{name.lower().replace(' ', '-')}", display_name=name)


def _interactive_decide(transcript):
    from .validation.model import Correction, Verdict

    def decide(claim):
        ev = claim.evidence[0]
        print(f"\n  ({claim.claim_type.value}, tier {claim.tier})")
        print(f"  Statement: {claim.statement}")
        print(f"  Evidence:  \"{ev.resolve(transcript)}\"")
        choice = input("  [a]ccept / [r]eject / [e]dit> ").strip().lower()
        if choice.startswith("r"):
            reason = input("  reason> ").strip() or "rejected by reviewer"
            return Verdict.REJECTED, reason, None
        if choice.startswith("e"):
            new_stmt = input("  corrected statement> ").strip()
            reason = input("  reason> ").strip() or "amended by reviewer"
            return Verdict.AMENDED, reason, Correction(new_statement=new_stmt or None)
        return Verdict.ACCEPTED, "", None

    return decide


if __name__ == "__main__":
    sys.exit(main())
