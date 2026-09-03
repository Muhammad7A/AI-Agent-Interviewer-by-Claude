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
difference is made explicit: ``ONTORA_ENV=production`` refuses to start unless a real
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

# Default to a current Claude model; override with ONTORA_MODEL.
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
# classification work. Set ONTORA_MODEL to a larger model if interview cognition
# needs it — that is a one-variable change.
DEFAULT_MODEL = os.environ.get("ONTORA_MODEL", "claude-sonnet-5")

ENV_VAR = "ONTORA_ENV"


class Runtime(str, Enum):
    #: Local development and tests. Mock cognition and plaintext storage allowed.
    DEV = "dev"
    #: A real deployment talking to real employees. Neither is allowed.
    PRODUCTION = "production"


class ConfigurationError(RuntimeError):
    """Raised when the runtime is not safe to serve real interviews."""


def runtime_from_env() -> Runtime:
    """Parse ``ONTORA_ENV`` — and refuse an unrecognized value.

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
    cache_derived: bool = os.environ.get("ONTORA_CACHE", "1") not in ("0", "false", "no")
    max_turns: int = int(os.environ.get("ONTORA_MAX_TURNS", "14"))
    temperature: float = float(os.environ.get("ONTORA_TEMPERATURE", "0.4"))
    data_dir: Path = Path(os.environ.get("ONTORA_DATA_DIR", "data/interviews"))

    @property
    def has_live_model(self) -> bool:
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
                "no ANTHROPIC_API_KEY: cognition would silently fall back to the "
                "scripted mock interviewer, serving fabricated interviews to real "
                "people and recording them as genuine testimony"
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
        model = f"LIVE {self.model}" if self.has_live_model else "MOCK (no API key)"
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
    from .llm.client import AnthropicClient
    from .llm.retry import RetryPolicy

    # One attempt: a wrong model id is permanent, and an overloaded API should not
    # hold up startup for four backoffs. A transient failure here is reported the
    # same way — the operator retries the command.
    client = AnthropicClient(
        model=settings.model,
        api_key=settings.api_key,
        policy=RetryPolicy(attempts=1),
    )
    try:
        client.complete(system="Reply with the single word: ok.",
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=8, temperature=0.0)
    except Exception as exc:
        raise ModelUnavailable(
            f"the configured model {settings.model!r} did not answer a trivial "
            f"request ({type(exc).__name__}: {exc}). Check ONTORA_MODEL names a "
            f"current model and that ANTHROPIC_API_KEY is valid."
        ) from exc
    return settings.model


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
                f"{ENV_VAR}=production requires ANTHROPIC_API_KEY; refusing to fall "
                f"back to the scripted mock interviewer."
            )
        return None
    from .llm.cache import wrap_if_caching
    from .llm.client import AnthropicClient

    client = AnthropicClient(model=settings.model, api_key=settings.api_key)
    # Deterministic calls (tagging, entailment, relation classification) are served
    # from cache; the interview loop samples and is never cached. Wrapping here means
    # every caller benefits without knowing the cache exists.
    return wrap_if_caching(client, settings.derived_store(), model=settings.model,
                           enabled=settings.cache_derived)
