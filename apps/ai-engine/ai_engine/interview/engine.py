"""The interview engine: produce the next interviewer turn.

The engine no longer walks a fixed script. It assesses the last answer, folds that into
the interview state, asks :class:`InterviewStrategy` what to do next, and then phrases
it — offline from a question bank, live by handing the model the chosen move as a
directive. Both paths run the same decision, so the strategy is measurable by the eval
harness rather than hidden inside a prompt.

The offline question texts are deliberately unchanged from the original scripted
ladder: the synthetic personas key their disclosures off this exact wording, so
rephrasing them would quietly break the testbed rather than improve it. What changed is
*which* question is asked, *when*, and what happens when an answer is vague or guarded.
"""
from __future__ import annotations

from ..llm.client import LLMClient, Message
from .prompts import INTERVIEWER_SYSTEM, render_turn_prompt
from .state import InterviewState
from .strategy import Intent, InterviewStrategy, Move
from .turn import Assessment, InterviewerTurn, NextMove, parse_turn

# Question bank, keyed by (area, tier). Texts preserved from the original ladder.
_BANK: dict[tuple[str, int], str] = {
    ("process_reality", 1):
        "Where does the real version of that differ from how it's officially supposed "
        "to work?",
    ("workarounds", 2):
        "When the official tools or process get in your way, what do you do instead — "
        "any workarounds you've built for yourself?",
    ("bottlenecks", 2):
        "Where do things most often stall or pile up waiting on someone or something?",
    ("wasted_effort", 2):
        "When was the last time you spent real effort on something that felt redundant "
        "or got redone? Walk me through it.",
    ("friction", 3):
        "Was that more about the tools, the process, or a decision someone made? "
        "There's no wrong answer — I'm just mapping where the friction sits.",
    ("ai_opportunity", 2):
        "Which parts of your week are the most repetitive or rules-based — the stuff "
        "you could almost do in your sleep?",
    ("friction", 4):
        "A lot of people quietly work around all this. What's your own honest version — "
        "anything you do differently than you're 'supposed' to?",
}

_OPENING = (
    "Thanks for making the time — nothing you say gets back to your employer with your "
    "name on it. To start, can you walk me through how your work actually gets done "
    "day to day?"
)

_CLOSING = "This has been genuinely useful. Thank you for being candid — we're done."

# Move-specific phrasings. Kept clear of the bank's keywords so the offline testbed
# attributes each disclosure to the question that actually earned it.
# A specificity probe must NAME what it is probing. "Can you give me an example?" is a
# weak question — it asks the subject to do the work of deciding what is relevant. A
# probe that repeats the topic's own words gets a concrete instance instead.
_SPECIFICITY_BY_AREA: dict[str, str] = {
    "process_reality":
        "When did it last differ from how it's officially supposed to work — what "
        "actually happened that time?",
    "workarounds":
        "When did you last do something instead of the official way — what was the "
        "workaround, exactly?",
    "bottlenecks":
        "When did things last stall or pile up — what were you waiting on, and for "
        "how long?",
    "wasted_effort":
        "What was the last thing that felt redundant or got redone — what was it, and "
        "how long did it take?",
    "ai_opportunity":
        "Which repetitive, rules-based task did you do most recently — walk me through "
        "it step by step?",
    "friction":
        "What was the last decision someone made that got in your way — what happened "
        "after that?",
}

_SPECIFICITY_FALLBACK = (
    "Can you give me the most recent example of that — what happened, and roughly when?"
)
_DE_ESCALATE = (
    "That's completely fine, we can leave that there. Let's step back: what does an "
    "ordinary day look like for you?"
)

# Reverse of the bank: exact question text -> (area, tier actually asked).
# The bank text for (friction, 1..2) does not exist, so a LADDER at friction tier 1
# phrases the tier-3 text; crediting the *move's* tier then recorded a tier-3
# disclosure as tier 1 and friction needed repeated asks to count as covered. The
# tier that matters is the one the words came from.
_BANK_REVERSE: dict[str, tuple[str, int]] = {
    text: (area, tier) for (area, tier), text in _BANK.items()
}


