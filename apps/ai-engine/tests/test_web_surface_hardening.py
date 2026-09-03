"""Hardening of the two web surfaces.

Each test pins a failure mode an unattended interview could actually hit: one
transient model failure bricking the consultant's loop, an oversized paste
wedging a participant's interview permanently, a withdrawal that lied about a
completed interview, a route parameter escaping the transcript directory, and a
bad model id surfacing at the participant's first question instead of startup.
"""
import tempfile
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
    _HAS_CLIENT = True
except Exception:  # pragma: no cover
    _HAS_CLIENT = False

from ai_engine.config import ModelUnavailable, Runtime, Settings, preflight_model
from ai_engine.llm.retry import LLMUnavailable
from ai_engine.persistence.invitations import InvitationStatus, InvitationStore
from ai_engine.persistence.transcript_store import TranscriptStore


def _settings(data_dir: Path, **kw) -> Settings:
    return Settings(api_key=None, store_key=None, runtime=Runtime.DEV,
                    data_dir=data_dir, **kw)


class _FailingLLM:
    def complete(self, **kwargs):
        raise LLMUnavailable("the model is down", None)


class _FlakyEngine:
    """An engine whose model dies exactly once — on the second turn.

    Installed as a subclass so the route behaviour — pause, recover, continue —
    is what is under test, against the real interview engine otherwise.
    """

    def __init__(self, *args, **kwargs):
        import ai_engine.interview.engine as engine_mod

        self._inner = engine_mod.InterviewEngine(*args, **kwargs)
        self._calls = 0

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def next_turn(self, **kwargs):
        self._calls += 1
        if self._calls in (2, 3):
            # Down for the answer's follow-up AND the first retry; back after.
            raise LLMUnavailable("the model is down", None)
        return self._inner.next_turn(**kwargs)


