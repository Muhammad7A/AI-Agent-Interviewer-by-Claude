"""The interview strategy: does the engine act on what it already knows?

Each test pins one behaviour the engine previously collected a signal for and then
ignored. The livelock test is the most important: it fails on a policy that soothes a
guarded subject and then keeps soothing.
"""
import unittest

from ai_engine.evidence.tagger import EvidenceTagger
from ai_engine.interview.engine import InterviewEngine, assess_locally
from ai_engine.interview.session import run_interview
from ai_engine.interview.state import InterviewState
from ai_engine.interview.strategy import Intent, InterviewStrategy
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.subjects.simulated import SimulatedInterviewee, default_persona
from ai_engine.transcript.model import Speaker

DEFLECTION = "I'd rather not get into that, honestly."
VAGUE = "It's mostly fine, I guess — nothing jumps out."
CONCRETE = "I keep a private spreadsheet because the dashboard is unusable, every week."


def _state_after(answers: list[str], *, area: str = "workarounds", tier: int = 2):
    """Drive a state through answers as the engine would, without an interview."""
    state = InterviewState(objective="test")
    strategy = InterviewStrategy(max_turns=14)
    move = strategy.decide(state)
    state.turn_count += 1
    state.note_question(area, tier)
    for answer in answers:
        assessment = assess_locally(answer, state)
        state.record_answer(
            areas_touched=assessment.areas_touched,
            tier_reached=assessment.tier_reached,
            got_disclosure=assessment.got_substantive_disclosure,
            specificity=assessment.specificity,
            candor_signal=assessment.candor_signal,
            answer=answer,
        )
        move = strategy.decide(state)
        state.turn_count += 1
        state.note_question(move.target_area, move.target_tier)
    return state, strategy, move


class AssessmentTest(unittest.TestCase):
    """A refusal and a non-answer are different failures and need different responses."""

    def test_deflection_reads_as_guarded(self):
        state = InterviewState(objective="t")
        state.note_question("friction", 3)
        a = assess_locally(DEFLECTION, state)
        self.assertEqual(a.candor_signal, "guarded")

    def test_vague_answer_is_not_guarded(self):
        # Conflating these makes the interviewer retreat when it should probe — and
        # caused a livelock: soothe, get vagueness, soothe again, forever.
        state = InterviewState(objective="t")
        state.note_question("friction", 3)
        a = assess_locally(VAGUE, state)
        self.assertEqual(a.candor_signal, "neutral")
        self.assertEqual(a.specificity, "vague")

    def test_concrete_answer_credits_the_targeted_tier(self):
        state = InterviewState(objective="t")
        state.note_question("workarounds", 2)
        a = assess_locally(CONCRETE, state)
        self.assertEqual(a.specificity, "concrete")
        self.assertEqual(a.tier_reached, 2)
        self.assertTrue(a.got_substantive_disclosure)


