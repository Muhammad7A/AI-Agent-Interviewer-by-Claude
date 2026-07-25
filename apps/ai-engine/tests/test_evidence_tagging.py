"""Evidence tagging: grounding, the confabulation filter, and the evidence-first
invariant.
"""
import unittest

from ai_engine.evidence.grounding import ground_proposal, ground_proposals
from ai_engine.evidence.model import (
    Claim,
    ClaimStatus,
    ClaimType,
    EvidenceError,
    GroundedEvidence,
    RawProposal,
)
from ai_engine.evidence.tagger import EvidenceTagger
from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.subjects.simulated import SimulatedInterviewee, default_persona
from ai_engine.transcript.model import EvidenceRef, Speaker, Transcript


def _transcript_with(subject_line: str, question: str = "How does the work get done?") -> Transcript:
    t = Transcript()
    t.append(Speaker.INTERVIEWER, question)
    t.append(Speaker.SUBJECT, subject_line)
    t.finalize()
    return t


class GroundingTest(unittest.TestCase):
    def test_exact_quote_grounds_to_precise_span(self):
        t = _transcript_with("I keep a private spreadsheet because the dashboard is unusable.")
        prop = RawProposal(claim_type="workaround", statement="Keeps a private spreadsheet.",
                           quote="private spreadsheet", tier=2)
        claim, reason = ground_proposal(prop, t)
        self.assertEqual(reason, "grounded")
        self.assertIsNotNone(claim)
        self.assertEqual(claim.evidence[0].match_kind, "exact")
        self.assertEqual(claim.evidence[0].resolve(t), "private spreadsheet")

    def test_flexible_match_tolerates_whitespace_and_case(self):
        t = _transcript_with("The real  bottleneck is the DIRECTOR's approval step.")
        # Quote differs in spacing and case but is otherwise the subject's words.
        prop = RawProposal(claim_type="friction", statement="Director approval is the bottleneck.",
                           quote="real bottleneck is the director's", tier=3)
        claim, reason = ground_proposal(prop, t)
        self.assertEqual(reason, "grounded")
        self.assertEqual(claim.evidence[0].match_kind, "flexible")
        # The resolved span is real source text, not the model's version.
        self.assertIn("DIRECTOR", claim.evidence[0].resolve(t))

    def test_fabricated_quote_is_rejected(self):
        # The confabulation filter: a quote not in the transcript never grounds.
        t = _transcript_with("I keep a private spreadsheet.")
        prop = RawProposal(claim_type="friction",
                           statement="The CEO is planning layoffs.",
                           quote="the CEO told me layoffs are coming", tier=4)
        claim, reason = ground_proposal(prop, t)
        self.assertIsNone(claim)
        self.assertEqual(reason, "quote_not_found")

    def test_quote_from_interviewer_is_rejected(self):
        # A quote that only matches the interviewer's question is not evidence (F8).
        t = _transcript_with("Yeah.", question="Is the director's approval the bottleneck?")
        prop = RawProposal(claim_type="friction", statement="Director is the bottleneck.",
                           quote="the director's approval the bottleneck", tier=3)
        claim, reason = ground_proposal(prop, t)
        self.assertIsNone(claim)
        self.assertEqual(reason, "cited_interviewer_not_subject")

    def test_empty_quote_is_rejected(self):
        t = _transcript_with("Anything.")
        claim, reason = ground_proposal(RawProposal("observation", "x", quote="  "), t)
        self.assertIsNone(claim)
        self.assertEqual(reason, "empty_quote")

    def test_confabulation_rate_over_a_batch(self):
        t = _transcript_with("I rebuild the weekly report by hand every week.")
        proposals = [
            RawProposal("wasted_effort", "Rebuilds report by hand.",
                        quote="rebuild the weekly report by hand", tier=2),
            RawProposal("friction", "Fabricated claim.",
                        quote="a quote that does not exist", tier=4),
        ]
        result = ground_proposals(proposals, t)
        self.assertEqual(len(result.claims), 1)
        self.assertEqual(result.report.total, 2)
        self.assertEqual(result.report.ungrounded, 1)
        self.assertAlmostEqual(result.report.confabulation_rate, 0.5)


