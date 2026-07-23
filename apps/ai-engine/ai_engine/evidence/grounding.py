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


def _locate(haystack: str, needle: str) -> tuple[int, int, str] | None:
    """Return (start, end, match_kind) of ``needle`` within ``haystack``, or None.

    Tries an exact substring first, then a flexible match that tolerates only
    differences in whitespace and letter case — both of which still yield precise
    offsets into the original text. Nothing looser is allowed.
    """
    needle = needle.strip()
    if not needle:
        return None

    idx = haystack.find(needle)
    if idx >= 0:
        return idx, idx + len(needle), "exact"

    tokens = [t for t in re.split(r"\s+", needle) if t]
    if not tokens:
        return None
    pattern = r"\s+".join(re.escape(t) for t in tokens)
    match = re.search(pattern, haystack, flags=re.IGNORECASE)
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
                ref=EvidenceRef(segment_id=seg.id, start=start, end=end),
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
