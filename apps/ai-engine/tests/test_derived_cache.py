"""Caching deterministic derived results.

The workspace recomputed the whole pipeline on every page view — the same interviews
producing the same model calls on every refresh, and an engagement report re-running
every pairwise relation call each time it was opened. With a live model that is
minutes of latency and repeated spend per click.

The cache boundary is temperature, and the tests below pin both halves of it: a
deterministic call is reused, and a sampled one never is. Caching the interview loop
would replace variation with repetition — a behaviour change disguised as an
optimisation.
"""
import base64
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ai_engine.llm.cache import CachingLLMClient, wrap_if_caching
from ai_engine.persistence.derived_store import (
    DEFAULT_TTL,
    DerivedStore,
    content_key,
)

SECRET = "I use my personal ChatGPT to draft the summaries, unsanctioned."


class _StubCipher:
    name = "stub"

    @property
    def protects_at_rest(self) -> bool:
        return True

    def encrypt(self, plaintext: bytes) -> bytes:
        return base64.b64encode(plaintext[::-1])

    def decrypt(self, blob: bytes) -> bytes:
        return base64.b64decode(blob)[::-1]


class _CountingLLM:
    def __init__(self, reply: str = "answer") -> None:
        self.calls = 0
        self.reply = reply

    def complete(self, *, system, messages, max_tokens=1024, temperature=0.4) -> str:
        self.calls += 1
        return self.reply


class _FailingLLM:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, *, system, messages, max_tokens=1024, temperature=0.4) -> str:
        self.calls += 1
        raise RuntimeError("model down")


class DerivedStoreTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_round_trips(self):
        store = DerivedStore(self.dir)
        key = content_key("kind", "a", 1)
        store.put(key, {"text": "hello"})
        self.assertEqual(store.get(key), {"text": "hello"})

    def test_miss_returns_none_and_counts(self):
        store = DerivedStore(self.dir)
        self.assertIsNone(store.get(content_key("nothing")))
        self.assertEqual(store.stats.misses, 1)

    def test_encrypted_at_rest(self):
        # Cached extraction output contains verbatim claim statements — testimony.
        store = DerivedStore(self.dir, _StubCipher())
        key = content_key("kind", "x")
        path = store.put(key, {"text": SECRET})
        self.assertNotIn(SECRET, path.read_text(encoding="utf-8", errors="ignore"))
        self.assertEqual(store.get(key)["text"], SECRET)

    def test_corrupt_entry_is_a_miss_not_a_crash(self):
        # The cache is an optimisation; it must never be able to break the pipeline.
        store = DerivedStore(self.dir)
        key = content_key("kind", "y")
        path = store.put(key, {"text": "v"})
        path.write_text("{ not json", encoding="utf-8")
        self.assertIsNone(store.get(key))

    def test_non_hex_key_is_refused(self):
        with self.assertRaises(ValueError):
            DerivedStore(self.dir).put("../escape", {"v": 1})

    def test_clear_and_sweep(self):
        store = DerivedStore(self.dir)
        store.put(content_key("a"), {"v": 1})
        store.put(content_key("b"), {"v": 2})
        self.assertEqual(store.sweep(), 0)
        later = datetime.now(timezone.utc) + DEFAULT_TTL + timedelta(days=1)
        self.assertEqual(store.sweep(now=later), 2)
        store.put(content_key("c"), {"v": 3})
        self.assertEqual(store.clear(), 1)

    def test_keys_are_content_addressed(self):
        self.assertEqual(content_key("a", 1), content_key("a", 1))
        self.assertNotEqual(content_key("a", 1), content_key("a", 2))


class CachingClientTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = DerivedStore(Path(self._tmp.name))

    def _client(self, inner, model="m1"):
        return CachingLLMClient(inner, self.store, model=model)

    def test_deterministic_call_is_reused(self):
        inner = _CountingLLM()
        client = self._client(inner)
        for _ in range(5):
            client.complete(system="s", messages=[{"role": "user", "content": "q"}],
                            temperature=0.0)
        self.assertEqual(inner.calls, 1, "a temperature-0 call was repeated")

    def test_sampled_calls_are_never_cached(self):
        # The interview loop samples on purpose; caching it would replace variation
        # with repetition, which is a behaviour change, not an optimisation.
        inner = _CountingLLM()
        client = self._client(inner)
        for _ in range(4):
            client.complete(system="s", messages=[{"role": "user", "content": "q"}],
                            temperature=0.4)
        self.assertEqual(inner.calls, 4)

    def test_different_prompt_is_a_different_entry(self):
        # A prompt edit must invalidate its own cache, not silently serve the
        # previous behaviour.
        inner = _CountingLLM()
        client = self._client(inner)
        client.complete(system="prompt v1", messages=[], temperature=0.0)
        client.complete(system="prompt v2", messages=[], temperature=0.0)
        self.assertEqual(inner.calls, 2)

    def test_different_messages_are_different_entries(self):
        inner = _CountingLLM()
        client = self._client(inner)
        client.complete(system="s", messages=[{"role": "user", "content": "a"}],
                        temperature=0.0)
        client.complete(system="s", messages=[{"role": "user", "content": "b"}],
                        temperature=0.0)
        self.assertEqual(inner.calls, 2)

    def test_one_model_never_serves_anothers_answers(self):
        inner = _CountingLLM()
        self._client(inner, model="model-a").complete(
            system="s", messages=[], temperature=0.0)
        self._client(inner, model="model-b").complete(
            system="s", messages=[], temperature=0.0)
        self.assertEqual(inner.calls, 2)

    def test_failures_are_not_cached(self):
        # A transient outage must not become a permanently empty answer.
        inner = _FailingLLM()
        client = self._client(inner)
        for _ in range(3):
            with self.assertRaises(RuntimeError):
                client.complete(system="s", messages=[], temperature=0.0)
        self.assertEqual(inner.calls, 3)

    def test_disabling_the_cache_passes_everything_through(self):
        inner = _CountingLLM()
        client = CachingLLMClient(inner, self.store, model="m", enabled=False)
        for _ in range(3):
            client.complete(system="s", messages=[], temperature=0.0)
        self.assertEqual(inner.calls, 3)

    def test_wrap_helper_leaves_mock_mode_alone(self):
        self.assertIsNone(wrap_if_caching(None, self.store, model="m"))
        inner = _CountingLLM()
        self.assertIs(wrap_if_caching(inner, None, model="m"), inner)


class PipelineReuseTest(unittest.TestCase):
    """The behaviour that motivated the cache: page views stop re-running the model."""

    def test_repeated_renders_make_no_further_calls(self):
        try:
            from fastapi.testclient import TestClient
        except Exception:  # pragma: no cover
            self.skipTest("requires fastapi and httpx")

        import ai_engine.webapp.app as appmod
        from ai_engine.config import Runtime, Settings

        with tempfile.TemporaryDirectory() as tmp:
            settings = Settings(api_key="k", store_key=None, runtime=Runtime.DEV,
                                data_dir=Path(tmp))
            inner = _CountingLLM('{"claims": []}')
            cached = CachingLLMClient(inner, settings.derived_store(), model="m")

            original = appmod.get_llm_client
            try:
                appmod.get_llm_client = lambda s: None      # seed via the mock path
                client = TestClient(appmod.create_app(settings))
                r = client.post("/interviews/new",
                                data={"participant": "A", "mode": "simulated"},
                                follow_redirects=False)
                iid = r.headers["location"].rsplit("/", 1)[-1]
                client.post(f"/interviews/{iid}/finish", follow_redirects=False)

                appmod.get_llm_client = lambda s: cached    # now "live"
                client.get("/")
                first = inner.calls
                self.assertGreater(first, 0, "the first render should do real work")
                for _ in range(3):
                    client.get("/")
                self.assertEqual(inner.calls, first,
                                 "re-rendering re-ran the model despite the cache")
            finally:
                appmod.get_llm_client = original


if __name__ == "__main__":
    unittest.main()