class StrategyBehaviourTest(unittest.TestCase):
    def test_opens_before_asking_anything_costly(self):
        move = InterviewStrategy().decide(InterviewState(objective="t"))
        self.assertIs(move.intent, Intent.OPEN)
        self.assertEqual(move.target_tier, 1)

    def test_vague_answer_triggers_specificity_conversion_on_the_same_area(self):
        _state, _strategy, move = _state_after([VAGUE], area="workarounds", tier=2)
        self.assertIs(move.intent, Intent.CONVERT_SPECIFICITY)
        self.assertEqual(move.target_area, "workarounds")

    def test_specificity_conversion_names_the_topic(self):
        # A probe that just says "give me an example" makes the subject decide what is
        # relevant; one that repeats the topic's words gets an instance.
        from ai_engine.interview.engine import _SPECIFICITY_BY_AREA

        self.assertIn("instead", _SPECIFICITY_BY_AREA["workarounds"])
        self.assertIn("stall", _SPECIFICITY_BY_AREA["bottlenecks"])

    def test_refusal_moves_to_a_different_area(self):
        _state, _strategy, move = _state_after([DEFLECTION], area="friction", tier=3)
        self.assertIs(move.intent, Intent.DE_ESCALATE)
        self.assertNotEqual(move.target_area, "friction")
        self.assertEqual(move.target_tier, 1)

    def test_never_de_escalates_twice_running(self):
        # Two soothing questions in a row is not reassurance, it is an interview that
        # has given up.
        _state, _strategy, move = _state_after([DEFLECTION, DEFLECTION],
                                               area="friction", tier=3)
        self.assertIsNot(move.intent, Intent.DE_ESCALATE)

    def test_returns_to_a_deferred_area_later(self):
        state, strategy, _move = _state_after([DEFLECTION], area="friction", tier=3)
        self.assertGreater(state.coverage["friction"].deferred_until_turn,
                           state.turn_count - 1)
        # After the deferral window the area competes normally again.
        state.turn_count += 5
        gains = {a: strategy for a in ()}  # (no-op, keeps the intent explicit)
        from ai_engine.interview.strategy import _information_gain

        self.assertGreater(_information_gain("friction", state), 0.5)

    def test_gives_up_on_an_area_that_stays_vague(self):
        # It may still convert specificity elsewhere — what it must not do is keep
        # grinding the same unproductive topic.
        state, _s, move = _state_after([VAGUE, VAGUE, VAGUE], area="workarounds", tier=2)
        self.assertGreaterEqual(state.coverage["workarounds"].vague_streak, 2)
        self.assertFalse(
            move.intent is Intent.CONVERT_SPECIFICITY
            and move.target_area == "workarounds",
            "kept probing an area that produced nothing three times")

    def test_an_exhausted_area_loses_priority(self):
        from ai_engine.interview.strategy import _information_gain

        state, _s, _move = _state_after([VAGUE, VAGUE], area="workarounds", tier=2)
        fresh = _information_gain("ai_opportunity", state)
        stale = _information_gain("workarounds", state)
        self.assertGreater(fresh, stale)

    def test_prefers_untouched_areas_over_covered_ones(self):
        state = InterviewState(objective="t")
        state.turn_count = 3
        state.coverage["workarounds"].level = "covered"
        state.coverage["workarounds"].max_tier = 2
        move = InterviewStrategy().decide(state)
        self.assertNotEqual(move.target_area, "workarounds")

    def test_closes_when_nothing_is_worth_asking(self):
        state = InterviewState(objective="t")
        state.turn_count = 99  # budget exhausted
        self.assertIs(InterviewStrategy(max_turns=14).decide(state).intent, Intent.CLOSE)


class NoLivelockTest(unittest.TestCase):
    def test_a_persistently_vague_subject_does_not_loop(self):
        """The regression this whole module was built around.

        A policy that treats vagueness as a refusal asks the same soothing question
        forever and elicits nothing.
        """
        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(default_persona("guarded"), llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        questions = [s.text for s in result.transcript.segments
                     if s.speaker is Speaker.INTERVIEWER]
        self.assertGreater(len(set(questions)), 3,
                           "the interviewer repeated itself instead of moving on")

    def test_an_open_subject_still_yields_findings(self):
        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(default_persona("open"), llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        claims = EvidenceTagger(llm=None).tag(result.transcript).claims
        self.assertGreaterEqual(len(claims), 4)


class LiveDirectiveTest(unittest.TestCase):
    def test_the_move_is_handed_to_the_model_as_an_instruction(self):
        from ai_engine.interview.engine import _directive
        from ai_engine.interview.strategy import Move

        text = _directive(Move(Intent.CONVERT_SPECIFICITY, "workarounds", 2, "vague"))
        self.assertIn("specificity_conversion", text)
        self.assertIn("Do NOT move on", text)

        text = _directive(Move(Intent.DE_ESCALATE, "process_reality", 1, "guarded"))
        self.assertIn("Do NOT push", text)


if __name__ == "__main__":
    unittest.main()
