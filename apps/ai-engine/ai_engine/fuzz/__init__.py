"""Adversarial / property-based auditing of the safety gates.

The product's entire credibility rests on two gates: **grounding** (is the quote
real?) and **entailment** (does the quote support the claim?). Both can fail in two
opposite directions, and the two failures cost very different things:

  * **False accept** — a fabrication is admitted. This is the dangerous direction:
    it puts an unsourced or unsupported claim in front of a consultant, which is the
    confabulation risk (F4) and the legal-exposure risk (F5).
  * **False reject** — a true quote is refused. This silently destroys recall and
    would make the evaluation harness report a worse system than we have.

Example-based tests check the cases an author thought of. This module instead
generates thousands of *near-misses* — the same words with different characters, or
almost the same words — and asserts a property that must hold for all of them.

The key to making it rigorous is knowing the expected answer independently:

  * A **cosmetic** mutation changes only characters (curly quotes, dashes, case,
    whitespace, trailing punctuation). The words are unchanged by construction, so
    it MUST still ground.
  * A **semantic** mutation changes the words (substitute, delete, insert, negate,
    swap, renumber). It MUST NOT ground — verified against a simple token-sequence
    precondition, and skipped rather than asserted in the rare case the mutation
    coincidentally still appears in the source.
"""

from .mutations import (
    COSMETIC_MUTATORS,
    SEMANTIC_MUTATORS,
    CosmeticMutator,
    SemanticMutator,
)
from .runner import FuzzReport, Violation, run_fuzz

__all__ = [
    "COSMETIC_MUTATORS",
    "CosmeticMutator",
    "FuzzReport",
    "SEMANTIC_MUTATORS",
    "SemanticMutator",
    "Violation",
    "run_fuzz",
]
