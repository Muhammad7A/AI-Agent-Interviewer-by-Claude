"""Runtime configuration and the LLM-client factory.

Nothing in ``interview/`` or ``transcript/`` names a model or an SDK — that is an
infrastructure concern that lives here (Constitution: the LLM sits behind a
port; a provider change is an infrastructure-only change).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


# Default to a current Claude model; override with ONTORA_MODEL. The engine and
# subjects fall back to deterministic mock behaviour when no client is available,
# so the package always runs.
DEFAULT_MODEL = os.environ.get("ONTORA_MODEL", "claude-opus-4-8")


@dataclass(frozen=True)
class Settings:
    model: str = DEFAULT_MODEL
    api_key: str | None = os.environ.get("ANTHROPIC_API_KEY") or None
    max_turns: int = int(os.environ.get("ONTORA_MAX_TURNS", "14"))
    temperature: float = float(os.environ.get("ONTORA_TEMPERATURE", "0.4"))
    data_dir: Path = Path(os.environ.get("ONTORA_DATA_DIR", "data/interviews"))

    @property
    def has_live_model(self) -> bool:
        return bool(self.api_key)


def load_settings() -> Settings:
    return Settings()


def get_llm_client(settings: Settings | None = None):
    """Return a live LLM client, or ``None`` to signal mock mode.

    Returning ``None`` (rather than raising) is deliberate: the whole loop must
    run offline for tests, CI, and the synthetic-org testbed.
    """
    settings = settings or load_settings()
    if not settings.has_live_model:
        return None
    from .llm.client import AnthropicClient

    return AnthropicClient(model=settings.model, api_key=settings.api_key)
