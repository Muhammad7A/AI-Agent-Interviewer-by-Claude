"""The interview loop orchestrator.

Ties the engine, the interviewee, the immutable transcript, and the testimony
event log into one run. Storage-agnostic: it records segments and emits events
through injected collaborators (Constitution C10). The same function drives both
a live human interview and a fully simulated one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..llm.client import Message
from ..persistence.event_log import EventLog, NullEventLog
from ..transcript.model import Speaker, Transcript
from .engine import InterviewEngine
from .prompts import PROMPT_VERSION
from .state import InterviewState
from .turn import InterviewerTurn

# Called with (speaker, text) so a CLI can print the exchange as it happens.
Emitter = Callable[[str, str], None]

DEFAULT_OBJECTIVE = (
    "Map how work actually gets done, where it stalls, what people work around, and "
    "where repetitive effort could be automated."
)


@dataclass
class InterviewResult:
    transcript: Transcript
    state: InterviewState
    turns: int


def _noop_emitter(speaker: str, text: str) -> None:
    return None


def run_interview(
    *,
    engine: InterviewEngine,
    subject,
    objective: str = DEFAULT_OBJECTIVE,
    transcript: Transcript | None = None,
    event_log: EventLog | None = None,
    max_turns: int = 14,
    emit: Emitter | None = None,
) -> InterviewResult:
    transcript = transcript or Transcript()
    log = event_log or NullEventLog()
    emit = emit or _noop_emitter
    state = InterviewState(objective=objective)
    history: list[Message] = []

    log.emit(
        "InterviewStarted",
        engagement_id=transcript.engagement_id,
        tenant_id=transcript.tenant_id,
        transcript_id=transcript.id,
        objective=objective,
        prompt_version=PROMPT_VERSION,
        mode="live" if engine.is_live else "mock",
    )

    last_answer: str | None = None

    for _ in range(max_turns):
        turn: InterviewerTurn = engine.next_turn(
            state=state, history=history, last_answer=last_answer
        )

        # Fold the engine's assessment of the PREVIOUS answer into coverage.
        if turn.assessment is not None:
            state.record_answer(
                areas_touched=turn.assessment.areas_touched,
                tier_reached=turn.assessment.tier_reached,
                got_disclosure=turn.assessment.got_substantive_disclosure,
            )

        # Record + emit the interviewer's question.
        q_seg = transcript.append(Speaker.INTERVIEWER, turn.utterance)
        history.append({"role": "assistant", "content": turn.utterance})
        state.turn_count += 1
        emit("interviewer", turn.utterance)
        log.emit(
            "InterviewerAsked",
            segment_id=q_seg.id,
            sequence=q_seg.sequence,
            turn=state.turn_count,
            target_area=(turn.next_move.target_area if turn.next_move else None),
            tier_targeted=(turn.next_move.tier_targeted if turn.next_move else None),
            technique=(turn.next_move.technique if turn.next_move else None),
        )

        if turn.should_close:
            log.emit("InterviewClosed", reason=turn.closing_reason, **_coverage_payload(state))
            break

        # Get the subject's answer, record + emit it.
        answer = subject.answer(turn.utterance)
        a_seg = transcript.append(Speaker.SUBJECT, answer)
        history.append({"role": "user", "content": answer})
        emit("subject", answer)
        log.emit(
            "SubjectResponded",
            segment_id=a_seg.id,
            sequence=a_seg.sequence,
            in_reply_to=q_seg.id,
            chars=len(answer),
        )
        last_answer = answer
    else:
        # Loop exhausted without an explicit close.
        log.emit("InterviewClosed", reason="budget", **_coverage_payload(state))

    transcript.finalize()
    return InterviewResult(transcript=transcript, state=state, turns=state.turn_count)


def _coverage_payload(state: InterviewState) -> dict:
    s = state.summary()
    return {
        "areas_covered": s["areas_covered"],
        "areas_total": s["areas_total"],
        "disclosures_tier2plus": s["disclosures_tier2plus"],
    }
