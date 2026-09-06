"""The consultant workspace — a local web app over the existing pipeline.

Deliberately **consultant-only**. The employer never gets a login; they receive a
generated, firewalled document. That keeps the privacy boundary a property of the
architecture rather than a permissions checkbox that a future feature can tick.

The app adds no domain logic. It is a surface over what already exists —
``InterviewDriver``, ``TranscriptStore``, ``EvidenceTagger``, ``ValidationGate``,
``privacy.release`` — so the guarantees it presents are the ones the engine actually
enforces, not a second implementation of them.

**Optional dependency, so optional must mean optional.** ``create_app`` is resolved
lazily: importing ``ai_engine.persistence.ledger`` (or anything else in the package) must
not require FastAPI, or the engine stops importing on a machine that only wants the
CLI. Eagerly importing ``.app`` here broke exactly that and turned CI red.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .app import create_app

__all__ = ["create_app"]


def __getattr__(name: str):
    # PEP 562: keeps `from ai_engine.webapp import create_app` working while leaving
    # the package importable without the web extra installed.
    if name == "create_app":
        from .app import create_app as _create_app

        return _create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
