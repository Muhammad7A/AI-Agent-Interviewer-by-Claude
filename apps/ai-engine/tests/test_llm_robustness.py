"""Surviving a flaky model.

Twenty turns times twenty people is roughly four hundred model calls; some will fail.
Without retries the first blip ends someone's interview at turn twelve — which does not
just lose data, it spends the trust the candour experiment depends on.
"""
import random
import tempfile
import unittest
from pathlib import Path

from ai_engine.interview.driver import InterviewDriver
from ai_engine.interview.engine import InterviewEngine
from ai_engine.llm.retry import (
    LLMUnavailable,
    PermanentLLMError,
    RetryPolicy,
    TransientLLMError,
    call_with_retries,
    classify,
)
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.transcript.model import Transcript


class _Status(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


class ClassificationTest(unittest.TestCase):
    def test_rate_limit_and_overload_are_transient(self):
        for code in (429, 500, 502, 503, 504, 529):
            with self.subTest(code=code):
                self.assertIsInstance(classify(_Status(code)), TransientLLMError)

    def test_auth_and_bad_request_are_permanent(self):
        # Retrying a 401 twenty times just delays telling the operator their key is
        # wrong.
        for code in (400, 401, 403, 404, 422):
            with self.subTest(code=code):
                self.assertIsInstance(classify(_Status(code)), PermanentLLMError)

    def test_network_errors_are_transient(self):
        for exc in (TimeoutError("t"), ConnectionError("c"), OSError("o")):
            with self.subTest(exc=type(exc).__name__):
                self.assertIsInstance(classify(exc), TransientLLMError)

    def test_unknown_errors_are_retried_but_bounded(self):
        self.assertIsInstance(classify(ValueError("who knows")), TransientLLMError)


class RetryTest(unittest.TestCase):
    def setUp(self):
        self.slept: list[float] = []

    def _sleep(self, seconds: float) -> None:
        self.slept.append(seconds)

    def test_succeeds_after_transient_failures(self):
        calls = {"n": 0}

        def flaky() -> str:
            calls["n"] += 1
            if calls["n"] < 3:
                raise _Status(529)
            return "ok"

        result = call_with_retries(flaky, policy=RetryPolicy(attempts=4, jitter=False),
                                   sleep=self._sleep)
        self.assertEqual(result, "ok")
        self.assertEqual(calls["n"], 3)
        self.assertEqual(len(self.slept), 2)

    def test_backoff_is_exponential(self):
        def always_fail():
            raise _Status(503)

        with self.assertRaises(LLMUnavailable):
            call_with_retries(always_fail, policy=RetryPolicy(attempts=4, jitter=False,
                                                             base_delay=1.0),
                              sleep=self._sleep)
        self.assertEqual(self.slept, [1.0, 2.0, 4.0])

    def test_backoff_is_capped(self):
        policy = RetryPolicy(attempts=9, jitter=False, base_delay=1.0, max_delay=5.0)
        self.assertEqual(policy.delay_for(8), 5.0)

    def test_jitter_spreads_retries(self):
        # Without jitter, concurrent interviews retry in lockstep and re-create the
        # burst that caused the rate limit.
        policy = RetryPolicy(base_delay=4.0, jitter=True)
        rng = random.Random(0)
        delays = {policy.delay_for(3, rng) for _ in range(20)}
        self.assertGreater(len(delays), 5)

    def test_permanent_failure_is_not_retried(self):
        calls = {"n": 0}

        def bad_key():
            calls["n"] += 1
            raise _Status(401)

        with self.assertRaises(PermanentLLMError):
            call_with_retries(bad_key, policy=RetryPolicy(attempts=5), sleep=self._sleep)
        self.assertEqual(calls["n"], 1)
        self.assertEqual(self.slept, [])

    def test_exhaustion_reports_the_cause(self):
        def always_fail():
            raise _Status(503)

        with self.assertRaises(LLMUnavailable) as ctx:
            call_with_retries(always_fail, policy=RetryPolicy(attempts=2, jitter=False),
                              sleep=self._sleep)
        self.assertIn("2 attempt", str(ctx.exception))
        self.assertEqual(ctx.exception.attempts, 2)

    def test_keyboard_interrupt_is_never_swallowed(self):
        def interrupted():
            raise KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            call_with_retries(interrupted, sleep=self._sleep)


class _FlakyLLM:
    """Fails the first ``fail_times`` calls, then answers."""

    def __init__(self, fail_times: int) -> None:
        self.fail_times = fail_times
        self.calls = 0

    def complete(self, *, system, messages, max_tokens=1024, temperature=0.4) -> str:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise LLMUnavailable(4, _Status(529))
        return '{"utterance": "What happens next?", "should_close": false}'


class InterviewSurvivesFailureTest(unittest.TestCase):
    """A failed model call must not corrupt or lose the interview."""

    def _driver(self, llm) -> InterviewDriver:
        return InterviewDriver(
            engine=InterviewEngine(llm=llm, max_turns=14),
            transcript=Transcript(), objective="test",
            event_log=NullEventLog(), max_turns=14)

    def test_a_failed_turn_can_be_retried_without_double_counting(self):
        # The engine folds the previous answer into the state BEFORE calling the
        # model, so a failed call has already folded. Retrying must not fold again,
        # or one answer counts twice and coverage is corrupted.
        llm = _FlakyLLM(fail_times=0)
        driver = self._driver(llm)
        driver.next_question()
        driver.submit_answer("I keep a private spreadsheet, it takes hours each week.")

        llm.fail_times = llm.calls + 1              # the next call fails once
        with self.assertRaises(LLMUnavailable):
            driver.next_question()
        folded_after_failure = len(driver.state.history)

        driver.next_question()                      # retry, now succeeding
        self.assertEqual(len(driver.state.history), folded_after_failure,
                         "the same answer was folded twice on retry")
        self.assertEqual(folded_after_failure, 1)

    def test_the_answer_is_still_in_the_transcript_after_a_failure(self):
        llm = _FlakyLLM(fail_times=0)
        driver = self._driver(llm)
        driver.next_question()
        driver.submit_answer("The director's approval adds three days to everything.")
        llm.fail_times = llm.calls + 1
        with self.assertRaises(LLMUnavailable):
            driver.next_question()
        self.assertIn("director", driver.transcript.render())


class EmployeeSurfaceRecoveryTest(unittest.TestCase):
    """The participant sees a recoverable pause, not a dead end."""

    def test_stall_page_says_nothing_was_lost(self):
        from ai_engine.employee.views import temporarily_unavailable, unavailable

        stalled = temporarily_unavailable("tok")
        self.assertIn("Nothing you have said has been lost", stalled)
        self.assertIn("Try again", stalled)
        # It must not read like the dead-link page, or someone told their interview
        # is over will not come back.
        self.assertNotEqual(stalled, unavailable("") if False else unavailable())


if __name__ == "__main__":
    unittest.main()
