"""The employee interview surface.

The tests that matter most are the negative ones. This app exists so an employee can be
alone with the tool, and its value depends entirely on what it *cannot* do: reach the
workspace, read anyone's testimony (including, after submission, their own), learn a
name, or keep answers that were withdrawn.
"""
import re
import tempfile
import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
    _HAS_CLIENT = True
except Exception:  # pragma: no cover
    _HAS_CLIENT = False

from ai_engine.config import Runtime, Settings
from ai_engine.persistence.invitations import (
    InvitationStatus,
    InvitationStore,
    new_token,
)


class InvitationStoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = InvitationStore(Path(self._tmp.name))

    def test_tokens_are_unguessable_and_unique(self):
        a, b = new_token(), new_token()
        self.assertNotEqual(a, b)
        self.assertGreater(len(a), 24)

    def test_create_and_read_back(self):
        inv = self.store.create(pseudonym="P-abc123")
        self.assertEqual(self.store.get(inv.token).pseudonym, "P-abc123")
        self.assertTrue(inv.is_open)

    def test_unknown_token_is_none(self):
        self.assertIsNone(self.store.get("nope"))

    def test_traversal_tokens_are_refused(self):
        for bad in ("../secret", "a/b", "..", ".hidden", ""):
            with self.subTest(token=bad):
                self.assertIsNone(self.store.get(bad))

    def test_status_transitions(self):
        inv = self.store.create(pseudonym="P-1")
        self.store.set_status(inv.token, InvitationStatus.COMPLETED,
                              transcript_id="txn-1")
        again = self.store.get(inv.token)
        self.assertTrue(again.is_finished)
        self.assertFalse(again.is_open)
        self.assertEqual(again.transcript_id, "txn-1")


