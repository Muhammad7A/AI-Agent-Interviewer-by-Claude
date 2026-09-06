"""The evaluation laboratory — measuring the AI behavior, not just running it.

Grader classes are declared, never faked: deterministic (proofs over the
system's own structures), heuristic (computed approximations, labeled as
such), model (requires a live provider; UNSCORED without one).
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type checkers only
    from .runner import SuiteResult, run_suite

__all__ = ["run_suite", "SuiteResult"]


def __getattr__(name: str):
    if name in ("run_suite", "SuiteResult"):
        from . import runner

        return getattr(runner, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
