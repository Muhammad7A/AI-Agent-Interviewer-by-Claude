"""Durable evidence, and the production posture.

The central assertion here is the one the whole evidence-first architecture rests on
once a process boundary exists:

    a rehydrated transcript resolves every EvidenceRef to exactly the same text.

Before the transcript store, that was false — the transcript was in memory only and
the event log recorded a character count instead of the words, so every reference in
every report went dangling the moment the process exited.
"""
import os
import tempfile
import unittest
from pathlib import Path

from ai_engine.config import ConfigurationError, Runtime, Settings, get_llm_client
from ai_engine.evidence.grounding import ground_proposal
from ai_engine.evidence.model import RawProposal
from ai_engine.evidence.tagger import EvidenceTagger
from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.crypto import (
    KEY_ENV,
    CipherUnavailable,
    FernetCipher,
    NullCipher,
    cipher_available,
    make_cipher,
)
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.persistence.transcript_store import (
    TranscriptNotFound,
    TranscriptStore,
    transcript_from_dict,
    transcript_to_dict,
)
from ai_engine.subjects.simulated import SimulatedInterviewee, default_persona
from ai_engine.transcript.model import Speaker, Transcript, TranscriptFinalizedError


def _interview() -> Transcript:
    engine = InterviewEngine(llm=None, max_turns=14)
    subject = SimulatedInterviewee(default_persona("open"), llm=None)
    return run_interview(engine=engine, subject=subject,
                         event_log=NullEventLog(), max_turns=14).transcript


class RoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.store = TranscriptStore(self.dir)

    def test_segments_survive_byte_for_byte(self):
        original = _interview()
        self.store.save(original)
        loaded = self.store.load(original.id)
        self.assertEqual(len(loaded.segments), len(original.segments))
        for a, b in zip(original.segments, loaded.segments):
            self.assertEqual((a.id, a.sequence, a.speaker, a.text),
                             (b.id, b.sequence, b.speaker, b.text))

    def test_evidence_resolves_identically_after_reload(self):
        # THE invariant. If this ever fails, every stored finding is unverifiable.
        original = _interview()
        claims = EvidenceTagger(llm=None).tag(original).claims
        self.assertGreater(len(claims), 0)
        self.store.save(original)
        loaded = self.store.load(original.id)
        for claim in claims:
            ref = claim.evidence[0].ref
            with self.subTest(claim=claim.id):
                self.assertEqual(ref.resolve(loaded), ref.resolve(original))

    def test_char_offsets_are_preserved_exactly(self):
        original = _interview()
        segment = next(s for s in original.segments if s.speaker is Speaker.SUBJECT)
        # A whole-word slice: the matcher legitimately trims trailing whitespace and
        # punctuation from a needle, so a mid-space cut would resolve one char short.
        quote = segment.text[:20].rstrip(" .,;:!?")
        claim, reason = ground_proposal(
            RawProposal("observation", "x", quote=quote, tier=2), original)
        self.assertEqual(reason, "grounded")
        self.store.save(original)
        loaded = self.store.load(original.id)
        self.assertEqual(claim.evidence[0].ref.resolve(loaded), quote)

    def test_finalized_state_and_immutability_survive(self):
        original = _interview()
        self.assertTrue(original.finalized)
        self.store.save(original)
        loaded = self.store.load(original.id)
        self.assertTrue(loaded.finalized)
        with self.assertRaises(TranscriptFinalizedError):
            loaded.append(Speaker.SUBJECT, "tampering after the fact")

    def test_dict_round_trip_is_lossless(self):
        original = _interview()
        again = transcript_from_dict(transcript_to_dict(original))
        self.assertEqual(again.id, original.id)
        self.assertEqual([s.text for s in again.segments],
                         [s.text for s in original.segments])

    def test_stored_transcript_is_write_once(self):
        original = _interview()
        self.store.save(original)
        with self.assertRaises(FileExistsError):
            self.store.save(original)

    def test_missing_transcript_raises(self):
        with self.assertRaises(TranscriptNotFound):
            self.store.load("txn-does-not-exist")

    def test_listing_and_existence(self):
        original = _interview()
        self.assertFalse(self.store.exists(original.id))
        self.store.save(original)
        self.assertTrue(self.store.exists(original.id))
        self.assertEqual(self.store.list_ids(), [original.id])

    def test_unknown_schema_is_refused(self):
        with self.assertRaises(ValueError):
            transcript_from_dict({"schema": "something-else/v9"})


