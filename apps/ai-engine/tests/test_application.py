"""The consultant's application layer, exercised headless — no web server.

These tests run the use-cases the way any surface (routes, CLI, a future API)
would: invite → start → answer → finish → tag → validate → report → release.
If orchestration is correct here, the routes cannot drift from it, because
they hold none of it.
"""
import tempfile
import unittest
from pathlib import Path

from ai_engine.application.service import (
    ANSWER_INACTIVE,
    ANSWER_RECORDED,
    ANSWER_TOO_LONG,
    ConsultantService,
)
from ai_engine.config import Runtime, Settings
from ai_engine.validation.model import Verdict


def _settings(data_dir: Path, **kw) -> Settings:
    return Settings(api_key=None, store_key=None, runtime=Runtime.DEV,
                    data_dir=data_dir, **kw)


class InterviewUseCaseTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)
        self.service = ConsultantService(_settings(self.data_dir))

    def _run_simulated(self) -> str:
        transcript_id = self.service.start("Dana Example", simulated=True)
        return self.service.finish(transcript_id)

    def test_a_simulated_interview_runs_to_a_stored_transcript(self):
        transcript_id = self._run_simulated()
        stored = self.service.load_transcript(transcript_id)
        self.assertIsNotNone(stored)
        self.assertTrue(stored.finalized)
        self.assertGreater(len(stored.segments), 2)
        self.assertNotIn("Dana Example", stored.render(),
                         "the real name must never reach the transcript")

    def test_a_manual_interview_advances_turn_by_turn(self):
        transcript_id = self.service.start("Eli")
        first = self.service.view(transcript_id)
        self.assertIsNotNone(first["question"])

        self.assertEqual(self.service.submit_answer(
            transcript_id, "I keep a private spreadsheet, honestly."), ANSWER_RECORDED)
        second = self.service.view(transcript_id)
        self.assertIn("private spreadsheet",
                      " ".join(s["text"] for s in second["segments"]))

        self.assertEqual(
            self.service.submit_answer(transcript_id, "x" * 50_000),
            ANSWER_TOO_LONG, "an oversized paste must not be recorded")
        self.assertEqual(self.service.submit_answer("no-such-id", "hi"),
                         ANSWER_INACTIVE)

    def test_finishing_twice_cannot_duplicate_the_transcript(self):
        transcript_id = self.service.start("Eli")
        self.assertIsNotNone(self.service.finish(transcript_id))
        self.assertIsNone(self.service.finish(transcript_id))

    def test_validation_flows_through_the_gate(self):
        transcript_id = self._run_simulated()
        tagging = self.service.tag(transcript_id)
        self.assertGreater(len(tagging.claims), 0)
        claim = tagging.claims[0]

        # The gate requires a reason to amend; without one the verdict is refused.
        self.assertFalse(self.service.record_verdict(
            transcript_id, claim.id, Verdict.AMENDED.value, reason=""))
        self.assertTrue(self.service.record_verdict(
            transcript_id, claim.id, Verdict.ACCEPTED.value))
        verdicts = self.service.verdicts(transcript_id)
        self.assertEqual(verdicts[claim.id].verdict, Verdict.ACCEPTED.value)

        findings = self.service.validated_findings(transcript_id)
        self.assertEqual([f.claim.id for f in findings], [claim.id])

    def test_reports_obey_the_firewall(self):
        transcript_id = self._run_simulated()
        tagging = self.service.tag(transcript_id)
        for claim in tagging.claims:
            self.service.record_verdict(transcript_id, claim.id,
                                        Verdict.ACCEPTED.value)

        consultant_md = self.service.consultant_report_markdown(transcript_id)
        self.assertIn("## Summary", consultant_md)
        # Saved under the at-rest policy like any testimony-derived artifact.
        report_files = list(self.data_dir.glob("*.report.md*"))
        self.assertEqual(len(report_files), 1)

        employer_md = self.service.employer_release_markdown([transcript_id])
        # One participant cannot satisfy k-anonymity: everything is suppressed,
        # and nothing verbatim reaches the employer's document.
        for claim in tagging.claims:
            self.assertNotIn(claim.statement, employer_md)

    def test_the_report_links_every_finding_to_its_verbatim_moment(self):
        transcript_id = self._run_simulated()
        tagging = self.service.tag(transcript_id)
        for claim in tagging.claims:
            self.service.record_verdict(transcript_id, claim.id,
                                        Verdict.ACCEPTED.value)
        claim = tagging.claims[0]
        segment_id = claim.evidence[0].ref.segment_id

        markdown = self.service.consultant_report_markdown(transcript_id)
        self.assertIn(f"/transcripts/{transcript_id}#seg-{segment_id}", markdown)
        self.assertIn("Grounded by construction", markdown)
        self.assertIn(str(tagging.report.total), markdown)

        page = self.service.consultant_report_page(transcript_id)
        self.assertEqual(page["grounding"]["proposed"], tagging.report.total)
        self.assertEqual(len(page["findings"]), len(tagging.claims))

    def test_dashboard_rows_count_claims_and_verdicts(self):
        self._run_simulated()
        rows = self.service.dashboard_rows()
        self.assertEqual(len(rows), 1)
        self.assertGreater(rows[0]["claims"], 0)
        self.assertEqual(rows[0]["validated"], 0)

    def test_live_interviews_survive_only_in_memory_until_finished(self):
        transcript_id = self.service.start("Eli")
        self.assertIn(transcript_id, [i["id"] for i in self.service.live_summary()])
        # A fresh service (a restarted process) has no live state — that is the
        # consent-preserving failure mode, not a bug.
        fresh = ConsultantService(_settings(self.data_dir))
        self.assertEqual(fresh.live_summary(), [])
        self.assertIsNone(fresh.view(transcript_id))


