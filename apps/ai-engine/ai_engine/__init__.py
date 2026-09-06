"""Groundwork AI cognition — runnable interview loop (thin slice).

This package is the deliberately-thin, runnable implementation of the interview
cognition capability. It exists to run the Year-0/1 gate experiments (candor,
elicitation superiority, value density, robustness) on real people, not to be
the full hexagonal skeleton under ``src/``.

Design rules it honours (see ``docs/ENGINEERING_CONSTITUTION.md``):
  * C1/C5 — the transcript is immutable and its segments are the finest evidence
    anchors, so every later claim can resolve to an immutable source span.
  * C7 — this slice writes only the *testimony* layer of the learning dataset;
    it never fuses interpretation, validation, or outcome.
  * C10 — cognition and storage are strangers: the engine returns transcripts
    and events; a thin adapter persists them.
"""

__all__ = ["__version__"]

__version__ = "0.0.1"
