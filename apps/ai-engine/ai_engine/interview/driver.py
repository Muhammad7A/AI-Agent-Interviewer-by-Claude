"""One-turn-at-a-time interview control.

``run_interview`` drives a whole interview in a loop, which suits a CLI and a test.
A web app cannot: each turn is a separate HTTP request, so the loop has to be
inverted — the caller asks for a question, goes away, and comes back with an answer.

Both control flows share this one implementation of what a turn *is*, rather than
each keeping its own copy. Two copies of the turn loop would be a semantic
duplication (Art. XV) in the most consequential place in the system: the code that
decides what gets recorded as testimony.
"""
from __future__ import annotations

from ..llm.client import Message
from ..persistence.event_log import EventLog, NullEventLog
from ..transcript.model import Speaker, Transcript
from .engine import InterviewEngine
from .prompts import PROMPT_VERSION
from .state import InterviewState
from .turn import InterviewerTurn


class InterviewDriver:
    """Advance an interview a turn at a time.

    Usage::

        q = driver.next_question()      # None once the interview has closed
        driver.submit_answer(text)
        q = driver.next_question()
        ...
        driver.finish()
    """

    def __init__(
        self,
        *,
        engine: InterviewEngine,
        transcript: Transcript,
        objective: str,
        event_log: EventLog | None = None,
        max_turns: int = 14,
    ) -> None:
        self._engine = engine
        self._transcript = transcript
        self._log = event_log or NullEventLog()
        self._state = InterviewState(objective=objective)
        self._history: list[Message] = []
        self._max_turns = max_turns
        self._last_answer: str | None = None
        self._pending_question: str | None = None
        self._closed = False
        self._close_reason: str | None = None
        self._started = False
        # Whether the current pending answer has already been folded into the state.
        self._folded_current = True  # nothing to fold before the first answer

    # -- state ------------------------------------------------------------
    @property
    def transcript(self) -> Transcript:
        return self._transcript

    @property
    def state(self) -> InterviewState:
        return self._state

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def pending_question(self) -> str | None:
        """The question awaiting an answer, if any."""
        return self._pending_question

    @property
    def awaiting_answer(self) -> bool:
        return self._pending_question is not None and not self._closed

    def _start(self) -> None:
        if self._started:
            return
        self._started = True
        self._log.emit(
            "InterviewStarted",
            engagement_id=self._transcript.engagement_id,
            tenant_id=self._transcript.tenant_id,
            transcript_id=self._transcript.id,
            objective=self._state.objective,
            prompt_version=PROMPT_VERSION,
            mode="live" if self._engine.is_live else "mock",
        )

    # -- turns ------------------------------------------------------------
    def next_question(self) -> str | None:
        """Ask the next question, or return ``None`` if the interview has closed."""
        self._start()
        if self._closed:
            return None
        if self._pending_question is not None:
            return self._pending_question  # idempotent: don't burn a turn on a refresh
        if self._state.turn_count >= self._max_turns:
            self._close("budget")
            return None

        # The engine folds the previous answer into the state itself, before choosing
        # the next move — it has to, or the decision would always be one turn behind
        # the answer it is reacting to. Folding again here would double-count.
        # Folding happens before the model call, so if that call fails the fold has
        # already occurred. Mark it done *before* the call, so retrying after a
        # transient model failure does not count the same answer twice.
        fold = not self._folded_current
        self._folded_current = True
        turn: InterviewerTurn = self._engine.next_turn(
            state=self._state, history=self._history, last_answer=self._last_answer,
            fold_last=fold,
        )

        segment = self._transcript.append(Speaker.INTERVIEWER, turn.utterance)
        self._history.append({"role": "assistant", "content": turn.utterance})
        self._state.turn_count += 1
        self._log.emit(
            "InterviewerAsked",
            segment_id=segment.id,
            sequence=segment.sequence,
            turn=self._state.turn_count,
            target_area=(turn.next_move.target_area if turn.next_move else None),
            tier_targeted=(turn.next_move.tier_targeted if turn.next_move else None),
            technique=(turn.next_move.technique if turn.next_move else None),
        )

        if turn.should_close:
            # The closing remark is recorded, then the interview ends.
            self._pending_question = None
            self._closing_utterance = turn.utterance
            self._close(turn.closing_reason or "coverage_saturated")
            return None

        self._pending_question = turn.utterance
        return turn.utterance

    def submit_answer(self, answer: str) -> None:
        """Record the interviewee's answer to the pending question."""
        if self._closed:
            raise RuntimeError("the interview has closed; no further answers")
        if self._pending_question is None:
            raise RuntimeError("there is no pending question to answer")
        question_segment = self._transcript.segments[-1]
        segment = self._transcript.append(Speaker.SUBJECT, answer)
        self._history.append({"role": "user", "content": answer})
        self._log.emit(
            "SubjectResponded",
            segment_id=segment.id,
            sequence=segment.sequence,
            in_reply_to=question_segment.id,
            chars=len(answer),
        )
        self._last_answer = answer
        self._pending_question = None
        self._folded_current = False  # this new answer has not been folded yet

    def _close(self, reason: str) -> None:
        if self._closed:
            return
        self._closed = True
        self._close_reason = reason
        summary = self._state.summary()
        self._log.emit(
            "InterviewClosed",
            reason=reason,
            areas_covered=summary["areas_covered"],
            areas_total=summary["areas_total"],
            disclosures_tier2plus=summary["disclosures_tier2plus"],
        )

    def close(self, reason: str = "ended_by_operator") -> None:
        """End the interview early (the consultant or interviewee stopped)."""
        self._pending_question = None
        self._close(reason)

    def finish(self) -> Transcript:
        """Close if needed and finalize the transcript, making it immutable."""
        self._close(self._close_reason or "budget")
        if not self._transcript.finalized:
            self._transcript.finalize()
        return self._transcript
