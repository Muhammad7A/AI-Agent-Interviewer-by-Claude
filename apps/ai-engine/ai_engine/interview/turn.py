"""The interviewer's per-turn structured output, and a defensive parser.

Each turn the model returns JSON: an assessment of the subject's *last* answer,
the next move (hypothesis + technique + target tier), a close decision, and the
actual utterance to say. Parsing is defensive — a malformed response degrades to
"say the raw text, assess nothing" rather than crashing the interview
(Constitution Art. XVI: no hidden failure; fail safe).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field


@dataclass
class Assessment:
    got_substantive_disclosure: bool = False
    tier_reached: int = 0
    specificity: str = "none"  # none | vague | concrete
    candor_signal: str = "neutral"  # guarded | neutral | open
    areas_touched: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class NextMove:
    hypothesis: str = ""
    target_area: str = ""
    tier_targeted: int = 0
    technique: str = "open"  # open | ladder | specificity_conversion | contradiction | safety
    reasoning: str = ""


@dataclass
class InterviewerTurn:
    utterance: str
    assessment: Assessment | None = None
    next_move: NextMove | None = None
    should_close: bool = False
    closing_reason: str | None = None
    raw: dict = field(default_factory=dict)


def _extract_json(text: str) -> dict | None:
    """Pull the first balanced ``{...}`` object out of a possibly-noisy string."""
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


def parse_turn(text: str) -> InterviewerTurn:
    data = _extract_json(text)
    if data is None:
        # Fail safe: treat the whole thing as the question, assess nothing.
        return InterviewerTurn(utterance=text.strip(), raw={})

    assess_raw = data.get("assessment_of_last_answer") or {}
    assessment = Assessment(
        got_substantive_disclosure=bool(assess_raw.get("got_substantive_disclosure", False)),
        tier_reached=int(assess_raw.get("tier_reached", 0) or 0),
        specificity=str(assess_raw.get("specificity", "none")),
        candor_signal=str(assess_raw.get("candor_signal", "neutral")),
        areas_touched=list(assess_raw.get("target_areas_touched", []) or []),
        note=str(assess_raw.get("note", "")),
    )
    move_raw = data.get("next_move") or {}
    next_move = NextMove(
        hypothesis=str(move_raw.get("hypothesis", "")),
        target_area=str(move_raw.get("target_area", "")),
        tier_targeted=int(move_raw.get("tier_targeted", 0) or 0),
        technique=str(move_raw.get("technique", "open")),
        reasoning=str(move_raw.get("reasoning", "")),
    )
    utterance = str(data.get("utterance", "")).strip()
    if not utterance:
        utterance = text.strip()
    return InterviewerTurn(
        utterance=utterance,
        assessment=assessment,
        next_move=next_move,
        should_close=bool(data.get("should_close", False)),
        closing_reason=data.get("closing_reason"),
        raw=data,
    )
