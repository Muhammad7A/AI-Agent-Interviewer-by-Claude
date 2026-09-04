"""Regressions for the review findings that had no test.

Each case here failed before the change it guards. They are grouped by the
property at risk rather than by module, because that is what a reader needs to
know when one of them goes red.
"""
from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from ai_engine.aggregation.model import (AggregatedFinding, MemberRelation,
                                         ParticipantFinding, Relation)
from ai_engine.confidence.scorer import UNKNOWN_COHORT_CAP, score_member
from ai_engine.evidence.entailment import (Entailment, HeuristicEntailmentChecker,
                                           _severe_stem, apply_entailment)
from ai_engine.evidence.model import Claim, ClaimType, GroundedEvidence
from ai_engine.persistence.crypto import NullCipher, cipher_available
from ai_engine.persistence.event_log import (EventLog, TamperedEventLog,
                                             TruncatedEventLog, head_path,
                                             read_events)
from ai_engine.persistence.reports import report_path
from ai_engine.privacy.identity import (CorruptIdentityState, Pseudonymizer,
                                        restricted_dir)
from ai_engine.transcript.model import EvidenceRef, Speaker, Transcript


def _cipher():
    """A real cipher, or ``None`` when cryptography is unavailable here."""
    if not cipher_available():
        return None
    from ai_engine.persistence.crypto import FernetCipher, generate_key
    return FernetCipher(generate_key())


class EvidenceRefIsSelfResolvingTest(unittest.TestCase):
    """The cross-transcript guard must not be defeatable by omission.

    ``transcript_id`` had a default of ``""`` and the guard read
    ``if self.transcript_id and ...``, so any ref built without one skipped the
    check entirely — the exact behaviour the field was added to prevent.
    """

    def test_transcript_id_is_required(self):
        with self.assertRaises(TypeError):
            EvidenceRef(segment_id="seg-1", start=0, end=3)  # type: ignore[call-arg]

    def test_resolving_against_another_transcript_is_refused(self):
        a = Transcript(id="txn-alice")
        a.append(Speaker.SUBJECT, "My manager approves within a day.")
        b = Transcript(id="txn-bob")
        seg = b.append(Speaker.SUBJECT, "I falsified the quarterly numbers.")
        ref = EvidenceRef(segment_id=seg.id, start=0, end=10, transcript_id="txn-bob")
        self.assertEqual(ref.resolve(b), "I falsifie")
        with self.assertRaises(ValueError):
            ref.resolve(a)


class EventLogTruncationTest(unittest.TestCase):
    """Per-line authentication cannot see a record that is no longer there."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.cipher = _cipher() or NullCipher()
        log = EventLog(self.dir, "txn-1", cipher=self.cipher)
        for i in range(5):
            log.emit("TurnRecorded", n=i)
        self.path = Path(log.path)
        self.lines = self.path.read_text(encoding="utf-8").splitlines()
        self.head = head_path(self.path).read_text(encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, lines):
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_intact_log_reads(self):
        self.assertEqual(len(read_events(self.path, self.cipher)), 5)

    def test_truncation_is_detected(self):
        self._write(self.lines[:3])
        with self.assertRaises(TruncatedEventLog):
            read_events(self.path, self.cipher)

    def test_deleting_a_middle_record_is_detected(self):
        self._write(self.lines[:2] + self.lines[3:])
        with self.assertRaises(TamperedEventLog):
            read_events(self.path, self.cipher)

    def test_reordering_is_detected(self):
        self._write([self.lines[0], self.lines[2], self.lines[1],
                     self.lines[3], self.lines[4]])
        with self.assertRaises(TamperedEventLog):
            read_events(self.path, self.cipher)

    def test_a_crash_between_append_and_head_is_tolerated(self):
        """The one direction that is damage rather than tampering."""
        self._write(self.lines[:4])
        self.assertEqual(len(read_events(self.path, self.cipher)), 4)

    def test_appending_behind_the_head_is_detected(self):
        self._write(self.lines + [self.lines[-1]])
        with self.assertRaises(TamperedEventLog):
            read_events(self.path, self.cipher)

    def test_unchained_legacy_logs_still_read(self):
        """A log written before the chain existed must not become unreadable."""
        legacy = self.dir / "legacy.testimony.jsonl"
        legacy.write_text(
            "\n".join(json.dumps({"layer": "testimony", "event": "E", "n": i})
                      for i in range(3)) + "\n", encoding="utf-8")
        self.assertEqual(len(read_events(legacy, None)), 3)


class IdentityStateTest(unittest.TestCase):
    """The file that re-identifies every participant is the most sensitive one."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_restricted_directory_is_owner_only(self):
        path = restricted_dir(self.dir)
        if os.name == "nt":  # pragma: no cover - POSIX modes only
            self.skipTest("POSIX modes are not meaningful on Windows")
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700)

    def test_state_survives_restart(self):
        first = Pseudonymizer.load_or_create(self.dir)
        alias = first.pseudonym("dana@corp.com")
        first.save_state(self.dir)
        self.assertEqual(Pseudonymizer.load_or_create(self.dir).pseudonym("dana@corp.com"),
                         alias)

    def test_state_is_encrypted_when_a_key_is_configured(self):
        cipher = _cipher()
        if cipher is None:
            self.skipTest("cryptography is not importable in this environment")
        p = Pseudonymizer.load_or_create(self.dir, cipher)
        p.pseudonym("dana@corp.com")
        path = p.save_state(self.dir, cipher)
        self.assertTrue(path.name.endswith(".enc"))
        self.assertNotIn(b"dana@corp.com", path.read_bytes())
        # ...and round-trips.
        self.assertEqual(
            Pseudonymizer.load_or_create(self.dir, cipher).pseudonym("dana@corp.com"),
            p.pseudonym("dana@corp.com"))

    def test_production_refuses_plaintext_identity_state(self):
        previous = os.environ.get("ONTORA_ENV")
        os.environ["ONTORA_ENV"] = "production"
        try:
            with self.assertRaises(RuntimeError):
                Pseudonymizer().save_state(self.dir, NullCipher())
        finally:
            if previous is None:
                os.environ.pop("ONTORA_ENV", None)
            else:
                os.environ["ONTORA_ENV"] = previous

    def test_corrupt_state_raises_rather_than_re_salting(self):
        """Silently starting fresh would re-issue every pseudonym."""
        p = Pseudonymizer.load_or_create(self.dir)
        p.pseudonym("dana@corp.com")
        p.save_state(self.dir)
        (restricted_dir(self.dir) / "engagement.json").write_text("{not json",
                                                                 encoding="utf-8")
        with self.assertRaises(CorruptIdentityState):
            Pseudonymizer.load_or_create(self.dir)

    def test_no_temporary_file_is_left_behind(self):
        p = Pseudonymizer.load_or_create(self.dir)
        p.pseudonym("dana@corp.com")
        p.save_state(self.dir)
        leftovers = [q.name for q in restricted_dir(self.dir).iterdir()
                     if q.name.startswith(".")]
        self.assertEqual(leftovers, [], "atomic write left a temp file behind")