@unittest.skipUnless(_HAS_CLIENT, "requires fastapi and httpx")
class EmployeeSurfaceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)
        self.settings = Settings(api_key=None, store_key=None, runtime=Runtime.DEV,
                                 data_dir=self.data_dir)
        from ai_engine.employee.app import create_employee_app

        self.client = TestClient(create_employee_app(self.settings))
        self.invitations = InvitationStore(self.data_dir)
        self.invitation = self.invitations.create(pseudonym="P-abc123")
        self.token = self.invitation.token

    def _begin(self) -> None:
        self.client.post(f"/i/{self.token}/begin", follow_redirects=False)

    def _answer(self, text: str) -> None:
        self.client.post(f"/i/{self.token}/answer", data={"answer": text},
                         follow_redirects=False)

    # -- the guarantee is shown before anything is asked -------------------
    def test_welcome_states_the_promise_before_the_first_question(self):
        page = self.client.get(f"/i/{self.token}").text
        self.assertIn("Your employer does not see your answers", page)
        self.assertIn("only person who mentions something", page)
        self.assertIn("you can stop", page.lower())
        self.assertIn("Begin", page)
        # No question has been asked yet.
        self.assertNotIn("Continue", page)

    def test_interview_asks_and_records(self):
        self._begin()
        page = self.client.get(f"/i/{self.token}").text
        self.assertIn("Question 1", page)
        self._answer("I keep a private spreadsheet because the tool is unusable.")
        page = self.client.get(f"/i/{self.token}").text
        self.assertIn("private spreadsheet", page)  # their own words, shown back

    def test_participant_is_never_asked_for_identifying_information(self):
        # The precise property is the absence of an input field, not the absence of
        # the word "name" — the page legitimately *promises* that the name is not
        # attached, which is the guarantee, not a request for it.
        for path, setup in ((f"/i/{self.token}", lambda: None),
                            (f"/i/{self.token}", self._begin)):
            setup()
            page = self.client.get(path).text
            with self.subTest(page=path):
                self.assertNotIn("<input", page.lower(),
                                 "the interview surface must collect no fields but the answer")
                for field in ("participant", "email", "employee", "fullname"):
                    self.assertNotIn(f'name="{field}"', page.lower())
        # The only input of any kind is the answer box.
        page = self.client.get(f"/i/{self.token}").text
        self.assertEqual(page.lower().count("<textarea"), 1)

    # -- what this app must NOT be able to do ------------------------------
    def test_no_workspace_route_exists(self):
        for path in ("/", "/engagement", "/invitations",
                     "/transcripts/txn-1", "/transcripts/txn-1/review",
                     "/transcripts/txn-1/report", "/transcripts/txn-1/employer",
                     "/interviews/new"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_another_participant_token_is_isolated(self):
        other = self.invitations.create(pseudonym="P-other")
        self._begin()
        self._answer("My own confidential answer about the night shift.")
        page = self.client.get(f"/i/{other.token}").text
        self.assertNotIn("night shift", page)
        self.assertNotIn("P-abc123", page)

    def test_unknown_and_finished_tokens_are_indistinguishable(self):
        unknown = self.client.get("/i/does-not-exist")
        self.invitations.set_status(self.token, InvitationStatus.COMPLETED)
        finished = self.client.get(f"/i/{self.token}")
        self.assertEqual(unknown.status_code, finished.status_code)
        self.assertEqual(unknown.text, finished.text)

    def test_completed_token_cannot_be_reused(self):
        self._begin()
        self.client.post(f"/i/{self.token}/finish", follow_redirects=False)
        self.assertEqual(self.client.post(f"/i/{self.token}/begin",
                                         follow_redirects=False).status_code, 404)

    # -- submission and withdrawal ----------------------------------------
    def test_finishing_stores_the_transcript_and_marks_the_invitation(self):
        from ai_engine.persistence.transcript_store import TranscriptStore

        self._begin()
        self._answer("The director's approval adds days to everything.")
        r = self.client.post(f"/i/{self.token}/finish")
        self.assertIn("Submitted", r.text)
        invitation = self.invitations.get(self.token)
        self.assertEqual(invitation.status, InvitationStatus.COMPLETED.value)
        stored = TranscriptStore(self.data_dir).load(invitation.transcript_id)
        self.assertTrue(stored.finalized)
        self.assertIn("director", stored.render())

    def test_withdrawal_stores_absolutely_nothing(self):
        # The right to withdraw is only real if withdrawing leaves nothing behind.
        self._begin()
        self._answer("Something I regret saying about my manager.")
        r = self.client.post(f"/i/{self.token}/withdraw")
        self.assertIn("Discarded", r.text)
        self.assertEqual(self.invitations.get(self.token).status,
                         InvitationStatus.WITHDRAWN.value)
        transcripts = self.data_dir / "transcripts"
        stored = list(transcripts.iterdir()) if transcripts.exists() else []
        self.assertEqual(stored, [], "a withdrawn interview must not be stored")
        # And the words themselves are nowhere in the data directory.
        for path in self.data_dir.rglob("*"):
            if path.is_file():
                with self.subTest(path=str(path)):
                    self.assertNotIn("regret saying",
                                     path.read_text(encoding="utf-8", errors="ignore"))

    def test_answers_cannot_be_added_after_withdrawal(self):
        self._begin()
        self.client.post(f"/i/{self.token}/withdraw")
        self.assertEqual(self.client.post(f"/i/{self.token}/answer",
                                          data={"answer": "more"},
                                          follow_redirects=False).status_code, 404)

    def test_testimony_is_escaped(self):
        self._begin()
        self._answer("<script>alert(1)</script> is what I use")
        page = self.client.get(f"/i/{self.token}").text
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;", page)

    def test_production_guard_applies_here_too(self):
        from ai_engine.config import ConfigurationError
        from ai_engine.employee.app import create_employee_app

        with self.assertRaises(ConfigurationError):
            create_employee_app(Settings(api_key=None, store_key=None,
                                         runtime=Runtime.PRODUCTION))


@unittest.skipUnless(_HAS_CLIENT, "requires fastapi and httpx")
class ConsultantInvitesTest(unittest.TestCase):
    """The consultant side of the handoff."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)
        from ai_engine.webapp.app import create_app

        self.settings = Settings(api_key=None, store_key=None, runtime=Runtime.DEV,
                                 data_dir=self.data_dir)
        self.client = TestClient(create_app(self.settings))

    def test_creating_an_invitation_pseudonymises_the_name(self):
        self.client.post("/invitations/new", data={"participant": "Dana Example"},
                         follow_redirects=False)
        page = self.client.get("/invitations").text
        self.assertNotIn("Dana Example", page)
        self.assertRegex(page, r"P-[0-9a-f]{6}")
        self.assertIn("/i/", page)

    def test_invitation_appears_with_pending_status(self):
        self.client.post("/invitations/new", data={"participant": "Eli"},
                         follow_redirects=False)
        self.assertIn("pending", self.client.get("/invitations").text)


if __name__ == "__main__":
    unittest.main()