@unittest.skipUnless(_HAS_CLIENT, "requires fastapi and httpx")
class ConsultantModelFailureTest(unittest.TestCase):
    """One transient model failure must pause the interview, not brick it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)
        import ai_engine.webapp.app as webapp_app

        self._module = webapp_app
        self._original_client = webapp_app.get_llm_client
        self._original_engine = webapp_app.InterviewEngine
        self.addCleanup(self._restore)

    def _restore(self):
        self._module.get_llm_client = self._original_client
        self._module.InterviewEngine = self._original_engine

    def test_start_survives_a_dead_model(self):
        self._module.get_llm_client = lambda s: _FailingLLM()
        client = TestClient(self._module.create_app(_settings(self.data_dir)))
        r = client.post("/interviews/new", data={"participant": "Dana", "mode": "manual"},
                        follow_redirects=False)
        self.assertEqual(r.status_code, 503)
        self.assertIn("temporarily unavailable", r.text)

    def test_a_failed_next_question_pauses_and_recovers(self):
        import ai_engine.interview.engine as engine_mod

        self._module.InterviewEngine = _FlakyEngine
        client = TestClient(self._module.create_app(_settings(self.data_dir)))
        r = client.post("/interviews/new", data={"participant": "Dana", "mode": "manual"},
                        follow_redirects=False)
        interview_id = r.headers["location"].rsplit("/", 1)[-1]

        # The next model call fails, but the answer was already recorded.
        r = client.post(f"/interviews/{interview_id}/answer",
                        data={"answer": "I keep a private spreadsheet, honestly."},
                        follow_redirects=False)
        self.assertEqual(r.status_code, 303)

        # The interview page reports a recoverable pause, not a 500.
        page = client.get(f"/interviews/{interview_id}")
        self.assertEqual(page.status_code, 503)
        self.assertIn("intact", page.text)

        # The model is back (transient failure): the same page continues —
        # nothing re-entered, nothing asked twice.
        page = client.get(f"/interviews/{interview_id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("private spreadsheet", page.text)


@unittest.skipUnless(_HAS_CLIENT, "requires fastapi and httpx")
class AnswerLengthCapTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)

    def test_an_oversized_consultant_answer_is_refused(self):
        from ai_engine.webapp.app import create_app

        client = TestClient(create_app(_settings(self.data_dir, max_answer_chars=100)))
        r = client.post("/interviews/new", data={"participant": "D", "mode": "manual"},
                        follow_redirects=False)
        interview_id = r.headers["location"].rsplit("/", 1)[-1]
        r = client.post(f"/interviews/{interview_id}/answer",
                        data={"answer": "word " * 40}, follow_redirects=False)
        self.assertEqual(r.status_code, 413)
        page = client.get(f"/interviews/{interview_id}")
        self.assertNotIn("word " * 10, page.text, "the oversized answer was recorded")

    def test_an_oversized_participant_answer_is_refused(self):
        from ai_engine.employee.app import create_employee_app

        invitations = InvitationStore(self.data_dir)
        token = invitations.create(pseudonym="P-abc123def456").token
        client = TestClient(create_employee_app(
            _settings(self.data_dir, max_answer_chars=50)))
        client.post(f"/i/{token}/begin", follow_redirects=False)
        r = client.post(f"/i/{token}/answer", data={"answer": "word " * 20})
        self.assertEqual(r.status_code, 413)
        self.assertIn("not recorded", r.text)


@unittest.skipUnless(_HAS_CLIENT, "requires fastapi and httpx")
class WithdrawAfterCompleteTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)
        self.invitations = InvitationStore(self.data_dir)
        self.token = self.invitations.create(pseudonym="P-abc123def456").token
        from ai_engine.employee.app import create_employee_app

        self.client = TestClient(create_employee_app(_settings(self.data_dir)))

    def test_a_completed_interview_cannot_be_withdrawn_into_a_lie(self):
        self.client.post(f"/i/{self.token}/begin", follow_redirects=False)
        self.client.post(f"/i/{self.token}/answer",
                         data={"answer": "I keep a private spreadsheet, honestly."})
        self.client.post(f"/i/{self.token}/finish")

        r = self.client.post(f"/i/{self.token}/withdraw")
        self.assertEqual(r.status_code, 409)
        self.assertIn("already complete", r.text)
        self.assertEqual(self.invitations.get(self.token).status,
                         InvitationStatus.COMPLETED.value)
        transcript_id = self.invitations.get(self.token).transcript_id
        self.assertTrue((self.data_dir / "transcripts").exists())


class TranscriptIdTraversalTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = TranscriptStore(Path(self._tmp.name))

    def test_separator_ids_are_refused(self):
        for bad in ("../escape", "a/b", "a\\b", ".hidden", "..", ""):
            with self.subTest(transcript_id=bad):
                with self.assertRaises(ValueError):
                    self.store.load(bad)
                with self.assertRaises(ValueError):
                    self.store.exists(bad)

    @unittest.skipUnless(_HAS_CLIENT, "requires fastapi and httpx")
    def test_a_traversal_route_parameter_is_a_404_not_an_escape(self):
        from ai_engine.webapp.app import create_app

        client = TestClient(create_app(_settings(Path(self._tmp.name))))
        r = client.get("/transcripts/%5C..%5C..%5Csecrets")
        self.assertEqual(r.status_code, 404)


class PreflightAtStartupTest(unittest.TestCase):
    def test_mock_mode_preflights_as_mock(self):
        settings = Settings(api_key=None, store_key=None, runtime=Runtime.DEV)
        self.assertEqual(preflight_model(settings), "mock")

    def test_an_unreachable_model_fails_preflight_with_the_model_named(self):
        import ai_engine.llm.client as llm_client_mod

        class _Dead:
            def __init__(self, **kwargs):
                pass

            def complete(self, **kwargs):
                raise LLMUnavailable("404 not found")

        original = llm_client_mod.AnthropicClient
        llm_client_mod.AnthropicClient = _Dead
        try:
            settings = Settings(api_key="sk-test", store_key="k", runtime=Runtime.DEV)
            with self.assertRaises(ModelUnavailable) as ctx:
                preflight_model(settings)
            self.assertIn("did not answer", str(ctx.exception))
        finally:
            llm_client_mod.AnthropicClient = original


if __name__ == "__main__":
    unittest.main()
