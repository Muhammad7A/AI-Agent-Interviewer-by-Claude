"""Encryption at rest for the event logs — closing a half-truth.

The transcript store was encrypted and the event logs were not, while the docs said
"encryption at rest". That protected the tidiest copy of the sensitive material and
left two untidier ones in plaintext: the interpretation layer carries claim statements
drawn verbatim from testimony, and the validation layer carries them again beside a
consultant's judgement.
"""
import base64
import tempfile
import unittest
from pathlib import Path

from ai_engine.persistence.crypto import NullCipher, cipher_available
from ai_engine.persistence.event_log import (
    EventLog,
    NullEventLog,
    find_log,
    read_events,
)

SECRET = "I use my personal ChatGPT to draft the summaries, unsanctioned."


class StubCipher:
    """A real, reversible transformation — not encryption, but exercises the plumbing.

    Without this the encrypted code path would never execute anywhere ``cryptography``
    cannot be imported, and "encrypted logs work" would rest on a skipped test. The
    stub proves the *mechanism* (opaque on disk, per-line, append-only, round-trips);
    the Fernet tests below prove the real cipher, and run wherever it is installed.
    """

    name = "stub (base64 — NOT encryption)"

    @property
    def protects_at_rest(self) -> bool:
        return True

    def encrypt(self, plaintext: bytes) -> bytes:
        return base64.b64encode(plaintext[::-1])

    def decrypt(self, blob: bytes) -> bytes:
        return base64.b64decode(blob)[::-1]


def _cipher():
    """The real cipher where it is importable, otherwise the stub."""
    if cipher_available():
        from ai_engine.persistence.crypto import FernetCipher, generate_key

        return FernetCipher(generate_key())
    return StubCipher()


class PlaintextLogTest(unittest.TestCase):
    """Development behaviour is unchanged: readable files, no key needed."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_writes_readable_jsonl_without_a_cipher(self):
        log = EventLog(self.dir, "txn-1", layer="interpretation")
        log.emit("ClaimProposed", statement=SECRET)
        self.assertFalse(log.encrypted)
        self.assertTrue(log.path.name.endswith(".jsonl"))
        self.assertIn(SECRET, log.path.read_text(encoding="utf-8"))

    def test_round_trips(self):
        log = EventLog(self.dir, "txn-1", layer="validation")
        log.emit("ClaimValidated", claim_id="clm-1", verdict="accepted")
        records = log.read()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["claim_id"], "clm-1")

    def test_null_log_reads_empty(self):
        self.assertEqual(NullEventLog().read(), [])

    def test_corrupt_line_does_not_lose_the_rest(self):
        log = EventLog(self.dir, "txn-1", layer="testimony")
        log.emit("A", n=1)
        with log.path.open("a", encoding="utf-8") as fh:
            fh.write("{not json\n")
        log.emit("B", n=2)
        self.assertEqual([r["event"] for r in log.read()], ["A", "B"])


class EncryptedLogTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.cipher = _cipher()

    def test_testimony_is_not_readable_on_disk(self):
        log = EventLog(self.dir, "txn-1", layer="interpretation", cipher=self.cipher)
        log.emit("ClaimProposed", statement=SECRET)
        self.assertTrue(log.encrypted)
        self.assertTrue(log.path.name.endswith(".jsonl.enc"))
        raw = log.path.read_text(encoding="utf-8")
        self.assertNotIn(SECRET, raw)
        self.assertNotIn("ChatGPT", raw)

    def test_round_trips_through_the_cipher(self):
        log = EventLog(self.dir, "txn-1", layer="validation", cipher=self.cipher)
        log.emit("ClaimValidated", claim_id="clm-1", statement=SECRET)
        records = log.read()
        self.assertEqual(records[0]["statement"], SECRET)

    def test_append_does_not_rewrite_earlier_records(self):
        # Per-line encryption: appending must not require decrypting everything
        # written so far, or an append-only log stops being append-only.
        log = EventLog(self.dir, "txn-1", layer="testimony", cipher=self.cipher)
        log.emit("A", n=1)
        first = log.path.read_bytes()
        log.emit("B", n=2)
        self.assertTrue(log.path.read_bytes().startswith(first))
        self.assertEqual([r["event"] for r in log.read()], ["A", "B"])

    def test_reading_encrypted_without_a_key_is_refused_not_silently_empty(self):
        log = EventLog(self.dir, "txn-1", layer="validation", cipher=self.cipher)
        log.emit("ClaimValidated", claim_id="clm-1")
        with self.assertRaises(ValueError):
            read_events(log.path, NullCipher())

    def test_a_plaintext_log_still_loads_after_a_key_is_introduced(self):
        # Development data must not become unreadable the day encryption is enabled.
        plain = EventLog(self.dir, "txn-2", layer="validation")
        plain.emit("ClaimValidated", claim_id="clm-old")
        found = find_log(self.dir, "txn-2", "validation")
        self.assertEqual(read_events(found, self.cipher)[0]["claim_id"], "clm-old")

    def test_the_ledger_reads_encrypted_verdicts(self):
        from ai_engine.webapp.ledger import read_verdicts

        log = EventLog(self.dir, "txn-3", layer="validation", cipher=self.cipher)
        log.emit("ClaimValidated", claim_id="clm-9", verdict="accepted",
                 validator_kind="consultant", reason="", correction=None,
                 decided_at="2026-01-01T00:00:00+00:00")
        verdicts = read_verdicts(self.dir, "txn-3", self.cipher)
        self.assertIn("clm-9", verdicts)
        self.assertEqual(verdicts["clm-9"].verdict, "accepted")


class NoPlaintextLeakTest(unittest.TestCase):
    """With a key configured, no layer may leave testimony readable on disk."""

    def test_every_layer_is_encrypted_when_a_cipher_is_configured(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            cipher = _cipher()
            for layer in ("testimony", "interpretation", "validation"):
                EventLog(d, "txn-1", layer=layer, cipher=cipher).emit(
                    "X", statement=SECRET)
            for path in d.rglob("*"):
                if path.is_file():
                    with self.subTest(path=path.name):
                        self.assertNotIn(
                            SECRET, path.read_text(encoding="utf-8", errors="ignore"))


if __name__ == "__main__":
    unittest.main()


class ReportPersistenceTest(unittest.TestCase):
    """A rendered report carries verbatim quotes, so it obeys the same at-rest
    policy as the testimony it cites. Before this existed, the transcript, event
    logs, and caches were cipher-wrapped while the report — the artifact most
    likely to be backed up or synced — was written with plain write_text().
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_report_is_opaque_on_disk_when_a_cipher_is_configured(self):
        from ai_engine.persistence.reports import load_report, save_report

        path = save_report(self.dir, "t1.report", SECRET, StubCipher())
        self.assertEqual(path.name, "t1.report.md.enc")
        self.assertNotIn(SECRET, path.read_text(encoding="utf-8", errors="ignore"))
        self.assertEqual(load_report(path, StubCipher()), SECRET)

    def test_report_stays_plain_in_dev_without_a_key(self):
        from ai_engine.persistence.reports import load_report, save_report

        path = save_report(self.dir, "t1.report", SECRET, NullCipher())
        self.assertEqual(path.name, "t1.report.md")
        self.assertIn(SECRET, path.read_text(encoding="utf-8"))
        self.assertEqual(load_report(path, NullCipher()), SECRET)

    def test_encrypted_report_refuses_to_load_without_a_cipher(self):
        from ai_engine.persistence.reports import load_report, save_report

        path = save_report(self.dir, "t1.report", SECRET, StubCipher())
        with self.assertRaises(ValueError):
            load_report(path, NullCipher())
