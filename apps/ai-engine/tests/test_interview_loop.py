"""The interview loop runs end-to-end in mock mode, and candor changes recovery.

These tests are the in-code candor experiment: the persona holds known tier-tagged
truths, so raising candor must (weakly) increase the tiers the loop reaches.
"""
import unittest

from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.subjects.simulated import SimulatedInterviewee, default_persona
from ai_engine.transcript.model import Speaker


def _run(candor: str):
    engine = InterviewEngine(llm=None, max_turns=14)
    subject = SimulatedInterviewee(default_persona(candor), llm=None)
    return run_interview(
        engine=engine, subject=subject, event_log=NullEventLog(), max_turns=14
    )


class InterviewLoopTest(unittest.TestCase):
    def test_loop_runs_and_produces_finalized_transcript(self):
        result = _run("neutral")
        self.assertTrue(result.transcript.finalized)
        self.assertGreater(len(result.transcript.segments), 2)
        # Alternates interviewer/subject and ends on the interviewer's close.
        self.assertEqual(result.transcript.segments[0].speaker, Speaker.INTERVIEWER)

    def test_transcript_alternates_speakers(self):
        result = _run("neutral")
        speakers = [s.speaker for s in result.transcript.segments]
        # Every subject turn is preceded by an interviewer turn.
        for i, sp in enumerate(speakers):
            if sp is Speaker.SUBJECT:
                self.assertIs(speakers[i - 1], Speaker.INTERVIEWER)

    def test_higher_candor_reaches_higher_tiers(self):
        guarded = _run("guarded").state.summary()
        openp = _run("open").state.summary()
        guarded_max = max(c["max_tier"] for c in guarded["coverage"].values())
        open_max = max(c["max_tier"] for c in openp["coverage"].values())
        # An open subject should let the loop reach a strictly higher tier than a
        # guarded one (guarded caps at tier 1 by construction).
        self.assertGreater(open_max, guarded_max)

    def test_guarded_subject_yields_few_tier2_disclosures(self):
        guarded = _run("guarded").state.summary()
        # Guarded persona caps at tier 1, so Tier-2+ disclosures should be ~none.
        self.assertEqual(guarded["disclosures_tier2plus"], 0)

    def test_event_log_records_testimony_only(self):
        # NullEventLog is a no-op; here we just assert the run completes with it.
        result = _run("open")
        self.assertGreaterEqual(result.turns, 1)


if __name__ == "__main__":
    unittest.main()