class HardenedGroundingTest(unittest.TestCase):
    """Real models re-emit true quotes with different punctuation; those must still
    ground. Paraphrases must not."""

    def test_curly_apostrophe_still_grounds(self):
        t = _transcript_with("The director's approval step adds three days.")  # straight '
        prop = RawProposal("friction", "Director approval is slow.",
                            quote="director’s approval step", tier=3)  # curly '
        claim, reason = ground_proposal(prop, t)
        self.assertEqual(reason, "grounded")
        self.assertEqual(claim.evidence[0].match_kind, "normalized")
        # Resolves to the REAL source span (straight apostrophe), not the model's.
        self.assertIn("director's approval step", claim.evidence[0].resolve(t))

    def test_em_dash_and_case_still_ground(self):
        t = _transcript_with("I rebuild the report by hand — about four hours.")  # em dash
        prop = RawProposal("wasted_effort", "Manual rebuild.",
                            quote="BY HAND - ABOUT FOUR HOURS", tier=2)  # hyphen + caps
        claim, reason = ground_proposal(prop, t)
        self.assertEqual(reason, "grounded")

    def test_extra_whitespace_still_grounds(self):
        t = _transcript_with("I keep a private spreadsheet because it is faster.")
        prop = RawProposal("workaround", "Private spreadsheet.",
                            quote="private    spreadsheet", tier=2)  # collapsed spaces
        claim, reason = ground_proposal(prop, t)
        self.assertEqual(reason, "grounded")

    def test_partial_word_match_is_rejected(self):
        # Found by the fuzz audit: without word-boundary guards, the fabricated
        # quote "vendor I" matched "vendor Ignores", grounding a claim on half a
        # word. A quote must align to whole words in the source.
        t = _transcript_with("I avoid the supplier portal because that vendor ignores each deadline.")
        prop = RawProposal("observation", "fabricated", quote="vendor I", tier=2)
        claim, reason = ground_proposal(prop, t)
        self.assertIsNone(claim)
        self.assertEqual(reason, "quote_not_found")

    def test_word_fragment_of_a_real_word_is_rejected(self):
        t = _transcript_with("I keep a private spreadsheet for the weekly numbers.")
        for fragment in ("spread", "sheet", "priva"):
            with self.subTest(fragment=fragment):
                claim, _ = ground_proposal(
                    RawProposal("observation", "x", quote=fragment, tier=2), t)
                self.assertIsNone(claim, f"{fragment!r} should not ground")

    def test_boundary_guard_does_not_reject_punctuation_led_quotes(self):
        # The guard must not over-constrain: a quote starting with punctuation is
        # still legitimate and must ground.
        t = _transcript_with("It is fine — pretty standard stuff, nothing new.")
        claim, reason = ground_proposal(
            RawProposal("observation", "x", quote="— pretty standard", tier=2), t)
        self.assertIsNotNone(claim, reason)

    def test_hyphenated_word_part_still_grounds(self):
        t = _transcript_with("My week is repetitive rules-based copying between systems.")
        claim, reason = ground_proposal(
            RawProposal("observation", "x", quote="rules-based copying", tier=2), t)
        self.assertIsNotNone(claim, reason)

    def test_paraphrase_still_rejected(self):
        # The filter must not go soft: changing the WORDS is still confabulation.
        t = _transcript_with("I keep a private spreadsheet.")
        prop = RawProposal("workaround", "Maintains a spreadsheet.",
                            quote="I maintain a personal spreadsheet", tier=2)
        claim, reason = ground_proposal(prop, t)
        self.assertIsNone(claim)
        self.assertEqual(reason, "quote_not_found")


class EvidenceFirstInvariantTest(unittest.TestCase):
    def test_claim_without_evidence_is_forbidden(self):
        with self.assertRaises(EvidenceError):
            Claim(id="clm-x", claim_type=ClaimType.OBSERVATION, statement="unsourced",
                  evidence=(), speaker=Speaker.SUBJECT, tier=1)

    def test_claim_is_always_only_proposed(self):
        t = _transcript_with("I keep a private spreadsheet.")
        claim, _ = ground_proposal(
            RawProposal("workaround", "spreadsheet", quote="private spreadsheet", tier=2), t
        )
        self.assertEqual(claim.status, ClaimStatus.PROPOSED)


class EndToEndTaggingTest(unittest.TestCase):
    def test_mock_tagging_over_simulated_interview_is_grounded_and_clean(self):
        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(default_persona("open"), llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        tagging = EvidenceTagger(llm=None).tag(result.transcript)

        # The open persona disclosed real Tier-2+ truths, so we get claims.
        self.assertGreater(len(tagging.claims), 0)
        # The mock tagger is honest: every claim grounds, zero confabulation.
        self.assertEqual(tagging.report.confabulation_rate, 0.0)
        # Every claim resolves to real subject text and carries evidence.
        for claim in tagging.claims:
            self.assertGreaterEqual(len(claim.evidence), 1)
            self.assertEqual(claim.speaker, Speaker.SUBJECT)
            resolved = claim.evidence[0].resolve(result.transcript)
            self.assertTrue(resolved)


if __name__ == "__main__":
    unittest.main()
