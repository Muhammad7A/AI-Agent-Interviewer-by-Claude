"""The Gemini adapter — proven against a fake transport, never a live endpoint.

Every claim here is about what the adapter *sends* and how it *classifies
failure*: request shape, role mapping (assistant → model), system instruction
placement, ADC token resolution and caching, and the transient/permanent split.
The first live call against a real Vertex AI endpoint remains the repo's open
empirical gap, exactly as documented.
"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai_engine.config import Settings
from ai_engine.llm import gemini_client as gc
from ai_engine.llm.gemini_client import GeminiClient, _HttpStatusError
from ai_engine.llm.retry import LLMUnavailable

_TOKEN_RESPONSE = {"access_token": "ya29.test-token", "expires_in": 3600}
_CONTENT_RESPONSE = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}


def _fake_sa_key() -> dict:
    """A real RSA key so the JWT actually gets signed with ``cryptography``."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    return {
        "client_email": "interviewer@groundwork.iam.gserviceaccount.com",
        "private_key": pem,
        "token_uri": "https://oauth2.googleapis.com/token",
    }


class TransportTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.key_path = Path(self._tmp.name) / "sa.json"
        self.key_path.write_text(json.dumps(_fake_sa_key()), encoding="utf-8")
        self.exchanges: list[tuple[str, dict | None, dict | None]] = []
        self._patch = mock.patch.object(
            gc, "_http_json",
            side_effect=self._fake_transport)
        self._patch.start()
        self.addCleanup(self._patch.stop)

    def _fake_transport(self, url, *, body=None, headers=None, timeout=None):
        self.exchanges.append((url, body, headers))
        if url == "https://oauth2.googleapis.com/token":
            return dict(_TOKEN_RESPONSE)
        return dict(_CONTENT_RESPONSE)

    def _client(self, **kw) -> GeminiClient:
        return GeminiClient(model="gemini-2.5-flash", project="proj-1",
                            location="us-central1",
                            credentials_path=str(self.key_path), **kw)

    def test_request_shape_and_role_mapping(self):
        text = self._client().complete(
            system="You are the interviewer.",
            messages=[{"role": "assistant", "content": "Earlier question."},
                      {"role": "user", "content": "The answer."}],
            max_tokens=300, temperature=0.2)
        self.assertEqual(text, "ok")

        generate = self.exchanges[-1]
        self.assertIn(":generateContent", generate[0])
        self.assertIn("publishers/google/models/gemini-2.5-flash", generate[0])
        self.assertEqual(generate[2]["Authorization"], "Bearer ya29.test-token")
        body = generate[1]
        self.assertEqual(
            body["systemInstruction"]["parts"][0]["text"], "You are the interviewer.")
        self.assertEqual([c["role"] for c in body["contents"]], ["model", "user"])
        self.assertEqual(body["generationConfig"],
                         {"temperature": 0.2, "maxOutputTokens": 300})

    def test_the_token_is_exchanged_once_and_reused(self):
        client = self._client()
        client.complete(system="s", messages=[{"role": "user", "content": "a"}])
        client.complete(system="s", messages=[{"role": "user", "content": "b"}])
        token_calls = [e for e in self.exchanges
                       if e[0] == "https://oauth2.googleapis.com/token"]
        self.assertEqual(len(token_calls), 1,
                         "the access token must be cached across calls")

    def test_permanent_status_fails_fast_transient_is_retried(self):
        responses = [_HttpStatusError(400, "bad request")]

        def flaky(url, *, body=None, headers=None, timeout=None):
            if url == "https://oauth2.googleapis.com/token":
                return dict(_TOKEN_RESPONSE)
            if responses:
                raise responses.pop(0)
            return dict(_CONTENT_RESPONSE)

        with mock.patch.object(gc, "_http_json", side_effect=flaky):
            with self.assertRaises(Exception) as ctx:
                self._client(policy=gc.RetryPolicy(attempts=1)).complete(
                    system="s", messages=[{"role": "user", "content": "a"}])
            self.assertIn("400", str(ctx.exception))

        def transient_then_ok(url, *, body=None, headers=None, timeout=None):
            if url == "https://oauth2.googleapis.com/token":
                return dict(_TOKEN_RESPONSE)
            if not getattr(transient_then_ok, "hit", False):
                transient_then_ok.hit = True
                raise _HttpStatusError(500, "internal")
            return dict(_CONTENT_RESPONSE)

        with mock.patch.object(gc, "_http_json", side_effect=transient_then_ok):
            text = self._client(policy=gc.RetryPolicy(attempts=2, jitter=False)).complete(
                system="s", messages=[{"role": "user", "content": "a"}])
        self.assertEqual(text, "ok")

    def test_a_dead_endpoint_surfaces_as_llm_unavailable(self):
        with mock.patch.object(gc, "_http_json",
                               side_effect=_HttpStatusError(429, "slow down")):
            with self.assertRaises(LLMUnavailable):
                self._client(policy=gc.RetryPolicy(attempts=2, jitter=False)).complete(
                    system="s", messages=[{"role": "user", "content": "a"}])


