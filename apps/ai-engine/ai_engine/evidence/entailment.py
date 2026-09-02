"""Entailment checking — the second verification gate.

Grounding proves the quote is *real*. Entailment proves the quote *supports the
claim*. They are different, and the gap is a real soundness hole: a model can
quote a genuine sentence ("I use my personal ChatGPT to draft summaries") and
staple a fabricated claim to it ("the employee admitted leaking customer data").
The quote grounds perfectly; the claim is invented. Grounding alone would pass it.

So every grounded claim must also pass an entailment check: does the claim assert
anything *beyond* what the quote says? If it over-reaches — adds severity,
accusations, named parties, or facts not in the quote — it is rejected as a
semantic confabulation.

The strong version of this is a natural-language-entailment judgement that needs a
live model (``LlmEntailmentChecker``). Offline we use a deliberately *conservative*
heuristic (``HeuristicEntailmentChecker``) that catches the three mechanical
inversions — an accusation the quote never made, a polarity flip, and an invented
figure — without pretending to full NLI.

The offline checker is a floor, not a ceiling. It compares word membership and
surface cues, so a fluent paraphrase that changes scope or subject still passes.
A trained fact-checking model (MiniCheck, AlignScore) drops in behind the same
``EntailmentChecker`` Protocol and is the intended production answer.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from ..lexicon import invents_quantity, negation_disagrees
from ..llm.client import LLMClient
from ..transcript.model import Transcript
from .model import Claim


class Entailment(str, Enum):
    SUPPORTED = "supported"
    NOT_SUPPORTED = "not_supported"


@dataclass(frozen=True)
class EntailmentResult:
    verdict: Entailment
    reason: str
    method: str  # "heuristic" | "llm"


@dataclass
class EntailmentReject:
    claim: Claim
    reason: str


@runtime_checkable
class EntailmentChecker(Protocol):
    def check(self, statement: str, quote: str) -> EntailmentResult: ...


# --- the conservative offline heuristic -----------------------------------

# Accusatory / legal stems. If a claim asserts one of these and the quote does
# NOT contain it, the claim has escalated beyond its evidence — the dangerous,
# legally-radioactive case (F5). Kept narrow to avoid false positives on ordinary
# words (e.g. we do NOT include generic terms like "data" or "customer").
_SEVERE_STEMS = (
    "illeg", "fraud", "leak", "stol", "steal", "theft", "embezzl", "brib",
    "kickback", "harass", "discrimin", "lawsuit", "misconduct", "breach",
    "violat", "confidential", "sabotag", "launder", "forg", "coverup",
)

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "for", "is",
    "are", "was", "were", "be", "been", "it", "its", "that", "this", "with",
    "as", "at", "by", "so", "we", "i", "they", "he", "she", "you", "my", "our",
    "their", "his", "her", "them", "about", "because", "than", "then", "just",
    "really", "very", "some", "any", "all", "not", "no", "do", "does", "did",
    "have", "has", "had", "from", "up", "out", "into", "over", "before", "after",
}

_MIN_OVERLAP = 0.30


def _content_words(text: str) -> set[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in _STOPWORDS}


def _severe_stem(word: str) -> str | None:
    for stem in _SEVERE_STEMS:
        if stem in word:
            return stem
    return None


class HeuristicEntailmentChecker:
    """Offline, conservative. Rejects escalation, polarity inversion, invented
    quantities, and near-zero overlap.

    It is a **smoke test, not a substitute for entailment.** It reasons about word
    membership, polarity cues and figures — never about meaning — so a paraphrase
    that reverses a claim's scope or subject will pass it. Treat a SUPPORTED
    verdict from this checker as "no mechanical inversion detected", not as
    "verified". Where a real judgement is required, supply an
    :class:`LlmEntailmentChecker` (or a trained NLI model behind the same
    Protocol) via :func:`make_checker`.
    """

    def check(self, statement: str, quote: str) -> EntailmentResult:
        claim_words = _content_words(statement)
        quote_words = _content_words(quote)

        # 1. Escalation: a serious/accusatory term in the claim, absent from the quote.
        for word in claim_words:
            stem = _severe_stem(word)
            if stem and not any(stem in qw for qw in quote_words):
                return EntailmentResult(
                    Entailment.NOT_SUPPORTED,
                    f"claim asserts '{word}' with no basis in the quote",
                    "heuristic",
                )

        # 2. Polarity inversion. Word overlap cannot see negation, so "I don't
        # think the approval step is a problem" and "the approval step is a
        # problem" scored as a near-perfect match — the claim asserting the
        # opposite of its own evidence, carrying a genuine verbatim quote. That
        # is the worst output this system can produce, so it is checked before
        # overlap rather than after.
        if negation_disagrees(statement, quote):
            return EntailmentResult(
                Entailment.NOT_SUPPORTED,
                "claim and quote disagree in polarity (one negates, the other does not)",
                "heuristic",
            )

        # 3. Invented quantity. Content words are letters-only, so every figure —
        # a duration, a headcount, a cost — passed unchecked and "three days"
        # could become "thirty days" with the overlap barely moving. Numbers are
        # what become business cases downstream, so a figure the quote does not
        # contain is a fabrication regardless of how well the words match.
        invented = invents_quantity(statement, quote)
        if invented is not None:
            return EntailmentResult(
                Entailment.NOT_SUPPORTED,
                f"claim asserts the quantity '{invented}', which is not in the quote",
                "heuristic",
            )

        # 4. Near-zero overlap: the claim's words barely appear in the quote.
        if claim_words:
            overlap = len(claim_words & quote_words) / len(claim_words)
            if overlap < _MIN_OVERLAP:
                return EntailmentResult(
                    Entailment.NOT_SUPPORTED,
                    f"claim overlaps the quote only {overlap:.0%}",
                    "heuristic",
                )
        return EntailmentResult(Entailment.SUPPORTED, "claim stays within the quote", "heuristic")


# --- the live model checker ------------------------------------------------

ENTAILMENT_PROMPT_VERSION = "entailment/v0.1"

ENTAILMENT_SYSTEM = """\
You are a strict evidence auditor. You are given a QUOTE (verbatim words an \
employee said) and a CLAIM about it. Decide whether the quote SUPPORTS the claim.

