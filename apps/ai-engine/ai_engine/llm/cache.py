"""Caching for deterministic model calls.

The cache boundary is **temperature**, and that is a principled line rather than a
convenient one:

  * At ``temperature = 0`` the provider is being asked for its single best answer.
    Calling twice with identical input is a request for the same thing twice, so
    reusing the first answer changes nothing about behaviour — only about cost and
    latency. Tagging, entailment and relation classification all run at 0.
  * Above 0 the caller is deliberately sampling. The interview loop runs at 0.4
    because an interviewer that asks a scripted question to every participant is not
    an interviewer. Caching there would silently replace variation with repetition,
    which is a behaviour change disguised as an optimisation — so it is refused.

The effect is that the derived pipeline stops being recomputed on every page view
while the interview itself stays live.
"""
from __future__ import annotations

import json
from typing import Callable

from ..persistence.derived_store import DerivedStore, content_key
from .client import LLMClient, Message


class CachingLLMClient:
    """Wraps an :class:`LLMClient`, reusing answers for deterministic calls."""

    def __init__(
        self,
        inner: LLMClient,
        store: DerivedStore,
        *,
        model: str,
        enabled: bool = True,
    ) -> None:
        self._inner = inner
        self._store = store
        self._model = model
        self._enabled = enabled

    @property
    def store(self) -> DerivedStore:
        return self._store

    @property
    def inner(self) -> LLMClient:
        return self._inner

    def _key(self, system: str, messages: list[Message], max_tokens: int) -> str:
        # The model is part of the key: one model's answers must never be served for
        # another's. Prompt text is included in full, so a prompt edit invalidates
        # its own entries rather than silently reusing the previous behaviour.
        return content_key(
            "llm.complete", self._model, max_tokens, system,
            json.dumps(messages, ensure_ascii=False, sort_keys=True),
        )

    def complete(
        self,
        *,
        system: str,
        messages: list[Message],
        max_tokens: int = 1024,
        temperature: float = 0.4,
    ) -> str:
        deterministic = self._enabled and temperature == 0.0
        if not deterministic:
            return self._inner.complete(
                system=system, messages=messages,
                max_tokens=max_tokens, temperature=temperature)

        key = self._key(system, messages, max_tokens)
        cached = self._store.get(key)
        if cached is not None and isinstance(cached.get("text"), str):
            return cached["text"]

        text = self._inner.complete(
            system=system, messages=messages,
            max_tokens=max_tokens, temperature=temperature)
        # A failed call raises before reaching here, so failures are never cached —
        # a transient outage must not become a permanently empty answer.
        self._store.put(key, {"text": text})
        return text


def wrap_if_caching(
    client: LLMClient | None,
    store: DerivedStore | None,
    *,
    model: str,
    enabled: bool = True,
) -> LLMClient | None:
    """Wrap ``client`` when there is somewhere to cache. ``None`` stays ``None``."""
    if client is None or store is None or not enabled:
        return client
    return CachingLLMClient(client, store, model=model, enabled=enabled)
