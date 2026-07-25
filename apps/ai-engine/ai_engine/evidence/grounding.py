"""Deterministic grounding verification — the confabulation filter (F4).

Given a proposal with a quote, try to *locate* that quote in the immutable
transcript and turn it into a real :class:`EvidenceRef`. This is intentionally
NOT the model's job and does not trust the model: if the quote cannot be found in
a subject segment, the claim is rejected. Strict matching (exact, then
flexible whitespace/case only — never fuzzy paraphrase) is a feature: better to
reject a real claim than to accept a paraphrase as verbatim evidence.

Rules enforced here:
  * A quote must resolve to a **subject** segment. A quote that only matches an
    interviewer question is rejected (guards against the model citing its own
    leading question as proof — F8).
  * The resulting EvidenceRef points at the *actual* original span, so
    ``.resolve()`` always returns real immutable source text.
"""
from __future__ import annotations

import re
import uuid

from ..transcript.model import EvidenceRef, Speaker, Transcript
from .model import (
    Claim,
    ClaimStatus,
    ClaimType,
    GroundedEvidence,
    GroundingReport,
    RawProposal,
    RejectedProposal,
    TaggingResult,
)


# Unicode characters a model commonly substitutes when it echoes a quote:
# curly quotes for straight, en/em dashes for hyphen, exotic spaces. Each maps to
# exactly ONE ascii character so the mapping is length-preserving — which means an
# offset in the canonicalized text is the SAME offset in the original text, so the
# resulting EvidenceRef still points at real immutable source.
_CANON: dict[str, str] = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",  # ' ' ‚ ‛
    "“": '"', "”": '"', "„": '"', "‟": '"',  # " " „ ‟
    "‐": "-", "‑": "-", "‒": "-", "–": "-",   # ‐ ‑ ‒ –
    "—": "-", "―": "-", "−": "-",                   # — ― −
    " ": " ", " ": " ", " ": " ", " ": " ",   # nbsp, thin spaces
    " ": " ", "\t": " ",
}


def _canon_char(ch: str) -> str:
    mapped = _CANON.get(ch, ch)
    lowered = mapped.lower()
    # Keep it length-preserving: a rare char that lowercases to >1 char is left as-is.
    return lowered if len(lowered) == 1 else mapped


def _canon(text: str) -> str:
    return "".join(_canon_char(c) for c in text)


def _word_char(ch: str) -> bool:
    return ch.isalnum() or ch == "_"


def _guard(pattern: str, first: str, last: str) -> str:
    """Wrap ``pattern`` so it cannot match the middle of a word.

    Without this, a fabricated quote can match a *word fragment*: "vendor I" was
    accepted against "vendor **i**gnores each deadline", producing evidence that
    pointed at half a word. Found by the fuzz audit.

    The guards are applied only on sides where the needle itself starts/ends with a
    word character — a quote that legitimately begins with punctuation ("— pretty")
    must not be over-constrained.
    """
    pre = r"(?<!\w)" if first and _word_char(first) else ""
    post = r"(?!\w)" if last and _word_char(last) else ""
    return f"{pre}{pattern}{post}"


def _search(literal_or_pattern: str, haystack: str, *, first: str, last: str,
            escape: bool = True) -> re.Match[str] | None:
    body = re.escape(literal_or_pattern) if escape else literal_or_pattern
    return re.search(_guard(body, first, last), haystack)


def _locate(haystack: str, needle: str) -> tuple[int, int, str] | None:
    """Return (start, end, match_kind) of ``needle`` within ``haystack``, or None.

    Strictness is the whole point of the confabulation filter: we accept a quote
    only if it is the *same words* as the source. We DO tolerate differences that
    are purely character-encoding — unicode punctuation, letter case, whitespace,
    and trailing punctuation — because a real model routinely re-emits a true quote
    with curly quotes or an em-dash, and rejecting that true quote would punish
    honesty. We do NOT tolerate paraphrase: change a word and it will not ground.

    Every path is word-boundary guarded, so a quote must align to whole words in the
    source — evidence that points at a fragment of a different word is not evidence.
    """
    needle = needle.strip()
    if not needle:
        return None

    # 1. Exact substring — the fast, unambiguous path.
    match = _search(needle, haystack, first=needle[0], last=needle[-1])
    if match:
        return match.start(), match.end(), "exact"

    # Canonicalize both (length-preserving, so offsets still map to the original).
    chay, cneedle = _canon(haystack), _canon(needle)

    # 2. Same words after unicode/case normalization, ignoring trailing punctuation.
    cneedle_core = cneedle.rstrip(" .,;:!?\"'-")
    for probe in (cneedle, cneedle_core):
        if not probe:
            continue
        match = _search(probe, chay, first=probe[0], last=probe[-1])
        if match:
            return match.start(), match.end(), "normalized"

    # 3. Same words but a different amount of whitespace between them.
    tokens = [t for t in re.split(r"\s+", cneedle_core or cneedle) if t]
    if tokens:
        pattern = r"\s+".join(re.escape(t) for t in tokens)
        match = _search(pattern, chay, first=tokens[0][0], last=tokens[-1][-1],
                        escape=False)
        if match:
            return match.start(), match.end(), "flexible"
    return None


def ground_proposal(
    proposal: RawProposal, transcript: Transcript
) -> tuple[Claim | None, str]:
    """Attempt to ground one proposal. Returns (claim_or_None, reason)."""
    quote = (proposal.quote or "").strip()
    if not quote:
        return None, "empty_quote"

    subject_segments = [s for s in transcript.segments if s.speaker is Speaker.SUBJECT]

    # If the tagger hinted a segment id, try it first — but do not trust it: if
    # the quote is not there, keep searching, since a mis-attributed id with a
    # real quote should still ground where the words actually are.
    ordered = subject_segments
    if proposal.segment_hint:
        hinted = [s for s in subject_segments if s.id == proposal.segment_hint]
        ordered = hinted + [s for s in subject_segments if s.id != proposal.segment_hint]

    for seg in ordered:
        found = _locate(seg.text, quote)
        if found:
            start, end, kind = found
            evidence = GroundedEvidence(
                ref=EvidenceRef(segment_id=seg.id, start=start, end=end,
                                transcript_id=transcript.id),
                quote=quote,
                match_kind=kind,
            )
            claim = Claim(
                id=f"clm-{uuid.uuid4().hex[:12]}",
                claim_type=ClaimType.coerce(proposal.claim_type),
                statement=proposal.statement.strip(),
                evidence=(evidence,),
                speaker=Speaker.SUBJECT,
                tier=max(0, min(4, int(proposal.tier or 0))),
            )
            return claim, "grounded"

    # The quote isn't in any subject segment. If it matches an interviewer
    # segment, that's a red flag — the model is citing the question, not testimony.
    for seg in transcript.segments:
        if seg.speaker is Speaker.INTERVIEWER and _locate(seg.text, quote):
            return None, "cited_interviewer_not_subject"

    return None, "quote_not_found"


def ground_proposals(
    proposals: list[RawProposal], transcript: Transcript
) -> TaggingResult:
    """Ground a batch of proposals into a TaggingResult with a report."""
    claims: list[Claim] = []
    rejected: list[RejectedProposal] = []
    for proposal in proposals:
        claim, reason = ground_proposal(proposal, transcript)
        if claim is not None:
            claims.append(claim)
        else:
            rejected.append(RejectedProposal(proposal=proposal, reason=reason))
    report = GroundingReport(total=len(proposals), grounded=len(claims), rejected=rejected)
    return TaggingResult(claims=claims, report=report)
