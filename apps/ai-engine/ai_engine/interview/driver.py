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

    @classmethod
    def resume(
        cls,
        *,
        engine: InterviewEngine,
        transcript: Transcript,
        objective: str,
        pending_question: str | None,
        turn_count: int,
        event_log: EventLog | None = None,
        max_turns: int = 14,
    ) -> "InterviewDriver":
        """Rebuild a driver mid-interview from a stored draft.

        Coverage state is reconstructed by replaying the transcript's answers through
        the same local assessment the engine uses, rather than being persisted
        separately — one source of truth for what an answer meant, so a resumed
        interview cannot diverge from one that never stopped.

        Attribution needs what each question *targeted* (``assess_locally`` credits
        ``state.pending_area``/``pending_tier``, which only ``note_question`` sets).
        Each ``InterviewerAsked`` event records exactly that, so the event log is the
        primary source; the offline question bank is the fallback for drafts whose
        log is missing. Without either, replayed answers would all attribute to no
        area at tier 0 — every area "untouched" — and the resumed interview would
        silently diverge from one that never stopped.
        """
        driver = cls(engine=engine, transcript=transcript, objective=objective,
                     event_log=event_log, max_turns=max_turns)
        driver._started = True  # do not re-emit InterviewStarted on every resume
        driver._pending_question = pending_question

        from .engine import assess_locally, question_area_index

        asked: dict[str, tuple[str, int]] = {}
        for event in (event_log.read() if event_log is not None else []):
            if (event.get("event") == "InterviewerAsked"
                    and event.get("segment_id") and event.get("target_area")):
                tier = event.get("tier_credited") or event.get("tier_targeted") or 1
                asked[event["segment_id"]] = (event["target_area"], int(tier))
        bank = question_area_index()

        pending_q: str | None = None
        replayed_turns = 0
        for segment in transcript.segments:
            if segment.speaker is Speaker.INTERVIEWER:
                pending_q = segment.text
                target = (asked.get(segment.id)
                          or bank.get(segment.text.strip()))
                if target is not None:
                    area, tier = target
                    if tier is None:
                        # A specificity probe: same topic, tier unchanged.
                        driver._state.pending_area = area
                    else:
                        driver._state.note_question(area, tier)
                driver._history.append({"role": "assistant", "content": segment.text})
                replayed_turns += 1
            else:
                driver._history.append({"role": "user", "content": segment.text})
                if pending_q is not None:
                    assessment = assess_locally(segment.text, driver._state)
                    driver._state.record_answer(
                        areas_touched=assessment.areas_touched,
                        tier_reached=assessment.tier_reached,
                        got_disclosure=assessment.got_substantive_disclosure,
                        specificity=assessment.specificity,
                        candor_signal=assessment.candor_signal,
                        answer=segment.text,
                    )
                driver._last_answer = segment.text
                pending_q = None
        # The stored count is authoritative (the caller checkpointed it); replaying
        # turn-by-turn first keeps deferred-until / last-asked arithmetic sane.
        driver._state.turn_count = turn_count if turn_count else replayed_turns
        driver._folded_current = True  # everything replayed is already folded
        return driver

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
            # What the asked question actually credited (the bank text asked may
            # sit at a different tier than the move targeted — see engine). Resume
            # replays from this, so it must match what live recorded.
            tier_credited=self._state.pending_tier,
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
