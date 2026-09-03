"""The edges of the privacy firewall, not its stores.

The transcript store, event logs, and caches were always cipher-wrapped; the
leaks lived at the edges — the re-identification key written beside the
employer deliverable, a pseudonymizer that forgot the engagement on restart
(and silently inflated k), tampered log lines swallowed on read, an
ONTORA_ENV parse that failed open, and a production posture enforced only at
whatever entry point remembered it. Each test pins one closed edge.
"""
import base64
import json
import os
import tempfile
import unittest
from pathlib import Path

from ai_engine.config import ConfigurationError, runtime_from_env
from ai_engine.persistence.crypto import NullCipher
from ai_engine.persistence.event_log import EventLog, TamperedEventLog
from ai_engine.persistence.transcript_store import TranscriptStore
from ai_engine.privacy.identity import Pseudonymizer, restricted_dir

ENV = "ONTORA_ENV"


class _StubCipher:
    """Reversible, opaque-on-disk — exercises the encrypted plumbing anywhere."""

    name = "stub"

    @property
    def protects_at_rest(self) -> bool:
        return True

    def encrypt(self, plaintext: bytes) -> bytes:
        return base64.b64encode(plaintext[::-1])

    def decrypt(self, blob: bytes) -> bytes:
        return base64.b64decode(blob)[::-1]


class IdentityPersistenceTest(unittest.TestCase):
    """The determinism invariant must survive a process restart."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_same_person_keeps_the_same_pseudonym_across_a_restart(self):
        first = Pseudonymizer.load_or_create(self.dir)
        before = first.pseudonym("Dana")

        restarted = Pseudonymizer.load_or_create(self.dir)
        self.assertEqual(restarted.pseudonym("Dana"), before)

    def test_distinct_engagements_remain_unlinkable(self):
        with tempfile.TemporaryDirectory() as other:
            a = Pseudonymizer.load_or_create(self.dir).pseudonym("Dana")
            b = Pseudonymizer.load_or_create(Path(other)).pseudonym("Dana")
        self.assertNotEqual(a, b)

    def test_reidentification_key_survives_the_restart_too(self):
        # The caller saves after issuing (as the webapp routes do); the point is
        # that the mapping comes back, not just the salt.
        first = Pseudonymizer.load_or_create(self.dir)
        first.pseudonym("Dana")
        first.save_state(self.dir)
        restarted = Pseudonymizer.load_or_create(self.dir)
        self.assertIn("Dana", restarted.key.values())

    def test_key_is_written_outside_the_deliverable_directory(self):
        p = Pseudonymizer("salt-a")
        p.pseudonym("Dana")
        key_path = p.write_key(restricted_dir(self.dir) / "identity-key.RESTRICTED.json")
        self.assertIn("RESTRICTED", key_path.parts)
        self.assertNotEqual(key_path.parent, self.dir,
                            "the re-identification key must not sit beside "
                            "employer-facing deliverables")

    def test_pseudonyms_carry_enough_entropy_to_not_collide(self):
        p = Pseudonymizer("salt-a")
        pseudo = p.pseudonym("Dana")
        hex_part = pseudo.removeprefix("P-")
        self.assertEqual(len(hex_part), 12,
                         "24 bits collides silently at engagement scale; a "
                         "collision merges two people's testimony")


class TamperEvidenceTest(unittest.TestCase):
    """Swallowing an authentication failure erases the event the log carried."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _write_log(self, cipher) -> Path:
        log = EventLog(self.dir, "tamper-1", cipher=cipher)
        log.emit("SubjectResponded", sequence=1)
        log.emit("SubjectResponded", sequence=2)
        log.emit("SubjectResponded", sequence=3)
        return log.path

    def test_a_tampered_midfile_line_is_loud(self):
        for cipher in (NullCipher(), _StubCipher()):
            with self.subTest(cipher=cipher.name):
                self.dir.mkdir(exist_ok=True)
                path = self._write_log(cipher)
                lines = path.read_text(encoding="utf-8").splitlines()
                lines[1] = lines[1][::-1] if isinstance(cipher, NullCipher) \
                    else ("x" * 8) + lines[1][8:]
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                with self.assertRaises(TamperedEventLog):
                    EventLog(self.dir, "tamper-1", cipher=cipher).read()

    def test_a_torn_final_line_is_tolerated(self):
        for cipher in (NullCipher(), _StubCipher()):
            with self.subTest(cipher=cipher.name):
                self.dir.mkdir(exist_ok=True)
                path = self._write_log(cipher)
                with path.open("a", encoding="utf-8") as fh:
                    fh.write("torn" if isinstance(cipher, NullCipher) else "torn123")
                self.assertEqual(len(EventLog(self.dir, "tamper-1", cipher=cipher).read()), 3)


class EnvFailClosedTest(unittest.TestCase):
    def _with_env(self, value):
        prior = os.environ.get(ENV)
        os.environ[ENV] = value
        try:
            return runtime_from_env()
        finally:
            if prior is None:
                os.environ.pop(ENV, None)
            else:
                os.environ[ENV] = prior

    def test_a_typo_is_an_error_not_dev(self):
        with self.assertRaises(ConfigurationError):
            self._with_env("produnction")

    def test_known_values_still_parse(self):
        self.assertFalse(self._with_env("dev").value == "production")
        self.assertFalse(self._with_env("development").value == "production")
        self.assertTrue(self._with_env("production").value == "production")
        self.assertTrue(self._with_env("prod").value == "production")


class ProductionAtRestTest(unittest.TestCase):
    """The at-rest guarantee holds at the persistence layer, not only at entry
    points that remembered to call assert_deployable."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def _production(self):
        self._prior = os.environ.get(ENV)
        os.environ[ENV] = "production"
        self.addCleanup(self._restore_env)

    def _restore_env(self):
        if self._prior is None:
            os.environ.pop(ENV, None)
        else:
            os.environ[ENV] = self._prior

    def test_plaintext_stores_refuse_to_construct_in_production(self):
        self._production()
        with self.assertRaises(RuntimeError):
            EventLog(self.dir, "t", cipher=NullCipher())
        with self.assertRaises(RuntimeError):
            TranscriptStore(self.dir, None)

    def test_encrypted_stores_construct_in_production(self):
        self._production()
        EventLog(self.dir, "t", cipher=_StubCipher())
        TranscriptStore(self.dir, _StubCipher())

    def test_dev_stays_plain(self):
        EventLog(self.dir, "t", cipher=NullCipher())
        TranscriptStore(self.dir, None)


if __name__ == "__main__":
    unittest.main()
