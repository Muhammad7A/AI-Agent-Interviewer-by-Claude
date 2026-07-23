"""Validation gate invariants, the auto-sim policy, and the report generator."""
import unittest

from ai_engine.evidence.grounding import ground_proposal
from ai_engine.evidence.model import ClaimType, RawProposal
from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.report.generator import render_markdown_report
from ai_engine.subjects.simulated import SimulatedInterviewee, default_persona
from ai_engine.transcript.model import EvidenceRef, Speaker, Transcript
from ai_engine.validation.gate import AutoValidator, ValidationGate, validate_claims
from ai_engine.validation.model import (
    Correction,
    ValidatedFinding,
    ValidationDecision,
    ValidationError,
    Validator,
    Verdict,
)


def _grounded_claim(subject_line: str, ctype: str = "workaround", quote: str | None = None, tier: int = 2):
    t = Transcript()
    t.append(Speaker.INTERVIEWER, "How does the work get done?")
    t.append(Speaker.SUBJECT, subject_line)
    t.finalize()
    claim, reason = ground_proposal(
        RawProposal(ctype, "stmt", quote=quote or subject_line, tier=tier), t
    )
    assert reason == "grounded", reason
    return claim, t


_V = Validator(id="val-1", display_name="Reviewer")


class ValidationInvariantTest(unittest.TestCase):
    def test_decision_requires_reviewed_evidence(self):
        with self.assertRaises(ValidationError):
            ValidationDecision(id="v", claim_id="c", verdict=Verdict.ACCEPTED,
                               validator=_V, reviewed_evidence=())

    def test_reject_requires_reason(self):
        claim, _ = _grounded_claim("I keep a private spreadsheet.")
        gate = ValidationGate(_V)
        with self.assertRaises(ValidationError):
            gate.decide(claim, Verdict.REJECTED, reason="   ")

    def test_amend_requires_correction(self):
        claim, _ = _grounded_claim("I keep a private spreadsheet.")
        gate = ValidationGate(_V)
        with self.assertRaises(ValidationError):
            gate.decide(claim, Verdict.AMENDED, reason="needs fixing", correction=None)

    def test_only_amend_may_carry_correction(self):
        claim, _ = _grounded_claim("I keep a private spreadsheet.")
        gate = ValidationGate(_V)
        with self.assertRaises(ValidationError):
            gate.decide(claim, Verdict.ACCEPTED, correction=Correction(new_tier=3))

    def test_accept_records_reviewed_evidence(self):
        claim, _ = _grounded_claim("I keep a private spreadsheet.")
        gate = ValidationGate(_V)
        decision = gate.decide(claim, Verdict.ACCEPTED)
        self.assertEqual(decision.verdict, Verdict.ACCEPTED)
        self.assertEqual(len(decision.reviewed_evidence), len(claim.evidence))


class ValidatedFindingProjectionTest(unittest.TestCase):
    def test_amendment_overrides_effective_values(self):
        claim, _ = _grounded_claim("I keep a private spreadsheet.", tier=2)
        gate = ValidationGate(_V)
        decision = gate.decide(
            claim, Verdict.AMENDED, reason="tighten",
            correction=Correction(new_statement="Maintains a private spreadsheet.", new_tier=3),
        )
        f = ValidatedFinding(claim=claim, decision=decision)
        self.assertEqual(f.statement, "Maintains a private spreadsheet.")
        self.assertEqual(f.tier, 3)
        self.assertTrue(f.is_reportable)

    def test_rejected_is_not_reportable(self):
        claim, _ = _grounded_claim("I keep a private spreadsheet.")
        gate = ValidationGate(_V)
        decision = gate.decide(claim, Verdict.REJECTED, reason="not useful")
        self.assertFalse(ValidatedFinding(claim=claim, decision=decision).is_reportable)


class AutoValidatorTest(unittest.TestCase):
    def test_auto_rejects_low_tier_and_accepts_high(self):
        auto = AutoValidator()
        high, _ = _grounded_claim("The director's approval adds three days.", "friction", tier=3)
        low, _ = _grounded_claim("We use Slack and email mostly here.", "observation", tier=0)
        self.assertEqual(auto.decide(high)[0], Verdict.ACCEPTED)
        self.assertEqual(auto.decide(low)[0], Verdict.REJECTED)

    def test_auto_amends_prefixed_statement(self):
        # The mock tagger prefixes statements with "[type] ..."; auto tightens it.
        t = Transcript()
        t.append(Speaker.INTERVIEWER, "q")
        seg = t.append(Speaker.SUBJECT, "I rebuild the report by hand every week.")
        t.finalize()
        from ai_engine.evidence.model import Claim, GroundedEvidence
        claim = Claim(id="clm-1", claim_type=ClaimType.WASTED_EFFORT,
                      statement="[wasted_effort] I rebuild the report by hand every week.",
                      evidence=(GroundedEvidence(EvidenceRef(seg.id, 0, len(seg.text)),
                                                 seg.text, "exact"),),
                      speaker=Speaker.SUBJECT, tier=2)
        verdict, _, correction = AutoValidator().decide(claim)
        self.assertEqual(verdict, Verdict.AMENDED)
        self.assertEqual(correction.new_statement, "I rebuild the report by hand every week.")


class ReportTest(unittest.TestCase):
    def _findings(self, candor="open"):
        from ai_engine.evidence.tagger import EvidenceTagger
        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(default_persona(candor), llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        claims = EvidenceTagger(llm=None).tag(result.transcript).claims
        gate = ValidationGate(AutoValidator.VALIDATOR)
        findings = validate_claims(gate, claims, AutoValidator().decide)
        return result.transcript, findings, result.state

    def test_report_contains_validated_findings_with_provenance(self):
        transcript, findings, state = self._findings("open")
        md = render_markdown_report(
            transcript=transcript, findings=findings, objective="obj",
            engagement_id="eng-x", interview_id=transcript.id,
            validator_kind="auto-sim", validator_name="Auto",
            coverage_summary=state.summary(),
        )
        self.assertIn("Organizational Assessment", md)
        # Every reportable finding's evidence quote appears verbatim in the report.
        for f in findings:
            if f.is_reportable:
                quote = f.claim.evidence[0].resolve(transcript)
                self.assertIn(quote, md)

    def test_report_excludes_rejected_content(self):
        transcript, findings, state = self._findings("open")
        md = render_markdown_report(
            transcript=transcript, findings=findings, objective="obj",
            engagement_id="eng-x", interview_id=transcript.id,
            validator_kind="auto-sim", validator_name="Auto",
        )
        rejected = [f for f in findings if f.verdict is Verdict.REJECTED]
        for f in rejected:
            self.assertNotIn(f.statement, md)

    def test_report_flags_simulated_validation(self):
        transcript, findings, state = self._findings("neutral")
        md = render_markdown_report(
            transcript=transcript, findings=findings, objective="obj",
            engagement_id="eng-x", interview_id=transcript.id,
            validator_kind="auto-sim", validator_name="Auto",
        )
        self.assertIn("DEMO ONLY", md)


if __name__ == "__main__":
    unittest.main()
