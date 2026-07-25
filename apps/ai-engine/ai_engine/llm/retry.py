"""Retry policy for model calls.

A twenty-turn interview with twenty people is roughly four hundred model calls. Some
of them will fail: rate limits, overload, a dropped connection. Without retries the
first blip ends someone's interview at turn twelve — which does not merely lose data,
it spends the trust the whole candour experiment depends on.

Two failures must be told apart. A **transient** failure (429, 5xx, timeout, connection
reset) should be retried with backoff. A **permanent** one (bad key, malformed request)
should fail immediately: retrying a 401 twenty times just makes the operator wait
longer to learn their key is wrong.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

T = TypeVar("T")


class LLMError(RuntimeError):
    """Base class for model-call failures."""


class PermanentLLMError(LLMError):
    """Retrying will not help — bad credentials, malformed request."""


class TransientLLMError(LLMError):
    """Worth another attempt — rate limit, overload, timeout, connection reset."""


class LLMUnavailable(LLMError):
    """Every attempt failed. Carries the last cause for the operator."""

    def __init__(self, attempts: int, cause: BaseException) -> None:
        super().__init__(
            f"the model was unreachable after {attempts} attempt(s): "
            f"{type(cause).__name__}: {cause}"
        )
        self.attempts = attempts
        self.cause = cause


# Status codes worth another attempt. 529 is Anthropic's "overloaded".
_TRANSIENT_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}
_PERMANENT_STATUS = {400, 401, 403, 404, 405, 422}

_TRANSIENT_NAMES = (
    "timeout", "connection", "overloaded", "ratelimit", "rate_limit",
    "apistatus", "internalserver", "serviceunavailable", "remoteprotocol",
)


def classify(exc: BaseException) -> LLMError:
    """Decide whether ``exc`` is worth retrying, without importing provider types.

    Duck-typed on purpose: the classification must not require the SDK to be
    installed, and must keep working if the provider reorganises its exceptions.
    """
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if isinstance(status, int):
        if status in _PERMANENT_STATUS:
            return PermanentLLMError(f"{status}: {exc}")
        if status in _TRANSIENT_STATUS or 500 <= status < 600:
            return TransientLLMError(f"{status}: {exc}")

    name = type(exc).__name__.lower()
    if any(marker in name for marker in _TRANSIENT_NAMES):
        return TransientLLMError(str(exc))
    if isinstance(exc, (TimeoutError, ConnectionError, OSError)):
        return TransientLLMError(str(exc))

    # Unknown failures are treated as transient but stay inside the same bounded
    # budget, so an unexpected error gets a second chance without looping forever.
    return TransientLLMError(f"{type(exc).__name__}: {exc}")


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 4
    base_delay: float = 0.5
    max_delay: float = 8.0
    #: Full jitter. Without it, concurrent interviews retry in lockstep and
    #: re-create the burst that caused the rate limit.
    jitter: bool = True

    def delay_for(self, attempt: int, rng: random.Random | None = None) -> float:
        raw = min(self.max_delay, self.base_delay * (2 ** max(0, attempt - 1)))
        if not self.jitter:
            return raw
        return (rng or random).uniform(0.0, raw)


def call_with_retries(
    fn: Callable[[], T],
    *,
    policy: RetryPolicy | None = None,
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Callable[[int, LLMError, float], None] | None = None,
    rng: random.Random | None = None,
) -> T:
    """Run ``fn``, retrying transient failures with exponential backoff and jitter."""
    policy = policy or RetryPolicy()
    last: LLMError | None = None
    for attempt in range(1, max(1, policy.attempts) + 1):
        try:
            return fn()
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:  # noqa: BLE001 - classified immediately below
            error = classify(exc)
            if isinstance(error, PermanentLLMError):
                raise error from exc
            last = error
            if attempt >= policy.attempts:
                raise LLMUnavailable(attempt, exc) from exc
            wait = policy.delay_for(attempt, rng)
            if on_retry is not None:
                on_retry(attempt, error, wait)
            sleep(wait)
    raise LLMUnavailable(policy.attempts, last or RuntimeError("unknown"))