class CipherTest(unittest.TestCase):
    def test_null_cipher_declares_it_protects_nothing(self):
        cipher = NullCipher()
        self.assertFalse(cipher.protects_at_rest)
        self.assertEqual(cipher.decrypt(cipher.encrypt(b"abc")), b"abc")

    def test_no_key_means_plaintext(self):
        self.assertFalse(make_cipher(None).protects_at_rest)

    def test_a_configured_key_never_silently_downgrades(self):
        # If a key is set but the cipher cannot be built, that must raise rather
        # than quietly writing plaintext.
        if cipher_available():
            self.skipTest("cryptography is importable; the downgrade path cannot occur")
        with self.assertRaises(CipherUnavailable):
            make_cipher("some-key")

    @unittest.skipUnless(cipher_available(),
                         "requires the 'secure' extra (cryptography importable)")
    def test_encrypted_round_trip_and_opacity(self):
        from ai_engine.persistence.crypto import generate_key

        with tempfile.TemporaryDirectory() as tmp:
            store = TranscriptStore(Path(tmp), FernetCipher(generate_key()))
            original = _interview()
            path = store.save(original)
            secret = next(s.text for s in original.segments
                          if s.speaker is Speaker.SUBJECT)
            self.assertNotIn(secret.encode("utf-8"), path.read_bytes(),
                             "testimony must not be readable on disk")
            self.assertEqual([s.text for s in store.load(original.id).segments],
                             [s.text for s in original.segments])


class ProductionPostureTest(unittest.TestCase):
    """The silent-mock and plaintext-testimony hazards, made impossible."""

    def _settings(self, **kw):
        base = dict(api_key=None, store_key=None, runtime=Runtime.PRODUCTION)
        base.update(kw)
        return Settings(**base)

    def test_dev_allows_mock_and_plaintext(self):
        settings = self._settings(runtime=Runtime.DEV)
        settings.assert_deployable()  # must not raise
        self.assertIsNone(get_llm_client(settings))

    def test_production_refuses_missing_model_key(self):
        with self.assertRaises(ConfigurationError) as ctx:
            self._settings(store_key="k").assert_deployable()
        self.assertIn("scripted mock", str(ctx.exception))

    def test_production_refuses_plaintext_storage(self):
        with self.assertRaises(ConfigurationError) as ctx:
            self._settings(api_key="sk-test").assert_deployable()
        self.assertIn("plaintext", str(ctx.exception))

    def test_production_lists_every_problem_at_once(self):
        problems = self._settings().deployment_problems()
        self.assertEqual(len(problems), 2)

    def test_get_llm_client_refuses_to_mock_in_production(self):
        with self.assertRaises(ConfigurationError):
            get_llm_client(self._settings())

    def test_production_with_unusable_cipher_is_refused(self):
        # A key that cannot actually encrypt is worse than no key: it looks safe.
        if cipher_available():
            self.skipTest("cryptography is importable in this environment")
        problems = self._settings(api_key="sk-test", store_key="k").deployment_problems()
        self.assertTrue(any("cryptography" in p for p in problems))

    def test_posture_banner_states_the_truth(self):
        banner = self._settings(runtime=Runtime.DEV).posture_banner()
        self.assertIn("MOCK", banner)
        self.assertIn("PLAINTEXT", banner)

    def test_runtime_reads_the_environment(self):
        prior = os.environ.get("GROUNDWORK_ENV")
        try:
            os.environ["GROUNDWORK_ENV"] = "production"
            self.assertTrue(Settings().is_production)
            os.environ["GROUNDWORK_ENV"] = "dev"
            self.assertFalse(Settings().is_production)
        finally:
            if prior is None:
                os.environ.pop("GROUNDWORK_ENV", None)
            else:
                os.environ["GROUNDWORK_ENV"] = prior


if __name__ == "__main__":
    unittest.main()
