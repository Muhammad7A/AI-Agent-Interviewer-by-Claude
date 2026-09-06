"""The employee interview surface — a separate app, on purpose.

This is a **different ASGI application** from the consultant workspace, not extra
routes on it. That is the point: the employee surface has no code path to a transcript
list, a review queue, a report, or anyone else's interview, because those routes do not
exist in this app at all. A boundary enforced by absence cannot be defeated by a
misconfigured guard.

What this app can do:  ask the next question, record an answer, store on submit,
discard on withdrawal.
What it cannot do:     read any interview (including the participant's own, once
submitted), reach the workspace, or learn anyone's name.

Why it exists: until now the interview ran inside the consultant workspace, which
means the consultant was present. That destroys the candour the whole product depends
on measuring (F1) — the experiment design requires the employee alone with the tool.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..config import Settings, get_llm_client, load_settings
from ..interview.driver import InterviewDriver
from ..interview.engine import InterviewEngine
from ..interview.session import DEFAULT_OBJECTIVE
from ..persistence.event_log import EventLog
from ..persistence.invitations import InvitationStatus, InvitationStore
from ..llm.retry import LLMError
from ..persistence.session_store import SavedSession, SessionStore
from ..persistence.transcript_store import TranscriptStore
from ..transcript.model import Speaker, Transcript
from . import views

OBJECTIVE_NOTE = (
    "We are mapping how work really happens here — where it stalls, what people work "
    "around, and which parts are repetitive enough to automate."
)


@dataclass
class LiveSession:
    driver: InterviewDriver
    question: str | None = None
    #: Set when a model call failed. The interview is recoverable, not over.
    stalled: bool = False


@dataclass
class Sessions:
    """In-flight interviews, keyed by invitation token.

    Held in memory deliberately: an interview that was never submitted has not been
    consented to, so it must not be written to disk. Losing it on restart is the
    correct failure mode — the alternative is retaining testimony the participant
    never agreed to hand over.
    """

    settings: Settings
    live: dict[str, LiveSession] = field(default_factory=dict)


def create_employee_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    settings.assert_deployable()

    sessions = Sessions(settings=settings)
    app = FastAPI(title="Groundwork interview", docs_url=None, redoc_url=None)
    app.state.sessions = sessions

    def store() -> InvitationStore:
        return InvitationStore(settings.data_dir)

    def sessions_store() -> SessionStore:
        return SessionStore(settings.data_dir, settings.cipher())

    def _persist(token: str, session: LiveSession) -> None:
        """Checkpoint the draft so a dropped connection does not lose the interview."""
        sessions_store().save(SavedSession(
            token=token,
            transcript=session.driver.transcript,
            pending_question=session.question,
            turn_count=session.driver.state.turn_count,
            closed=session.driver.closed,
            updated_at=None,  # set on write
        ))

    def _revive(token: str, invitation) -> LiveSession | None:
        """Rebuild an in-flight interview from its stored draft, after a restart."""
        saved = sessions_store().load(token)
        if saved is None or saved.is_expired():
            if saved is not None:
                sessions_store().delete(token)
            return None
        driver = InterviewDriver.resume(
            engine=InterviewEngine(llm=get_llm_client(settings),
                                   max_turns=settings.max_turns),
            transcript=saved.transcript,
            objective=DEFAULT_OBJECTIVE,
            pending_question=saved.pending_question,
            turn_count=saved.turn_count,
            event_log=EventLog(settings.data_dir, saved.transcript.id,
                               layer="testimony", cipher=settings.cipher()),
            max_turns=settings.max_turns,
        )
        session = LiveSession(driver=driver, question=saved.pending_question)
        sessions.live[token] = session
        return session

    def _unavailable() -> HTMLResponse:
        # One response for unknown, used, and withdrawn tokens alike: distinguishing
        # them would let a probe learn which tokens exist.
        return HTMLResponse(views.unavailable(), status_code=404)

    def _answered_pairs(transcript: Transcript) -> list[dict]:
        """The participant's own question/answer pairs, for their own review."""
        pairs: list[dict] = []
        pending: str | None = None
        for segment in transcript.segments:
            if segment.speaker is Speaker.INTERVIEWER:
                pending = segment.text
            elif pending is not None:
                pairs.append({"question": pending, "answer": segment.text})
                pending = None
        return pairs

    @app.get("/i/{token}", response_class=HTMLResponse)
    def surface(request: Request, token: str) -> HTMLResponse:
        invitation = store().get(token)
        if invitation is None or invitation.is_finished:
            return _unavailable()

        session = sessions.live.get(token) or _revive(token, invitation)
        if session is None:
            return HTMLResponse(views.welcome(token=token, objective_note=OBJECTIVE_NOTE))

        answered = _answered_pairs(session.driver.transcript)
        if session.stalled and not session.driver.closed:
            try:
                session.question = session.driver.next_question()
                session.stalled = False
            except LLMError:
                return HTMLResponse(views.temporarily_unavailable(token), status_code=503)
        if session.driver.closed or session.question is None:
            return HTMLResponse(views.review_before_finish(token=token, answered=answered))
        return HTMLResponse(views.question_page(
            token=token, question=session.question, answered=answered,
            turn=session.driver.state.turn_count,
            max_turns=settings.max_turns))

    @app.post("/i/{token}/begin")
    def begin(request: Request, token: str):
        invitation = store().get(token)
        if invitation is None or invitation.is_finished:
            return _unavailable()
        if token not in sessions.live:
            transcript = Transcript(engagement_id=invitation.engagement_id,
                                    tenant_id=invitation.tenant_id)
            # The pseudonym was assigned when the invitation was created; this app
            # never sees or asks for a real name.
            transcript.interview_id = invitation.pseudonym
            driver = InterviewDriver(
                engine=InterviewEngine(llm=get_llm_client(settings),
                                       max_turns=settings.max_turns),
                transcript=transcript,
                objective=DEFAULT_OBJECTIVE,
                event_log=EventLog(settings.data_dir, transcript.id, layer="testimony",
                                cipher=settings.cipher()),
                max_turns=settings.max_turns,
            )
            session = LiveSession(driver=driver)
            try:
                session.question = driver.next_question()
            except LLMError:
                store().set_status(token, InvitationStatus.PENDING)
                return HTMLResponse(views.temporarily_unavailable(token), status_code=503)
            sessions.live[token] = session
            _persist(token, session)
            store().set_status(token, InvitationStatus.IN_PROGRESS,
                               transcript_id=transcript.id)
        return RedirectResponse(f"/i/{token}", status_code=303)

    @app.post("/i/{token}/answer")
    def answer(request: Request, token: str, answer: str = Form(...)):
        invitation = store().get(token)
        session = sessions.live.get(token)
        if session is None and invitation is not None and not invitation.is_finished:
            session = _revive(token, invitation)
        if invitation is None or invitation.is_finished or session is None:
            return _unavailable()
        if len(answer) > settings.max_answer_chars:
            # An oversized paste would be recorded verbatim and then fail every
            # future model call permanently — wedging the interview with no way
            # to retract it. Refuse it before it touches the transcript.
            return HTMLResponse(
                views.answer_too_long(token, settings.max_answer_chars),
                status_code=413)
        if not session.driver.closed and session.question is not None:
            session.driver.submit_answer(answer)
            try:
                session.question = session.driver.next_question()
            except LLMError:
                # The answer is already recorded; only the NEXT question failed.
                # Leave the session intact so a refresh retries, rather than
                # discarding fifteen minutes of someone's time.
                session.question = None
                session.stalled = True
        _persist(token, session)
        return RedirectResponse(f"/i/{token}", status_code=303)

    @app.post("/i/{token}/finish")
    def finish(request: Request, token: str):
        invitation = store().get(token)
        session = sessions.live.pop(token, None)
        if session is None and invitation is not None and not invitation.is_finished:
            session = _revive(token, invitation)
            sessions.live.pop(token, None)
        if invitation is None or invitation.is_finished or session is None:
            return _unavailable()
        transcript = session.driver.finish()
        # The transcript is finalized here for the first time; if it somehow
        # already exists, write-once immutability wins and the completed page
        # below is still the right response.
        try:
            TranscriptStore(settings.data_dir, settings.cipher()).save(transcript)
        except FileExistsError:
            pass
        # The draft has become a consented record; the working copy goes.
        sessions_store().delete(token)
        store().set_status(token, InvitationStatus.COMPLETED,
                           transcript_id=transcript.id)
        return HTMLResponse(views.finished())

    @app.post("/i/{token}/withdraw")
    def withdraw(request: Request, token: str):
        invitation = store().get(token)
        if invitation is None:
            return _unavailable()
        if invitation.is_finished:
            # A completed interview cannot be withdrawn post hoc: the testimony
            # was consented to and stored. Telling someone "nothing was stored"
            # here would be a lie — the honest answer is that withdrawal no
            # longer applies and erasure goes through the consultant.
            return HTMLResponse(views.already_submitted(), status_code=409)
        # Drop the in-flight interview without ever storing it. The right to withdraw
        # is only real if withdrawing leaves nothing behind.
        sessions.live.pop(token, None)
        # Deleting the draft is what makes the right to withdraw real.
        sessions_store().delete(token)
        store().set_status(token, InvitationStatus.WITHDRAWN)
        return HTMLResponse(views.withdrawn())

    return app