class MetadataPathTest(unittest.TestCase):
    def test_without_a_key_file_the_metadata_server_is_used(self):
        client = GeminiClient(model="gemini-2.5-flash", project="proj-1",
                              credentials_path=None)
        calls = []

        def fake(url, *, body=None, headers=None, timeout=None):
            calls.append((url, headers))
            if url == gc._METADATA_URL:
                self.assertEqual(headers.get("Metadata-Flavor"), "Google")
                return dict(_TOKEN_RESPONSE)
            return dict(_CONTENT_RESPONSE)

        with mock.patch.object(gc, "_http_json", side_effect=fake):
            text = client.complete(system="s", messages=[{"role": "user", "content": "a"}])
        self.assertEqual(text, "ok")
        self.assertEqual(calls[0][0], gc._METADATA_URL)


class ProviderSelectionTest(unittest.TestCase):
    def test_gemini_provider_builds_the_gemini_adapter(self):
        import base64

        with tempfile.TemporaryDirectory() as tmp:
            store_key = base64.urlsafe_b64encode(os.urandom(32)).decode("ascii")
            with mock.patch.dict(os.environ, {
                "GROUNDWORK_PROVIDER": "gemini",
                "GOOGLE_APPLICATION_CREDENTIALS": "sa.json",
                "GROUNDWORK_GEMINI_PROJECT": "proj-1",
            }):
                settings = Settings(store_key=store_key, data_dir=Path(tmp))
                self.assertTrue(settings.has_live_model)
                self.assertEqual(settings.provider, "gemini")
                client = __import__("ai_engine.config", fromlist=["get_llm_client"]) \
                    .get_llm_client(settings)
            from ai_engine.llm.cache import CachingLLMClient
            from ai_engine.llm.gemini_client import GeminiClient as G

            self.assertIsInstance(client, CachingLLMClient)
            self.assertIsInstance(client._inner, G)

    def test_an_explicit_provider_beats_inference(self):
        with mock.patch.dict(os.environ, {"GROUNDWORK_PROVIDER": "anthropic",
                                          "GOOGLE_APPLICATION_CREDENTIALS": "sa.json"}):
            settings = Settings()
        self.assertEqual(settings.provider, "anthropic")

    def test_gemini_without_a_project_is_a_deployment_problem(self):
        with mock.patch.dict(os.environ, {"GROUNDWORK_PROVIDER": "gemini",
                                          "GOOGLE_APPLICATION_CREDENTIALS": "sa.json"}):
            settings = Settings()
        problems = settings.deployment_problems()
        self.assertTrue(any("GROUNDWORK_GEMINI_PROJECT" in p for p in problems))


if __name__ == "__main__":
    unittest.main()


class ProviderFailClosedTest(unittest.TestCase):
    """GROUNDWORK_PROVIDER=gemni (typo) used to fall through to mock mode: a
    'live' deployment serving scripted interviews. Same fail-closed rule as
    GROUNDWORK_ENV."""

    def test_an_unknown_provider_is_refused(self):
        import os

        from ai_engine.config import ConfigurationError

        with mock.patch.dict(os.environ, {"GROUNDWORK_PROVIDER": "gemni"}):
            with self.assertRaises(ConfigurationError):
                Settings()

    def test_known_providers_still_construct(self):
        with mock.patch.dict(os.environ, {"GROUNDWORK_PROVIDER": "gemini"}):
            Settings()
        with mock.patch.dict(os.environ, {"GROUNDWORK_PROVIDER": "anthropic"}):
            Settings()