class PseudonymPersistenceTest(unittest.TestCase):
    def test_the_service_survives_a_restart_with_its_pseudonyms(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = ConsultantService(_settings(Path(tmp)))
            token = first.invite("Dana Example")
            invitation = first.list_invitations()[0]
            pseudonym = invitation.pseudonym

            restarted = ConsultantService(_settings(Path(tmp)))
            same_person = restarted.pseudonymizer.pseudonym("Dana Example")
            self.assertEqual(same_person, pseudonym,
                             "a restart must not re-pseudonymize the same person")
            self.assertEqual(restarted.list_invitations()[0].token, token)


if __name__ == "__main__":
    unittest.main()


class EngagementUseCaseTest(unittest.TestCase):
    """Engagements are the consultant's unit of work — named, grouped, reported."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.data_dir = Path(self._tmp.name)
        self.service = ConsultantService(_settings(self.data_dir))

    def test_interviews_group_under_a_named_engagement(self):
        engagement_id = self.service.create_engagement("Acme discovery")["id"]
        tid = self.service.start("Dana", simulated=True, engagement_id=engagement_id)
        self.service.finish(tid)
        rows = {r["id"]: r for r in self.service.dashboard_rows()}
        self.assertEqual(rows[tid]["engagement"], "Acme discovery")
        listing = self.service.list_engagements()
        acme = next(e for e in listing if e["id"] == engagement_id)
        self.assertEqual(acme["interviews"], 1)

    def test_resolving_a_name_reuses_the_engagement(self):
        first = self.service.resolve_engagement("Acme")
        second = self.service.resolve_engagement("acme")   # case-insensitive
        self.assertEqual(first, second)
        blank = self.service.resolve_engagement("  ")
        self.assertEqual(self.service.engagement_name(blank), "Ad-hoc interviews")

    def test_batch_intake_creates_one_invitation_per_line(self):
        tokens = self.service.invite_batch("Ana\nBo\n\nCitra\n")
        self.assertEqual(len(tokens), 3, "blank lines must be skipped")
        self.assertEqual(len(self.service.list_invitations()), 3)


class BatchIntakeWebTest(unittest.TestCase):
    def test_the_batch_route_creates_invitations(self):
        try:
            from fastapi.testclient import TestClient
        except Exception:
            self.skipTest("requires fastapi")
            return
        from ai_engine.webapp.app import create_app

        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(create_app(_settings(Path(tmp))))
            r = client.post("/invitations/batch",
                            data={"names": "Ana\nBo\nCitra"}, follow_redirects=False)
            self.assertEqual(r.status_code, 303)
            page = client.get("/invitations").text
            self.assertEqual(page.count("/i/"), 3)
