"""The second live adapter: Google Gemini on Vertex AI, via ADC.

Same contract as :class:`AnthropicClient` — the ``LLMClient`` protocol — so the
provider is an infrastructure choice, invisible to the interview loop (Art.: the
LLM sits behind a port). Chosen with ``GROUNDWORK_PROVIDER=gemini`` (or left to
the factory: an Anthropic key wins, then Gemini when ``GOOGLE_APPLICATION_CREDENTIALS``
is present).

Authentication is Application Default Credentials, two paths:

  * **On Google Cloud** (Cloud Run, GCE, GKE), the metadata server hands out a
    token to any process on the box — plain HTTP, stdlib only.
  * **A service-account key file** at ``GOOGLE_APPLICATION_CREDENTIALS``: a JWT
    signed RS256 and exchanged at the OAuth token endpoint. RS256 signing uses
    the ``cryptography`` package — the same optional extra the encrypted store
    already needs — rather than pulling in a Google SDK.

**Honesty note:** this adapter has never been executed against a live Gemini
endpoint any more than the Anthropic adapter has; the first live run is still
the repo's open empirical gap. The unit tests prove request shape, role
mapping, and token caching against a fake transport.
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from .client import DEFAULT_TIMEOUT, _log_retry
from .retry import RetryPolicy, call_with_retries

_METADATA_URL = ("http://metadata.google.internal/computeMetadata/v1/instance/"
                 "service-accounts/default/token")
_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


class _HttpStatusError(RuntimeError):
    """Carries an HTTP status on ``status_code`` so ``retry.classify`` can see it."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status


def _http_json(url: str, *, body: dict | None = None, headers: dict | None = None,
               timeout: float = DEFAULT_TIMEOUT) -> dict:
    """One JSON HTTP exchange. Module-level so tests can stub the transport."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise _HttpStatusError(exc.code, f"HTTP {exc.code}: {detail}") from exc


def _load_service_account(path: str) -> dict:
    try:
        key = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"GOOGLE_APPLICATION_CREDENTIALS points at {path!r}, which cannot be "
            f"read as a service-account key file: {exc}") from exc
    for field in ("client_email", "private_key", "token_uri"):
        if not key.get(field):
            raise RuntimeError(
                f"the service-account key at {path!r} has no {field!r}; it is not "
                f"a usable Google Cloud credential")
    return key


def _sign_jwt(key: dict, *, now: float) -> str:
    """A one-hour RS256 JWT for the token exchange, signed with ``cryptography``."""
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Signing a service-account JWT needs the 'cryptography' package — "
            "install it with `pip install -e '.[secure]'` (the encrypted store "
            "uses the same extra).") from exc

    header = {"alg": "RS256", "typ": "JWT"}
    claims = {
        "iss": key["client_email"],
        "scope": _SCOPE,
        "aud": key["token_uri"],
        "iat": int(now),
        "exp": int(now) + 3600,
    }
    b64 = lambda obj: base64.urlsafe_b64encode(
        json.dumps(obj).encode("utf-8")).rstrip(b"=")
    unsigned = b64(header) + b"." + b64(claims)
    private_key = serialization.load_pem_private_key(
        key["private_key"].encode("utf-8"), password=None)
    signature = private_key.sign(unsigned, padding.PKCS1v15(), hashes.SHA256())
    return (unsigned + b"." + base64.urlsafe_b64encode(signature).rstrip(b"=")
            ).decode("ascii")


class GeminiClient:
    """Live adapter over Vertex AI ``generateContent`` with ADC credentials."""

    def __init__(
        self,
        *,
        model: str,
        project: str,
        location: str = "us-central1",
        credentials_path: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        policy: "RetryPolicy | None" = None,
    ) -> None:
        self._model = model
        self._project = project
        self._location = location
        self._credentials_path = (credentials_path
                                  or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        self._timeout = timeout
        self._policy = policy or RetryPolicy()
        self._token: tuple[str, float] | None = None  # (access_token, expires_at)

    # -- auth ---------------------------------------------------------------
    def _access_token(self) -> str:
        now = time.time()
        if self._token and self._token[1] > now + 60:
            return self._token[0]
        if self._credentials_path:
            key = _load_service_account(self._credentials_path)
            assertion = _sign_jwt(key, now=now)
            response = _http_json(
                key["token_uri"],
                body={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                      "assertion": assertion},
                headers={"Content-Type": "application/json"},
                timeout=self._timeout,
            )
            if "access_token" not in response:
                raise _HttpStatusError(
                    401, f"token exchange returned no access_token: {response}")
            token, lifetime = response["access_token"], response.get("expires_in", 3600)
        else:
            # Not on a key file: trust the metadata server (works only on GCP —
            # which is exactly the deployment this path is for).
            response = _http_json(
                _METADATA_URL,
                headers={"Metadata-Flavor": "Google"},
                timeout=5.0,
            )
            token, lifetime = response["access_token"], response.get("expires_in", 3600)
        self._token = (token, now + float(lifetime))
        return token

    # -- the protocol ---------------------------------------------------------
    def complete(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.4,
    ) -> str:
        def _once() -> str:
            url = (f"https://{self._location}-aiplatform.googleapis.com/v1/"
                   f"projects/{self._project}/locations/{self._location}/"
                   f"publishers/google/models/{self._model}:generateContent")
            body = {
                # Gemini separates the system instruction from the turn history;
                # roles are "user"/"model" rather than "user"/"assistant".
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [
                    {"role": ("model" if m["role"] == "assistant" else "user"),
                     "parts": [{"text": m["content"]}]}
                    for m in messages
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }
            response = _http_json(
                url, body=body,
                headers={
                    "Authorization": f"Bearer {self._access_token()}",
                    "Content-Type": "application/json",
                },
                timeout=self._timeout,
            )
            candidates = response.get("candidates") or []
            if not candidates:
                block = response.get("promptFeedback", {}).get("blockReason")
                raise RuntimeError(
                    "Gemini returned no candidates"
                    + (f" (blocked: {block})" if block else ""))
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts).strip()

        return call_with_retries(_once, policy=self._policy, on_retry=_log_retry)