def question_area_index(bank: dict | None = None, opening: str | None = None,
                        probes: dict | None = None) -> dict[str, tuple[str, int | None]]:
    """Which (area, tier) each known offline question text aims at.

    Used by ``InterviewDriver.resume`` to restore what each replayed question was
    targeting when no event log records it. Specificity probes stay on the topic's
    current tier (``None`` = keep whatever was pending), and the de-escalation
    text is deliberately absent — the safe area it drops to is chosen from state,
    so text alone cannot recover it and replay keeps the previous topic.

    Defaults to the module's own tables; a composed scenario injects its
    rendered bank/opening/probes (universe seam S1) so resume attribution and
    the lab's relevance grader read the SAME tables the engine phrases from.
    """
    bank = _BANK if bank is None else bank
    opening = _OPENING if opening is None else opening
    probes = _SPECIFICITY_BY_AREA if probes is None else probes
    index: dict[str, tuple[str, int | None]] = {opening: ("process_reality", 1)}
    index.update({text: (area, tier) for (area, tier), text in bank.items()})
    for area, text in probes.items():
        index[text] = (area, None)
    return index


def _phrase(move: Move, state: InterviewState, bank: dict | None = None,
            opening: str | None = None, probes: dict | None = None) -> str:
    bank = _BANK if bank is None else bank
    opening = _OPENING if opening is None else opening
    probes = _SPECIFICITY_BY_AREA if probes is None else probes
    if move.intent is Intent.OPEN:
        return opening
    if move.intent is Intent.CLOSE:
        return _CLOSING
    if move.intent is Intent.CONVERT_SPECIFICITY:
        return probes.get(move.target_area, _SPECIFICITY_FALLBACK)
    if move.intent is Intent.DE_ESCALATE:
        return _DE_ESCALATE
    if move.intent is Intent.SURFACE_CONTRADICTION:
        earlier = move.earlier[:90]
        return (f"Earlier you mentioned \"{earlier}\" — how does that sit alongside what "
                f"you just said? I'm not catching you out, I just want to get it right.")
    # LADDER: the bank entry for this area at this tier, or the nearest lower tier.
    for tier in range(move.target_tier, 0, -1):
        text = bank.get((move.target_area, tier))
        if text:
            return text
    for (area, _tier), text in bank.items():
        if area == move.target_area:
            return text
    return _CLOSING


# Two different failures, which must not be conflated.
#
# A DEFLECTION is a refusal: the subject is declining to go there. The right response
# is to back off and return later.
#
# A VAGUE answer is not a refusal — the subject answered, but said nothing usable. The
# right response is the opposite: stay on the topic and ask for a concrete instance.
#
# Treating vagueness as guardedness makes the interviewer retreat precisely when it
# should probe, and (as this engine did until it was caught) can livelock: soothe, get
# another vague answer, soothe again, forever.
_DEFLECTION_MARKERS = (
    "rather not", "prefer not", "no comment", "don't want to get into",
    "not comfortable", "won't answer", "skip that", "pass on that",
)

_VAGUE_MARKERS = (
    "mostly fine", "nothing jumps out", "pretty standard", "standard stuff",
    "nothing really", "can't think of", "not sure", "hard to say",
    "can't really say",
)


def _is_deflection(answer: str) -> bool:
    low = answer.lower()
    return any(m in low for m in _DEFLECTION_MARKERS)


def _is_vague(answer: str) -> bool:
    low = answer.lower()
    return any(m in low for m in _VAGUE_MARKERS) or len(answer.split()) < 6


def assess_locally(answer: str, state: InterviewState) -> Assessment:
    """A fast, model-free read of an answer.

    Offline this is the assessment of record. Live it is used only to keep the
    strategy's directive current: the model's own assessment of an answer arrives with
    the *following* response, so without a local read the strategy would always be
    reacting one turn late — and reacting late to "I'd rather not say" is the same as
    not reacting.
    """
    deflected = _is_deflection(answer)
    vague = deflected or _is_vague(answer)
    substantive = not vague
    area = state.pending_area or ""
    return Assessment(
        got_substantive_disclosure=substantive,
        tier_reached=state.pending_tier if substantive else 0,
        specificity="concrete" if substantive else "vague",
        # Only an actual refusal counts as guarded.
        candor_signal="guarded" if deflected else "neutral",
        areas_touched=[area] if area else [],
        note="local-assessment",
    )


