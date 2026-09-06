"""Runtime configuration, the LLM-client factory, and the production posture.

Nothing in ``interview/`` or ``transcript/`` names a model or an SDK — that is an
infrastructure concern that lives here (Constitution: the LLM sits behind a port; a
provider change is an infrastructure-only change).

**Why a production posture exists.** The offline fallbacks in this package are
excellent for testing and a liability in a deployment:

  * with no API key, every component silently falls back to *scripted mock*
    behaviour — a misconfigured deployment would serve fake interviews to real
    employees and log them as genuine testimony;
  * with no storage key, verbatim attributable testimony is written to disk in
    plaintext.

Both are correct for local development and unacceptable in production, so the
difference is made explicit: ``GROUNDWORK_ENV=production`` refuses to start unless a real
model and a real cipher are configured. Failing loudly at startup is the only safe
version of this — a silent mock is indistinguishable from a working system until
someone reads a transcript that nobody ever said.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .persistence.crypto import KEY_ENV, Cipher, cipher_available, make_cipher

# Default to a current Claude model; override with GROUNDWORK_MODEL.
#
# This default must be a *real* model id. The previous value named a model that
# does not exist, so the first live call returned 404 — and because 404 is
# correctly classified as permanent in ``llm/retry.py``, it failed instantly
# rather than retrying. Nothing caught it because the evaluation harness had only
# ever run in mock mode, where no request is made at all. See
# :func:`preflight_model`, which exists so that failure can never again wait
# until an employee is mid-interview to surface.
#
# Sonnet rather than the largest model: an engagement is roughly four hundred
# calls, and the deterministic ones (tagging, entailment, relation) are
# classification work. Set GROUNDWORK_MODEL to a larger model if interview cognition
# needs it — that is a one-variable change.
DEFAULT_MODEL = os.environ.get("GROUNDWORK_MODEL", "claude-sonnet-5")

ENV_VAR = "GROUNDWORK_ENV"


class Runtime(str, Enum):
    #: Local development and tests. Mock cognition and plaintext storage allowed.
    DEV = "dev"
    #: A real deployment talking to real employees. Neither is allowed.
    PRODUCTION = "production"


class ConfigurationError(RuntimeError):
    """Raised when the runtime is not safe to serve real interviews."""


def runtime_from_env() -> Runtime:
    """Parse ``GROUNDWORK_ENV`` — and refuse an unrecognized value.

    The whole point of the production posture is refusing unsafe startup, so a
    typo'd value ("produnction") must be an error, not silently mean dev: a guard
    that fails open is a request, not a guard.
    """
    raw = (os.environ.get(ENV_VAR) or "dev").strip().lower()
    if raw in ("production", "prod"):
        return Runtime.PRODUCTION
    if raw in ("dev", "development"):
        return Runtime.DEV
    raise ConfigurationError(
        f"{ENV_VAR}={raw!r} is not a recognized runtime — use 'dev' or "
        f"'production'. A typo here would silently disable the production "
        f"posture, so it is refused rather than ignored.")


@dataclass(frozen=True)
class Settings:
    model: str = DEFAULT_MODEL
    api_key: str | None = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY") or None
    )
    store_key: str | None = field(
        default_factory=lambda: os.environ.get(KEY_ENV) or None
    )
    runtime: Runtime = field(default_factory=runtime_from_env)
    #: Reuse deterministic derived results across page views. Off only for
    #: benchmarking what an uncached run actually costs.
    cache_derived: bool = os.environ.get("GROUNDWORK_CACHE", "1") not in ("0", "false", "no")
    max_turns: int = int(os.environ.get("GROUNDWORK_MAX_TURNS", "14"))
    temperature: float = float(os.environ.get("GROUNDWORK_TEMPERATURE", "0.4"))
    data_dir: Path = Path(os.environ.get("GROUNDWORK_DATA_DIR", "data/interviews"))
    #: An oversized answer would be appended to the transcript verbatim and sent
    #: as part of every later model call — a multi-MB paste guarantees a permanent
    #: request failure on every future turn, wedging the interview with no way to
    #: retract the answer. Capped at the web layer, where the input arrives.
    max_answer_chars: int = int(os.environ.get("GROUNDWORK_MAX_ANSWER_CHARS", "20000"))
    #: When set, the consultant workspace demands HTTP Basic with this password,
    #: and production refuses to start without one. Unset keeps the localhost
    #: no-auth Year-0/1 posture; the employee surface's auth is invitation tokens.
    operator_password: str | None = field(
        default_factory=lambda: os.environ.get("GROUNDWORK_OPERATOR_PASSWORD") or None)
    #: Which live adapter to build. Explicit via GROUNDWORK_PROVIDER ("anthropic"
    #: | "gemini"); otherwise inferred — an Anthropic key wins, then Gemini when
    #: GOOGLE_APPLICATION_CREDENTIALS is set. Empty means mock mode.
    provider: str = field(default_factory=lambda: (
        (os.environ.get("GROUNDWORK_PROVIDER") or "").strip().lower()
        or ("anthropic" if os.environ.get("ANTHROPIC_API_KEY")
            else ("gemini" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                  else ""))))
    gemini_model: str = os.environ.get("GROUNDWORK_GEMINI_MODEL", "gemini-2.5-flash")
    gemini_project: str | None = field(
        default_factory=lambda: os.environ.get("GROUNDWORK_GEMINI_PROJECT") or None)
    gemini_location: str = os.environ.get("GROUNDWORK_GEMINI_LOCATION", "us-central1")

    @property
    def has_live_model(self) -> bool:
        if self.provider == "gemini":
            return True  # ADC is configured via the environment; preflight proves it
        return bool(self.api_key)

    @property
    def is_production(self) -> bool:
        return self.runtime is Runtime.PRODUCTION

    def cipher(self) -> Cipher:
        return make_cipher(self.store_key)

    def derived_store(self):
        """Cache for deterministic derived results. Encrypted like everything else."""
        from .persistence.derived_store import DerivedStore

        return DerivedStore(self.data_dir, self.cipher())

    # -- the posture check --------------------------------------------------
    def deployment_problems(self) -> list[str]:
        """Every reason this configuration must not serve real interviews."""
        problems: list[str] = []
        if not self.has_live_model:
            problems.append(
                "no live model configured: set ANTHROPIC_API_KEY, or "
                "GOOGLE_APPLICATION_CREDENTIALS (with GROUNDWORK_PROVIDER=gemini) — "
                "otherwise cognition would silently fall back to the scripted mock "
                "interviewer, serving fabricated interviews to real people and "
                "recording them as genuine testimony"
            )
        if self.provider == "gemini" and not self.gemini_project:
            problems.append(
                "GROUNDWORK_GEMINI_PROJECT is not set: the Vertex AI endpoint is "
                "per-project, so the Gemini adapter cannot be built without it"
            )
        if not self.store_key:
            problems.append(
                f"no {KEY_ENV}: verbatim, attributable employee testimony would be "
                f"written to disk in plaintext"
            )
        elif not cipher_available():
            problems.append(
                f"{KEY_ENV} is set but the 'cryptography' package is not importable, "
                f"so encryption at rest cannot actually be performed "
                f"(install with `pip install -e '.[secure]'`)"
            )
        return problems

    def assert_deployable(self) -> None:
        """Raise unless this configuration is safe for real interviews.

        Call at startup, before any employee can reach the system.
        """
        if not self.is_production:
            return
        problems = self.deployment_problems()
        if problems:
            listed = "\n".join(f"  - {p}" for p in problems)
            raise ConfigurationError(
                f"{ENV_VAR}=production, but this configuration is not safe to serve "
                f"real interviews:\n{listed}\n"
                f"Set the missing configuration, or run with {ENV_VAR}=dev for local "
                f"work with mock cognition and plaintext storage."
            )

    def posture_banner(self) -> str:
        """One line stating exactly what the operator is running."""
        model = (f"LIVE {self.gemini_model if self.provider == 'gemini' else self.model}"
                 if self.has_live_model else "MOCK (no live model)")
        store = "encrypted" if (self.store_key and cipher_available()) else "PLAINTEXT"
        return f"env={self.runtime.value}  cognition={model}  storage-at-rest={store}"


def load_settings() -> Settings:
    return Settings()


class ModelUnavailable(ConfigurationError):
    """The configured model could not be reached with a trivial request."""


def preflight_model(settings: Settings | None = None) -> str:
    """Make one minimal call to prove the configured model actually answers.

    ``assert_deployable`` checks that configuration is *present*; it deliberately
    touches no network, so it cannot tell a real model id from a plausible
    typo. That gap is how an invalid default model shipped: every offline check
    passed and the first real interview died at turn one with a 404.

    This closes it with the cheapest possible request — a few tokens — and is
    called once at startup, before any employee can reach the system. It is a
    no-op without a live model, since mock mode makes no requests.

    Returns the model id on success. Raises :class:`ModelUnavailable` otherwise,
    naming the model, so the operator learns which id is wrong rather than
    reading a stack trace from inside the SDK.
    """
    settings = settings or load_settings()
    if not settings.has_live_model:
        return "mock"
    from .llm.retry import RetryPolicy

    # One attempt: a wrong model id is permanent, and an overloaded API should not
    # hold up startup for four backoffs. A transient failure here is reported the
    # same way — the operator retries the command.
    client = _build_provider_client(settings, policy=RetryPolicy(attempts=1))
    try:
        client.complete(system="Reply with the single word: ok.",
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=8, temperature=0.0)
    except Exception as exc:
        raise ModelUnavailable(
            f"the configured model {settings.model!r} did not answer a trivial "
            f"request ({type(exc).__name__}: {exc}). Check GROUNDWORK_MODEL names a "
            f"current model and that ANTHROPIC_API_KEY is valid."
        ) from exc
    return settings.model


def _build_provider_client(settings: Settings, policy=None):
    """The live adapter for ``settings.provider`` — the only place it is chosen."""
    if settings.provider == "gemini":
        from .llm.gemini_client import GeminiClient

        return GeminiClient(
            model=settings.gemini_model,
            project=settings.gemini_project or "",
            location=settings.gemini_location,
            policy=policy,
        )
    from .llm.client import AnthropicClient

    return AnthropicClient(model=settings.model, api_key=settings.api_key,
                           policy=policy)


def get_llm_client(settings: Settings | None = None):
    """Return a live LLM client, or ``None`` to signal mock mode.

    Returning ``None`` in development is deliberate: the whole loop must run offline
    for tests and the synthetic testbed. In production the same situation is an
    error, not a fallback.
    """
    settings = settings or load_settings()
    if not settings.has_live_model:
        if settings.is_production:
            raise ConfigurationError(
                f"{ENV_VAR}=production requires a live model (ANTHROPIC_API_KEY, or "
                f"GROUNDWORK_PROVIDER=gemini with GOOGLE_APPLICATION_CREDENTIALS); "
                f"refusing to fall back to the scripted mock interviewer."
            )
        return None
    from .llm.cache import wrap_if_caching

    client = _build_provider_client(settings)
    # Deterministic calls (tagging, entailment, relation classification) are served
    # from cache; the interview loop samples and is never cached. Wrapping here means
    # every caller benefits without knowing the cache exists.
    cache_model = (settings.gemini_model if settings.provider == "gemini"
                   else settings.model)
    return wrap_if_caching(client, settings.derived_store(), model=cache_model,
                           enabled=settings.cache_derived)
