"""Deciding how two findings relate: agree, conflict, variation, complement.

Offline uses a conservative heuristic — shared topic words plus opposing polarity
cues signal a conflict; strong overlap with matching polarity signals agreement.
It cannot reliably tell *variation* from *complement* (that needs real reasoning),
so offline it defaults the ambiguous case to complement and never invents a
conflict that isn't cued. With a live model, an NLI-style classifier drops in via
the same ``RelationChecker`` seam and can distinguish all four.
"""
from __future__ import annotations

import json
import re
from typing import Protocol, runtime_checkable

from ..lexicon import NEGATION_CUES, quantities
from ..llm.client import LLMClient
from .model import Relation

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for", "is",
    "are", "was", "were", "be", "been", "it", "its", "that", "this", "with",
    "as", "at", "by", "so", "we", "i", "they", "he", "she", "you", "my", "our",
    "their", "his", "her", "them", "about", "than", "then", "just", "really",
    "very", "some", "any", "all", "do", "does", "did", "have", "has", "had",
    "from", "up", "out", "into", "over", "before", "after", "actually",
    "basically", "exactly", "pretty", "here", "there", "us", "get", "gets",
    "getting", "what", "when", "where", "who", "which", "step",
}

# Polarity cues: does the statement assert a thing is happening / true (POS) or
# not happening / broken / absent (NEG)? Opposite polarity on a shared topic = conflict.
#
# The general negation vocabulary is shared with the entailment gate (see
# ``ai_engine.lexicon``) because keeping two private copies is exactly how this
# drifted: this list knew ``can't`` but not ``cannot``, so "Finance cannot close
# the books on time" and "Finance closes the books on time, always" were read as
# AGREE — and the confidence scorer then counted the contradiction as an
# independent corroborating voice. Domain-specific cues that only make sense when
# describing a process ("outdated", "unusable") stay here.
_NEG = NEGATION_CUES + (
    "out of date", "outdated", "ignored", "ignore", "abandon", "unusable",
    "broken", "fails", "fell over", "gave up on",
)
_POS = (
    # Deliberately excludes ambiguous stems like "follow"/"updated": those fire
    # inside their own negation ("nobody follows"), which would read a denial as
    # an affirmation and hide a real contradiction.
    "always", "everyone", "everybody", "up to date", "reliable",
    "consistently", "exactly as", "on time", "by the book",
)


def content_words(text: str) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in _STOPWORDS}


def _polarity(text: str) -> int:
    """+1 asserts the thing happens, -1 denies it, 0 says neither.

    **Negation dominates.** Counting cues and comparing totals let a positive cue
    sitting *inside* a negation cancel it out: "Finance cannot close the books on
    time" scored `on time` as +1 against `cannot` as -1 and came out neutral,
    which read as agreement with "Finance closes the books on time, always". This
    is the same scope trap the `_POS` list already avoids by excluding "follow"
    and "updated" — a denial containing an affirming word is still a denial, so
    the rule belongs in the function rather than in the choice of vocabulary.
    """
    padded = " " + text.lower() + " "
    if any(cue in padded for cue in _NEG):
        return -1
    return 1 if any(cue in padded for cue in _POS) else 0


def overlap_coefficient(a_words: set[str], b_words: set[str]) -> float:
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / min(len(a_words), len(b_words))


@runtime_checkable
class RelationChecker(Protocol):
    def classify(self, a: str, b: str) -> Relation: ...


class HeuristicRelationChecker:
    TOPIC_MIN_SHARED = 2
    TOPIC_MIN_OVERLAP = 0.15
    AGREE_MIN_OVERLAP = 0.50

    def classify(self, a: str, b: str) -> Relation:
        wa, wb = content_words(a), content_words(b)
        shared = wa & wb
        overlap = overlap_coefficient(wa, wb)
        if len(shared) < self.TOPIC_MIN_SHARED or overlap < self.TOPIC_MIN_OVERLAP:
            return Relation.UNRELATED
        pa, pb = _polarity(a), _polarity(b)
        if pa and pb and pa != pb:
            return Relation.CONFLICT
        # One-sided polarity still conflicts. Requiring a cue on *both* sides let
        # a plain assertion ("Finance closes the books on time") agree with its own
        # denial ("Finance cannot close the books on time"), because the
        # unmarked side scores 0 and `pa and pb` short-circuits.
        if (pa < 0) != (pb < 0):
            return Relation.CONFLICT
        # Two people quoting different figures for the same thing disagree, however
        # closely their wording matches: "approvals take three days" and "approvals
        # take thirty days" share every other word.
        qa, qb = quantities(a), quantities(b)
        if qa and qb and qa != qb:
            return Relation.CONFLICT
        if overlap >= self.AGREE_MIN_OVERLAP and pa == pb:
            return Relation.AGREE
        return Relation.COMPLEMENT


RELATION_PROMPT_VERSION = "relation/v0.1"

RELATION_SYSTEM = """\
You compare two statements from different employees about their organization and \
decide how they relate. Choose exactly one:
- AGREE: they assert the same thing (corroboration).
- CONFLICT: they cannot both be true (a real disagreement to investigate).
- VARIATION: both can be true but differ by team, role, or context.
- COMPLEMENT: both true and additive — they describe different parts of one thing.
- UNRELATED: they are not about the same thing.
Return ONLY JSON: {"relation": "AGREE|CONFLICT|VARIATION|COMPLEMENT|UNRELATED", "reason": "short"}.
"""


class LlmRelationChecker:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def classify(self, a: str, b: str) -> Relation:
        text = self._llm.complete(
            system=RELATION_SYSTEM,
            messages=[{"role": "user", "content": f'A: "{a}"\nB: "{b}"'}],
            max_tokens=150,
            temperature=0.0,
        )
        data = _extract_json(text)
        if not data:
            return Relation.UNRELATED
        try:
            return Relation(str(data.get("relation", "unrelated")).strip().lower())
        except ValueError:
            return Relation.UNRELATED


def make_relation_checker(llm: LLMClient | None) -> RelationChecker:
    return LlmRelationChecker(llm) if llm is not None else HeuristicRelationChecker()


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None