class InterviewEngine:
    def __init__(
        self,
        *,
        llm: LLMClient | None = None,
        max_turns: int = 14,
        temperature: float = 0.4,
        strategy: InterviewStrategy | None = None,
        bank: dict | None = None,
        opening: str | None = None,
        probes: dict | None = None,
    ) -> None:
        self._llm = llm
        self._max_turns = max_turns
        self._temperature = temperature
        self._strategy = strategy or InterviewStrategy(max_turns=max_turns)
        # Universe seam S1: a composed scenario injects its own question bank,
        # opening, and specificity probes; None keeps the module defaults, so
        # every existing caller and all 17 golden scenarios are unchanged.
        self._bank = dict(bank) if bank else _BANK
        self._opening = opening or _OPENING
        self._probes = dict(probes) if probes else _SPECIFICITY_BY_AREA

    def question_index(self) -> dict[str, tuple[str, int | None]]:
        """The (text → area, tier) index for THIS engine's tables — what
        ``InterviewDriver.resume`` replays against."""
        return question_area_index(self._bank, self._opening, self._probes)

    @property
    def is_live(self) -> bool:
        return self._llm is not None

    @property
    def strategy(self) -> InterviewStrategy:
        return self._strategy

    def next_turn(
        self,
        *,
        state: InterviewState,
        history: list[Message],
        last_answer: str | None,
        fold_last: bool = True,
    ) -> InterviewerTurn:
        """Produce the next turn.

        ``fold_last=False`` when the caller is *retrying* after a failed model call:
        the previous answer was already folded into the state on the attempt that
        failed, and folding it twice would double-count the disclosure and corrupt
        coverage. Folding happens before the model call, so a caller that saw an
        exception must assume it happened.
        """
        assessment: Assessment | None = None
        if fold_last and last_answer is not None and state.pending_area is not None:
            assessment = assess_locally(last_answer, state)
            state.record_answer(
                areas_touched=assessment.areas_touched,
                tier_reached=assessment.tier_reached,
                got_disclosure=assessment.got_substantive_disclosure,
                specificity=assessment.specificity,
                candor_signal=assessment.candor_signal,
                answer=last_answer,
            )

        move = self._strategy.decide(state)

        noted = (move.target_area, move.target_tier)
        if self._llm is not None:
            turn = self._live_turn(state=state, history=history,
                                   last_answer=last_answer, move=move)
        else:
            utterance = _phrase(move, state, self._bank, self._opening,
                                self._probes)
            if move.intent is Intent.LADDER:
                # Credit the tier the phrased words actually came from, not the
                # move's target — see _BANK_REVERSE.
                noted = _BANK_REVERSE.get(utterance, noted)
            turn = InterviewerTurn(
                utterance=utterance,
                assessment=assessment,
                next_move=NextMove(
                    hypothesis=move.rationale,
                    target_area=move.target_area,
                    tier_targeted=move.target_tier,
                    technique=move.technique,
                    reasoning=move.rationale,
                ),
                should_close=move.intent is Intent.CLOSE,
                closing_reason=("coverage_saturated" if move.intent is Intent.CLOSE
                                else None),
            )

        if not turn.should_close:
            state.note_question(*noted)        # The assessment has already been folded; do not hand it back for re-folding.
        turn.assessment = None
        return turn

    def _live_turn(
        self,
        *,
        state: InterviewState,
        history: list[Message],
        last_answer: str | None,
        move: Move,
    ) -> InterviewerTurn:
        messages = list(history)
        messages.append({
            "role": "user",
            "content": (
                render_turn_prompt(
                    state_summary=state.summary(),
                    last_answer=last_answer,
                    turn_index=state.turn_count + 1,
                )
                + "\n\n" + _directive(move)
            ),
        })
        text = self._llm.complete(
            system=INTERVIEWER_SYSTEM,
            messages=messages,
            max_tokens=800,
            temperature=self._temperature,
        )
        turn = parse_turn(text)
        if move.intent is Intent.CLOSE:
            turn.should_close = True
        return turn


def _directive(move: Move) -> str:
    """The strategy's decision, handed to the model as an instruction for this turn."""
    lines = [
        "STRATEGIC DIRECTIVE for this turn (chosen from the interview state — follow it):",
        f"- move: {move.intent.value}",
        f"- target area: {move.target_area}",
        f"- target tier: {move.target_tier}",
        f"- why: {move.rationale}",
    ]
    if move.intent is Intent.CONVERT_SPECIFICITY:
        lines.append("- The last answer was vague. Do NOT move on. Ask for the most "
                     "recent concrete instance: what happened, and when.")
    elif move.intent is Intent.DE_ESCALATE:
        lines.append("- The subject was guarded. Do NOT push. Reassure briefly, drop to "
                     "a lower-cost topic, and leave the sensitive one for later.")
    elif move.intent is Intent.SURFACE_CONTRADICTION:
        lines.append(f"- This appears to conflict with something they said earlier: "
                     f"\"{move.earlier[:160]}\". Raise it gently and without accusation; "
                     f"assume it is a clarification, not a lie.")
    elif move.intent is Intent.CLOSE:
        lines.append("- Close the interview warmly. Set should_close to true.")
    return "\n".join(lines)
