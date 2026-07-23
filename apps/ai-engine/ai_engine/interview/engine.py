"""The interview engine: produce the next interviewer turn.

If a live LLM client is supplied, the engine is genuinely hypothesis-driven — the
model assesses the last answer and selects the next question. With no client it
falls back to a deterministic tier-laddering script so the whole loop runs
offline (tests, CI, the synthetic-org testbed). The scripted fallback is a real
interview strategy, just a fixed one — which is also the baseline the research
program wants to beat (learned vs scripted, Q5).
"""
from __future__ import annotations

from ..llm.client import LLMClient, Message
from .prompts import INTERVIEWER_SYSTEM, render_turn_prompt
from .state import COVERAGE_TIER, TARGET_AREAS, InterviewState
from .turn import Assessment, InterviewerTurn, NextMove, parse_turn

# Deterministic laddering script for mock mode: (area, tier, question).
_MOCK_LADDER: list[tuple[str, int, str]] = [
    ("process_reality", 1,
     "Thanks for making the time — nothing you say gets back to your employer with "
     "your name on it. To start, can you walk me through how your work actually gets "
     "done day to day?"),
    ("process_reality", 1,
     "Where does the real version of that differ from how it's officially supposed to work?"),
    ("workarounds", 2,
     "When the official tools or process get in your way, what do you do instead — "
     "any workarounds you've built for yourself?"),
    ("bottlenecks", 2,
     "Where do things most often stall or pile up waiting on someone or something?"),
    ("wasted_effort", 2,
     "When was the last time you spent real effort on something that felt redundant "
     "or got redone? Walk me through it."),
    ("friction", 3,
     "Was that more about the tools, the process, or a decision someone made? "
     "There's no wrong answer — I'm just mapping where the friction sits."),
    ("ai_opportunity", 2,
     "Which parts of your week are the most repetitive or rules-based — the stuff "
     "you could almost do in your sleep?"),
    ("friction", 4,
     "A lot of people quietly work around all this. What's your own honest version — "
     "anything you do differently than you're 'supposed' to?"),
]


class InterviewEngine:
    def __init__(
        self,
        *,
        llm: LLMClient | None = None,
        max_turns: int = 14,
        temperature: float = 0.4,
    ) -> None:
        self._llm = llm
        self._max_turns = max_turns
        self._temperature = temperature

    @property
    def is_live(self) -> bool:
        return self._llm is not None

    def next_turn(
        self,
        *,
        state: InterviewState,
        history: list[Message],
        last_answer: str | None,
    ) -> InterviewerTurn:
        if self._llm is not None:
            return self._live_turn(state=state, history=history, last_answer=last_answer)
        return self._mock_turn(state=state, last_answer=last_answer)

    # -- live path ---------------------------------------------------------
    def _live_turn(
        self,
        *,
        state: InterviewState,
        history: list[Message],
        last_answer: str | None,
    ) -> InterviewerTurn:
        messages = list(history)
        messages.append(
            {
                "role": "user",
                "content": render_turn_prompt(
                    state_summary=state.summary(),
                    last_answer=last_answer,
                    turn_index=state.turn_count + 1,
                ),
            }
        )
        text = self._llm.complete(
            system=INTERVIEWER_SYSTEM,
            messages=messages,
            max_tokens=800,
            temperature=self._temperature,
        )
        return parse_turn(text)

    # -- mock path ---------------------------------------------------------
    def _mock_turn(self, *, state: InterviewState, last_answer: str | None) -> InterviewerTurn:
        # Assess the previous answer crudely: a non-deflecting answer of some
        # length counts as a disclosure at the tier we were targeting.
        assessment: Assessment | None = None
        step = state.turn_count  # number of interviewer questions already asked
        if last_answer is not None and step >= 1:
            prev_area, prev_tier, _ = _MOCK_LADDER[min(step - 1, len(_MOCK_LADDER) - 1)]
            low_signal = _looks_low_signal(last_answer)
            substantive = (not low_signal) and len(last_answer.split()) >= 6
            # Credit the targeted tier only on a genuine disclosure. A vague or
            # deflecting answer reached nothing, however long it is.
            assessment = Assessment(
                got_substantive_disclosure=substantive,
                tier_reached=prev_tier if substantive else 0,
                specificity="concrete" if substantive else "vague",
                candor_signal="guarded" if low_signal else "neutral",
                areas_touched=[prev_area],
                note="mock-assessment",
            )

        # Choose the next scripted question, or close.
        if step >= len(_MOCK_LADDER) or step >= self._max_turns or state.saturated():
            return InterviewerTurn(
                utterance=(
                    "That's really helpful — thank you. Last thing: is there anything "
                    "important about how work really gets done here that I didn't ask about?"
                    if step < len(_MOCK_LADDER) else
                    "This has been genuinely useful. Thank you for being candid — we're done."
                ),
                assessment=assessment,
                next_move=None,
                should_close=step >= len(_MOCK_LADDER),
                closing_reason="coverage_saturated" if state.saturated() else "budget",
            )

        area, tier, question = _MOCK_LADDER[step]
        return InterviewerTurn(
            utterance=question,
            assessment=assessment,
            next_move=NextMove(
                hypothesis=f"probe {area}",
                target_area=area,
                tier_targeted=tier,
                technique="ladder",
                reasoning="scripted laddering (mock)",
            ),
            should_close=False,
        )


# Markers of a deflection or a content-free non-answer. Either way, no
# organizational truth was actually disclosed.
_LOW_SIGNAL_MARKERS = (
    # deflections
    "rather not", "prefer not", "not sure", "can't really say", "no comment",
    "don't want to get into", "not comfortable", "hard to say",
    # vague non-answers
    "mostly fine", "nothing jumps out", "pretty standard", "standard stuff",
    "nothing really", "can't think of",
)


def _looks_low_signal(answer: str) -> bool:
    low = answer.lower()
    return any(m in low for m in _LOW_SIGNAL_MARKERS)
