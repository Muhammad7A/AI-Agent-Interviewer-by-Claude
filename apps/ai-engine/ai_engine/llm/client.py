"""The LLM port and its one live adapter (Anthropic).

Domain/application code depends only on the :class:`LLMClient` protocol; the
concrete provider is chosen in ``config.get_llm_client``. Swapping providers is
an edit to this file plus the factory — nothing else.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

# A minimal chat message. Kept as a plain dict so no provider type leaks upward.
Message = dict[str, str]  # {"role": "user" | "assistant", "content": str}


@runtime_checkable
class LLMClient(Protocol):
    def complete(
        self,
        *,
        system: str,
        messages: list[Message],
        max_tokens: int = 1024,
        temperature: float = 0.4,
    ) -> str:
        """Return the model's text completion for a system prompt + turn history."""
        ...


class AnthropicClient:
    """Live adapter over the Anthropic Messages API.

    The ``anthropic`` import is lazy so the package imports and runs in mock mode
    with the SDK absent.
    """

    def __init__(self, *, model: str, api_key: str | None) -> None:
        self._model = model
        self._api_key = api_key
        self._client = None  # created on first use

    def _ensure_client(self):
        if self._client is None:
            try:
                import anthropic  # type: ignore
            except ImportError as exc:  # pragma: no cover - environment dependent
                raise RuntimeError(
                    "The 'anthropic' package is not installed. Install it with "
                    "`pip install -e '.[live]'`, or run without ANTHROPIC_API_KEY "
                    "to use mock/simulated mode."
                ) from exc
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def complete(
        self,
        *,
        system: str,
        messages: list[Message],
        max_tokens: int = 1024,
        temperature: float = 0.4,
    ) -> str:
        client = self._ensure_client()
        response = client.messages.create(
            model=self._model,
            system=system,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # Concatenate text blocks; ignore non-text content.
        parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        return "".join(parts).strip()
