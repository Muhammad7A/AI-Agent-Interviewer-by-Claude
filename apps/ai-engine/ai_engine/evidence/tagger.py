"""The evidence tagger: propose claims, then ground them deterministically.

Live path: an LLM extracts claim proposals with verbatim quotes. Mock path: a
deterministic keyword tagger that quotes whole subject segments (so its claims
ground by construction) — the honest offline baseline. Both paths emit
:class:`RawProposal`s and funnel through the same grounding verifier, so the
confabulation filter is identical regardless of who proposed the claim.
"""
from __future__ import annotations

import json
import re

from ..llm.client import LLMClient
from ..transcript.model import Speaker, Transcript
from .grounding import ground_proposals
from .model import RawProposal, TaggingResult
from .prompts import TAGGER_SYSTEM, render_tagger_prompt

# Ordered keyword -> (claim_type, tier). First match wins, so more specific /
# higher-value types are listed first.
_MOCK_RULES: list[tuple[tuple[str, ...], str, int]] = [
    (("chatgpt", "not sanctioned", "automat", "repetit", "rules-based"), "ai_opportunity", 2),
    (("approval", "director", "sign off", "routes around", "politics"), "friction", 3),
    (("workaround", "instead", "spreadsheet", "by hand", "manual", "unsanctioned"), "workaround", 2),
    (("waits", "stall", "pile", "bottleneck", "stuck", "delay", "reconciled"), "bottleneck", 2),
    (("redundant", "redone", "rebuild", "four hours", "wasted"), "wasted_effort", 2),
    (("pads", "underutilized", "hide", "status"), "friction", 4),
]

_LOW_SIGNAL = (
    "mostly fine", "nothing jumps out", "pretty standard", "standard stuff",
    "nothing really", "rather not", "prefer not", "not sure",
)


class EvidenceTagger:
    def __init__(self, *, llm: LLMClient | None = None, temperature: float = 0.0) -> None:
        self._llm = llm
        self._temperature = temperature

    @property
    def is_live(self) -> bool:
        return self._llm is not None

    def tag(self, transcript: Transcript) -> TaggingResult:
        proposals = (
            self._live_proposals(transcript)
            if self._llm is not None
            else self._mock_proposals(transcript)
        )
        return ground_proposals(proposals, transcript)

    # -- live path ---------------------------------------------------------
    def _live_proposals(self, transcript: Transcript) -> list[RawProposal]:
        text = self._llm.complete(
            system=TAGGER_SYSTEM,
            messages=[{"role": "user", "content": render_tagger_prompt(transcript.render())}],
            max_tokens=1500,
            temperature=self._temperature,
        )
        return _parse_proposals(text)

    # -- mock path ---------------------------------------------------------
    def _mock_proposals(self, transcript: Transcript) -> list[RawProposal]:
        proposals: list[RawProposal] = []
        for seg in transcript.segments:
            if seg.speaker is not Speaker.SUBJECT:
                continue
            low = seg.text.lower()
            if any(m in low for m in _LOW_SIGNAL) or len(seg.text.split()) < 6:
                continue
            claim_type, tier = _classify(low)
            proposals.append(
                RawProposal(
                    claim_type=claim_type,
                    statement=f"[{claim_type}] {seg.text}",
                    quote=seg.text,          # whole utterance -> grounds exactly
                    tier=tier,
                    segment_hint=seg.id,
                )
            )
        return proposals


def _classify(low_text: str) -> tuple[str, int]:
    for keywords, claim_type, tier in _MOCK_RULES:
        if any(kw in low_text for kw in keywords):
            return claim_type, tier
    return "observation", 1


def _extract_json(text: str) -> dict | None:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    break
    if not candidate:
        return None
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _parse_proposals(text: str) -> list[RawProposal]:
    data = _extract_json(text)
    if not data:
        return []
    out: list[RawProposal] = []
    for item in data.get("claims", []) or []:
        if not isinstance(item, dict):
            continue
        quote = str(item.get("quote", "")).strip()
        if not quote:
            continue  # fail safe: a claim with no quote can never be grounded
        out.append(
            RawProposal(
                claim_type=str(item.get("type", "observation")),
                statement=str(item.get("statement", "")).strip(),
                quote=quote,
                tier=int(item.get("tier", 0) or 0),
                segment_hint=item.get("segment_id"),
            )
        )
    return out
