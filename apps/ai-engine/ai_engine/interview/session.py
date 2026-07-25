"""The interview loop orchestrator.

Ties the engine, the interviewee, the immutable transcript, and the testimony
event log into one run. Storage-agnostic: it records segments and emits events
through injected collaborators (Constitution C10). The same function drives both
a live human interview and a fully simulated one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..persistence.event_log import EventLog
from ..transcript.model import Transcript
from .driver import InterviewDriver
from .engine import InterviewEngine
from .state import InterviewState

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
    emit = emit or _noop_emitter

    # The batch loop and the web app share one definition of a turn (see
    # ``InterviewDriver``); this function is the batch control flow over it.
    driver = InterviewDriver(
        engine=engine,
        transcript=transcript,
        objective=objective,
        event_log=event_log,
        max_turns=max_turns,
    )

    while True:
        question = driver.next_question()
        if question is None:
            break
        emit("interviewer", question)
        answer = subject.answer(question)
        driver.submit_answer(answer)
        emit("subject", answer)

    # The closing remark, if the engine produced one, is already recorded.
    closing = getattr(driver, "_closing_utterance", None)
    if closing:
        emit("interviewer", closing)

    driver.finish()
    return InterviewResult(
        transcript=driver.transcript, state=driver.state, turns=driver.state.turn_count
    )