Answer SUPPORTED only if the claim asserts nothing beyond what the quote says or \
plainly implies. Answer NOT_SUPPORTED if the claim adds ANY of: severity or \
accusation not in the quote, named people/teams not in the quote, specific numbers \
not in the quote, or facts the quote does not establish. When in doubt, answer \
NOT_SUPPORTED — an unsupported claim is worse than a missing one.

Return ONLY a JSON object: {"verdict": "SUPPORTED" | "NOT_SUPPORTED", "reason": "short"}.
"""


class LlmEntailmentChecker:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def check(self, statement: str, quote: str) -> EntailmentResult:
        text = self._llm.complete(
            system=ENTAILMENT_SYSTEM,
            messages=[{"role": "user", "content": f'QUOTE: "{quote}"\nCLAIM: "{statement}"'}],
            max_tokens=200,
            temperature=0.0,
        )
        data = _extract_json(text)
        if not data:
            # Fail closed: a grounded claim we could not verify is dropped, not passed.
            return EntailmentResult(Entailment.NOT_SUPPORTED, "unverifiable response", "llm")
        verdict = str(data.get("verdict", "")).strip().upper()
        reason = str(data.get("reason", ""))
        if verdict == "SUPPORTED":
            return EntailmentResult(Entailment.SUPPORTED, reason, "llm")
        return EntailmentResult(Entailment.NOT_SUPPORTED, reason or "not supported", "llm")


def make_checker(llm: LLMClient | None) -> EntailmentChecker:
    return LlmEntailmentChecker(llm) if llm is not None else HeuristicEntailmentChecker()


def apply_entailment(
    claims: list[Claim], transcript: Transcript, checker: EntailmentChecker
) -> tuple[list[Claim], list[EntailmentReject]]:
    """Second gate: keep only claims whose quote supports them."""
    kept: list[Claim] = []
    rejected: list[EntailmentReject] = []
    for claim in claims:
        quote = claim.evidence[0].resolve(transcript)
        result = checker.check(claim.statement, quote)
        if result.verdict is Entailment.SUPPORTED:
            kept.append(claim)
        else:
            rejected.append(EntailmentReject(claim=claim, reason=result.reason))
    return kept, rejected


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None
