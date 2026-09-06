"""The zero-dependency import contract.

The package advertises that it imports and runs with no third-party dependencies —
that is what makes the CLI, the eval harness, the fuzz audit and the synthetic testbed
usable anywhere, and it is what CI relies on.

Adding the web app broke it: ``ai_engine/webapp/__init__.py`` eagerly imported
``.app``, which imports FastAPI, so merely importing ``ai_engine.persistence.ledger``
required an optional dependency and CI went red.

These tests run in a subprocess with the optional packages made unimportable, which is
the only honest way to check the contract from inside a process where they are already
loaded.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
import unittest

# Everything that must remain importable with nothing installed.
CORE_MODULES = (
    "ai_engine",
    "ai_engine.config",
    "ai_engine.cli",
    "ai_engine.interview.driver",
    "ai_engine.interview.session",
    "ai_engine.transcript.model",
    "ai_engine.evidence.grounding",
    "ai_engine.evidence.tagger",
    "ai_engine.validation.gate",
    "ai_engine.privacy",
    "ai_engine.persistence.transcript_store",
    "ai_engine.persistence.crypto",
    "ai_engine.report.generator",
    "ai_engine.eval.runner",
    "ai_engine.aggregation.aggregator",
    "ai_engine.confidence.scorer",
    "ai_engine.synthetic.generator",
    "ai_engine.fuzz.runner",
    "ai_engine.persistence.invitations",
    "ai_engine.persistence.session_store",
    "ai_engine.persistence.derived_store",
    "ai_engine.llm.cache",
    "ai_engine.llm.retry",
    # The web packages' non-web parts must not drag FastAPI in.
    "ai_engine.webapp",
    "ai_engine.persistence.ledger",
    "ai_engine.employee",
)

_BLOCKED = ("fastapi", "starlette", "uvicorn", "httpx", "pydantic", "multipart",
            "anthropic", "cryptography")

# Modern MetaPathFinder protocol (find_spec) is required on Python 3.12+.
# The legacy find_module / load_module pair is no longer consulted for ordinary
# top-level imports, so a blocker written against the old protocol silently
# fails to intercept and the contract tests become no-ops.
_SCRIPT = textwrap.dedent(
    """
    import sys
    from importlib.machinery import ModuleSpec

    BLOCKED = {blocked!r}

    class _Blocker:
        def find_spec(self, name, path=None, target=None):
            if name.split(".")[0] in BLOCKED:
                return ModuleSpec(name, self)
            return None

        def create_module(self, spec):
            return None

        def exec_module(self, module):
            raise ImportError("blocked: " + module.__name__)

    sys.meta_path.insert(0, _Blocker())

    import importlib
    for module in {modules!r}:
        importlib.import_module(module)
    print("OK")
    """
)


def _run_isolated(modules: tuple[str, ...]) -> subprocess.CompletedProcess:
    script = _SCRIPT.format(blocked=set(_BLOCKED), modules=modules)
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=120,
    )


class ImportContractTest(unittest.TestCase):
    def test_core_imports_without_any_optional_dependency(self):
        result = _run_isolated(CORE_MODULES)
        self.assertIn("OK", result.stdout,
                      f"import failed with optional deps blocked:\n{result.stderr}")

    def test_each_module_individually(self):
        # Import one at a time, so a failure names the offending module rather than
        # leaving the whole list suspect.
        for module in CORE_MODULES:
            with self.subTest(module=module):
                result = _run_isolated((module,))
                self.assertIn("OK", result.stdout,
                              f"{module} requires an optional dependency:\n{result.stderr}")

    def test_the_blocker_actually_blocks(self):
        # Guards the guard: if the blocker were ineffective, the tests above would
        # pass regardless and prove nothing.
        result = _run_isolated(("fastapi",))
        self.assertNotIn("OK", result.stdout)
        self.assertIn("blocked", result.stderr)

    # NOTE: the counterpart assertion — that lazy resolution has not broken
    # `from ai_engine.webapp import create_app` — lives in test_webapp.py, because it
    # requires FastAPI. This module must stay runnable on a bare interpreter, since
    # that is the whole contract it exists to check.


if __name__ == "__main__":
    unittest.main()
