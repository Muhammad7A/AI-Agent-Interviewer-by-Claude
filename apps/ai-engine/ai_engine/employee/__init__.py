"""The employee interview surface: append-only, one interview, nothing else.

A separate ASGI app from the consultant workspace so the boundary is structural — the
routes that would expose other people's testimony are not merely guarded here, they do
not exist.

``create_employee_app`` is resolved lazily so this package imports without FastAPI
installed (see ``tests/test_import_contract.py``).
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .app import create_employee_app

__all__ = ["create_employee_app"]


def __getattr__(name: str):
    if name == "create_employee_app":
        from .app import create_employee_app as _factory

        return _factory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
