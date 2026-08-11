"""Entailment: the second gate. Grounding proves the quote is real; entailment
proves the quote supports the claim. This closes the 'real quote, fabricated
claim' hole that grounding alone cannot catch.
"""
import unittest

from ai_engine.evidence.entailment import (
    Entailment,
    HeuristicEntailmentChecker,
    apply_entailment,
)
from ai_engine.evidence.grounding import ground_proposal
from ai_engine.evidence.model import RawProposal
from ai_engine.evidence.tagger import EvidenceTagger
from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.subjects.simulated import SimulatedInterviewee, default_persona
from ai_engine.transcript.model import Speaker, Transcript


CHATGPT_QUOTE = "I use my personal ChatGPT to draft the summaries."


def _grounded(statement: str, quote: str, transcript: Transcript):
    claim, reason = ground_proposal(
        RawProposal("observation", statement, quote=quote, tier=2), transcript
    )
    assert reason == "grounded", reason
    return claim


def _transcript(line: str) -> Transcript:
    t = Transcript()
    t.append(Speaker.INTERVIEWER, "Tell me about your tools.")
    t.append(Speaker.SUBJECT, line)
    t.finalize()
    return t


class HeuristicCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = HeuristicEntailmentChecker()

    def test_aligned_claim_is_supported(self):
        r = self.checker.check("Uses personal ChatGPT to draft summaries.", CHATGPT_QUOTE)
        self.assertIs(r.verdict, Entailment.SUPPORTED)

    def test_escalation_to_accusation_is_not_supported(self):
        # The dangerous case: a benign quote turned into a serious accusation.
        r = self.checker.check("The employee admitted leaking confidential customer data.",
                               CHATGPT_QUOTE)
        self.assertIs(r.verdict, Entailment.NOT_SUPPORTED)

    def test_unrelated_claim_is_not_supported(self):
        r = self.checker.check("The office coffee machine is broken.", CHATGPT_QUOTE)
        self.assertIs(r.verdict, Entailment.NOT_SUPPORTED)


class ApplyEntailmentTest(unittest.TestCase):
    def test_real_quote_wrong_claim_is_rejected(self):
        # Both claims quote the SAME real sentence and both GROUND fine...
        t = _transcript(CHATGPT_QUOTE)
        good = _grounded("Uses personal ChatGPT to draft summaries.", CHATGPT_QUOTE, t)
        bad = _grounded("The employee is leaking confidential data to fraud rings.",
                        CHATGPT_QUOTE, t)
        kept, rejected = apply_entailment([good, bad], t, HeuristicEntailmentChecker())
        # ...but only the supported one survives the second gate.
        self.assertEqual([c.id for c in kept], [good.id])
        self.assertEqual(len(rejected), 1)
        self.assertIs(rejected[0].claim, bad)


class TaggingIntegrationTest(unittest.TestCase):
    def test_combined_confabulation_rate_counts_entailment_rejects(self):
        # A tagger whose entailment checker rejects everything => confabulation 1.0.
        class RejectAll:
            def check(self, statement, quote):
                from ai_engine.evidence.entailment import EntailmentResult
                return EntailmentResult(Entailment.NOT_SUPPORTED, "test", "heuristic")

        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(default_persona("open"), llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        tagging = EvidenceTagger(llm=None, entailment=RejectAll()).tag(result.transcript)
        self.assertEqual(len(tagging.claims), 0)                 # all dropped by gate 2
        self.assertGreater(len(tagging.entailment_rejected), 0)
        self.assertEqual(tagging.confabulation_rate, 1.0)        # all counted as fabrication

    def test_normal_pipeline_still_clean(self):
        # The honest mock claims (statement contains the quote) all pass entailment.
        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(default_persona("open"), llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        tagging = EvidenceTagger(llm=None).tag(result.transcript)
        self.assertGreater(len(tagging.claims), 0)
        self.assertEqual(len(tagging.entailment_rejected), 0)
        self.assertEqual(tagging.confabulation_rate, 0.0)


if __name__ == "__main__":
    unittest.main()
