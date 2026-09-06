"""The consultant's application layer — use-cases, headless.

Orchestration that used to live inside HTTP handlers — pseudonymizing a
participant, driving an interview turn-by-turn, finalizing and tagging a
transcript, recording validation decisions, releasing through the privacy
firewall — lives here, once, testable without a web server. Routes and CLIs
are thin over it (Art. XV: one behavior, one home).
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .service import ConsultantService

__all__ = ["ConsultantService"]


def __getattr__(name: str):
    # PEP 562, same pattern as the webapp package: importing this package must
    # not require FastAPI or any other optional dependency.
    if name == "ConsultantService":
        from .service import ConsultantService as _cls

        return _cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