class EntailmentFollowupTest(unittest.TestCase):
    def setUp(self):
        self.checker = HeuristicEntailmentChecker()

    def test_ordinary_words_are_not_accusations(self):
        """"forgot" is the most ordinary thing an interviewee says about a missed step."""
        for word in ("forgot", "forget", "forgetting", "forgive",
                     "confidential", "confidentiality"):
            with self.subTest(word=word):
                self.assertIsNone(_severe_stem(word))

    def test_real_accusations_still_fire(self):
        for word in ("forgery", "forged", "fraud", "embezzled", "harassment"):
            with self.subTest(word=word):
                self.assertIsNotNone(_severe_stem(word))

    def test_a_forgot_claim_is_no_longer_rejected_as_an_accusation(self):
        result = self.checker.check(
            "The employee forgot to send the report last week.",
            "I forgot to send the report last week.")
        self.assertIs(result.verdict, Entailment.SUPPORTED, result.reason)

    def test_every_piece_of_evidence_is_checked(self):
        """A second quote must not ride in behind the first."""
        t = Transcript()
        t.append(Speaker.INTERVIEWER, "q")
        good = t.append(Speaker.SUBJECT, "Approvals take three days.")
        bad = t.append(Speaker.SUBJECT, "The weather is fine.")
        t.finalize()
        def ev(seg):
            return GroundedEvidence(
                EvidenceRef(seg.id, 0, len(seg.text), t.id), seg.text, "exact")
        # Only the SECOND piece supports the claim; the first does not. Reading
        # evidence[0] alone would reject a claim that is in fact supported.
        claim = Claim(id="clm-1", claim_type=ClaimType.OBSERVATION,
                      statement="Approvals take three days.",
                      evidence=(ev(bad), ev(good)),
                      speaker=Speaker.SUBJECT, tier=2)
        kept, rejected = apply_entailment([claim], t, self.checker)
        self.assertEqual(len(kept), 1, f"rejected: {[r.reason for r in rejected]}")


class CorroborationIndependenceTest(unittest.TestCase):
    """Agreement inside one team is not five independent observations."""

    @staticmethod
    def _finding(cohorts):
        members = [ParticipantFinding(
            participant_id=f"P{i}", participant_name=f"P{i}", claim_type="friction",
            statement="approvals take three days", tier=2,
            evidence_quote="approvals take three days", segment_id="s",
            transcript_id="t", cohort=c) for i, c in enumerate(cohorts)]
        relations = [MemberRelation(a, b, Relation.AGREE)
                     for a in range(len(members)) for b in range(a + 1, len(members))]
        return AggregatedFinding(topic_id="t1", claim_type="friction", label="l",
                                 members=members, contradictions=[], relations=relations)

    def test_one_team_scores_below_five_departments(self):
        same = score_member(self._finding(["finance"] * 5), 0).value
        spread = score_member(self._finding([f"team{i}" for i in range(5)]), 0).value
        self.assertLess(same, spread)

    def test_unknown_cohorts_are_capped(self):
        capped = score_member(self._finding([None] * 12), 0)
        detail = next(c for c in capped.contributions if c.name == "corroboration").detail
        self.assertIn("capped", detail)
        uncapped = score_member(self._finding([f"t{i}" for i in range(12)]), 0)
        self.assertLess(capped.value, uncapped.value)

    def test_the_cap_is_the_documented_value(self):
        many = score_member(self._finding([None] * 20), 0)
        detail = next(c for c in many.contributions if c.name == "corroboration").detail
        self.assertIn(f"{UNKNOWN_COHORT_CAP:.2f}", detail)

    def test_a_single_source_is_still_one_voice(self):
        one = score_member(self._finding(["finance"]), 0)
        detail = next(c for c in one.contributions if c.name == "corroboration").detail
        self.assertIn("single source", detail)


class ReportStemTest(unittest.TestCase):
    def test_a_separator_in_the_stem_is_refused(self):
        for stem in ("../escape", "a/b", "a\\b", "", ".hidden"):
            with self.subTest(stem=stem):
                with self.assertRaises(ValueError):
                    report_path(Path("/tmp"), stem)

    def test_an_ordinary_stem_is_accepted(self):
        self.assertTrue(str(report_path(Path("/tmp"), "txn-1.report")).endswith(".md"))


if __name__ == "__main__":
    unittest.main()
