"""Matching a piece of text to a known latent truth.

Ground-truth scoring must tolerate paraphrase (a live model won't quote the
persona verbatim) without being so loose it credits unrelated text. A verbatim
containment of the truth's statement is a strong match; otherwise we fall back to
keyword overlap above a threshold.
"""
from __future__ import annotations

import re

from ..subjects.simulated import LatentTruth

# A finding/segment must clear this keyword-overlap score to count as a match,
# unless it verbatim-contains the truth's statement (which always wins).
MATCH_THRESHOLD = 2
_STATEMENT_SCORE = 1000


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _kw_hits(keyword: str, low: str) -> bool:
    """Whether a truth keyword occurs as the start of a word in ``low``.

    Keywords are stems ("summar", "repetit"), so there is deliberately no
    trailing boundary — but there must be a LEADING one, or the shadow-AI
    truth's keyword "ai" fired inside "email/said/fail/wait" and a sentence
    with no AI content marked the truth as elicited. In live mode every recall,
    precision, and candor number flows through this matcher.
    """
    return re.search(rf"(?<!\w){re.escape(keyword.lower())}", low) is not None


def match_score(text: str, truth: LatentTruth) -> int:
    low = _norm(text)
    statement = _norm(truth.statement)
    if statement and statement in low:
        return _STATEMENT_SCORE
    return sum(1 for kw in truth.keywords if _kw_hits(kw, low))


def truth_in_texts(truth: LatentTruth, texts: list[str]) -> bool:
    return any(match_score(t, truth) >= MATCH_THRESHOLD for t in texts)


def assign_findings_to_truths(
    finding_texts: list[str], truths: list[LatentTruth]
) -> tuple[set[str], set[int]]:
    """Greedy best-match. Returns (captured truth ids, matched finding indices).

    Each finding matches at most one truth and each truth is captured by at most
    one finding, so a single verbose finding can't 'cover' the whole truth set.
    """
    triples: list[tuple[int, int, str]] = []
    for i, text in enumerate(finding_texts):
        for truth in truths:
            score = match_score(text, truth)
            if score >= MATCH_THRESHOLD:
                triples.append((score, i, truth.id))
    triples.sort(key=lambda x: x[0], reverse=True)

    used_findings: set[int] = set()
    captured_truths: set[str] = set()
    for _score, i, truth_id in triples:
        if i in used_findings or truth_id in captured_truths:
            continue
        used_findings.add(i)
        captured_truths.add(truth_id)
    return captured_truths, used_findings
