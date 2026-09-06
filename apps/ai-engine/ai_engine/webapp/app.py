"""The consultant workspace: a presentation over the application layer.

Deliberate boundaries:

  * **Consultant-only.** There is no employer surface. The employer's document is
    produced by ``privacy.release`` and read here; it is never a page they log into.
  * **No domain logic.** Every route delegates to
    :class:`ai_engine.application.service.ConsultantService` — the use-cases live
    there once, headless and tested; this module parses forms and renders HTML.
  * **No authentication, unless an operator password is set.** This is a localhost
    single-consultant tool for the Year-0/1 experiments; with
    ``GROUNDWORK_OPERATOR_PASSWORD`` set, every route demands HTTP Basic (browsers
    prompt natively, no third-party dependency), and a production deployment
    refuses to start without one.
"""
from __future__ import annotations

import base64
import hmac

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..application.service import (
    ANSWER_TOO_LONG,
    ConsultantService,
)
from ..config import ConfigurationError, Settings, load_settings
from ..llm.retry import LLMError
from ..privacy import ReleasePolicy
from . import views


def _operator_authorized(request: Request, password: str | None) -> bool:
    if not password:
        return True
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth[6:].strip()).decode("utf-8")
    except Exception:
        return False
    supplied = decoded.partition(":")[2]
    return hmac.compare_digest(supplied.encode("utf-8"), password.encode("utf-8"))


def create_app(settings: Settings | None = None,
               service: ConsultantService | None = None) -> FastAPI:
    settings = settings or load_settings()
    # Refuse to serve real interviews from an unsafe configuration.
    settings.assert_deployable()
    if settings.is_production and not settings.operator_password:
        raise ConfigurationError(
            "GROUNDWORK_OPERATOR_PASSWORD must be set in production: the "
            "consultant workspace holds employee testimony, and its only "
            "development protection is that it binds to localhost.")
    svc = service or ConsultantService(settings)
    employer_k = ReleasePolicy.for_employer().k_anonymity

    app = FastAPI(title="Groundwork consultant workspace", docs_url=None,
                  redoc_url=None)
    app.state.service = svc

    @app.middleware("http")
    async def _require_operator(request: Request, call_next):
        if not _operator_authorized(request, settings.operator_password):
            posture, warn = svc.posture()
            return HTMLResponse(
                views.message(
                    title="Operator sign-in required",
                    text="This workspace holds employee testimony. Sign in with "
                         "the operator password to continue.",
                    posture=posture, warn=warn),
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="groundwork", charset="UTF-8"'})
        return await call_next(request)

    # -- dashboard ---------------------------------------------------------
    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> HTMLResponse:
        posture, warn = svc.posture()
        return HTMLResponse(views.dashboard(
            interviews=svc.dashboard_rows(), live=svc.live_summary(),
            engagements=svc.list_engagements(),
            posture=posture, warn=warn))

    # -- invitations -------------------------------------------------------
    @app.post("/invitations/new")
    def invite(request: Request, participant: str = Form(...),
               base_url: str = Form("http://127.0.0.1:8100")) -> RedirectResponse:
        """Create an invitation for the employee surface.

        The pseudonym is assigned here, on the consultant's side, so the interview
        surface never asks the participant for a name — there is no field for it.
        """
        svc.invite(participant)
        return RedirectResponse("/invitations", status_code=303)

    @app.post("/invitations/batch")
    def invite_batch(request: Request, names: str = Form(...)) -> RedirectResponse:
        svc.invite_batch(names)
        return RedirectResponse("/invitations", status_code=303)

    @app.get("/invitations", response_class=HTMLResponse)
    def invitations(request: Request) -> HTMLResponse:
        posture, warn = svc.posture()
        items = [
            {"token": i.token, "pseudonym": i.pseudonym, "status": i.status,
             "transcript_id": i.transcript_id or ""}
            for i in svc.list_invitations()
        ]
        return HTMLResponse(views.invitations(
            items=items, posture=posture, warn=warn))

    # -- interview ---------------------------------------------------------
    @app.post("/interviews/new")
    def start_interview(request: Request, participant: str = Form(...),
                        mode: str = Form("manual"),
                        engagement: str = Form("")):
        engagement_id = svc.resolve_engagement(engagement)
        try:
            transcript_id = svc.start(participant, simulated=(mode == "simulated"),
                                      engagement_id=engagement_id)
        except LLMError:
            # Nothing is registered, so the consultant can simply retry; the
            # transcript had no answers yet.
            posture, warn = svc.posture()
            return HTMLResponse(views.message(
                title="Model temporarily unavailable",
                text="The interview could not be started — no answers were "
                     "recorded. Try again.",
                posture=posture, warn=warn), status_code=503)
        return RedirectResponse(f"/interviews/{transcript_id}", status_code=303)

    @app.get("/interviews/{interview_id}", response_class=HTMLResponse)
    def interview(request: Request, interview_id: str) -> HTMLResponse:
        posture, warn = svc.posture()
        view = svc.view(interview_id)
        if view is None:
            return HTMLResponse(views.message(
                title="Interview not found",
                text="It may already be finalised — check the stored interviews.",
                posture=posture, warn=warn), status_code=404)
        if view["stalled"]:
            return HTMLResponse(views.message(
                title="Model temporarily unavailable",
                text="The interview is intact — refresh to retry. Nothing "
                     "needs to be re-entered.",
                posture=posture, warn=warn), status_code=503)
        return HTMLResponse(views.runner(
            interview_id=interview_id, participant=view["participant"],
            question=view["question"], turns=view["turns"],
            max_turns=settings.max_turns,
            transcript_html=views.transcript_turns(view["segments"]),
            closed=view["closed"],
            coverage=view["coverage"], posture=posture, warn=warn))

    @app.post("/interviews/{interview_id}/answer")
    def answer(request: Request, interview_id: str,
               answer: str = Form(...)):
        outcome = svc.submit_answer(interview_id, answer)
        if outcome == ANSWER_TOO_LONG:
            posture, warn = svc.posture()
            return HTMLResponse(views.message(
                title="Answer too long",
                text=f"Answers are capped at {settings.max_answer_chars} "
                     "characters. Split it into parts and answer again — "
                     "nothing was recorded.",
                posture=posture, warn=warn), status_code=413)
        return RedirectResponse(f"/interviews/{interview_id}", status_code=303)

    @app.post("/interviews/{interview_id}/finish")
    def finish(request: Request, interview_id: str) -> RedirectResponse:
        transcript_id = svc.finish(interview_id)
        if transcript_id is None:
            return RedirectResponse("/", status_code=303)
        return RedirectResponse(f"/transcripts/{transcript_id}/review",
                                status_code=303)

    # -- transcript & review ----------------------------------------------
    @app.get("/transcripts/{transcript_id}", response_class=HTMLResponse)
    def transcript_view(request: Request, transcript_id: str) -> HTMLResponse:
        posture, warn = svc.posture()
        transcript = svc.load_transcript(transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found",
                                              text="No stored transcript with that id.",
                                              posture=posture, warn=warn), status_code=404)
        segments = [{"id": s.id, "speaker": s.speaker.value, "text": s.text}
                    for s in transcript.segments]
        body = views.transcript_page(
            title=f"Transcript {transcript_id}",
            subtitle=f"{len(segments)} segments · immutable · every finding links here",
            segments=segments,
            back=f"/transcripts/{transcript_id}/review",
            posture=posture, warn=warn,
            note="The stored record. Every quote in every report deep-links to the "
                 "highlighted segment — provenance you can click.")
        return HTMLResponse(body)

    @app.get("/transcripts/{transcript_id}/review", response_class=HTMLResponse)
    def review(request: Request, transcript_id: str) -> HTMLResponse:
        posture, warn = svc.posture()
        transcript = svc.load_transcript(transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found",
                                              text="No stored transcript with that id.",
                                              posture=posture, warn=warn), status_code=404)
        tagging = svc.tag(transcript_id)
        verdicts = svc.verdicts(transcript_id)
        items = []
        for claim in (tagging.claims if tagging else []):
            ev = claim.evidence[0]
            recorded = verdicts.get(claim.id)
            items.append({
                "claim_id": claim.id,
                "claim_type": claim.claim_type.value,
                "tier": claim.tier,
                "statement": claim.statement,
                "quote": ev.resolve(transcript),
                "segment_id": ev.ref.segment_id,
                "start": ev.ref.start,
                "end": ev.ref.end,
                "match_kind": ev.match_kind,
                "verdict": recorded.verdict if recorded else None,
                "new_statement": recorded.new_statement if recorded else None,
            })
        return HTMLResponse(views.review(
            interview_id=transcript_id, participant=transcript.interview_id or "—",
            items=items, confabulation=tagging.confabulation_rate,
            unsourced=tagging.report.ungrounded,
            unsupported=len(tagging.entailment_rejected),
            posture=posture, warn=warn))

    @app.post("/transcripts/{transcript_id}/validate")
    def validate(request: Request, transcript_id: str, claim_id: str = Form(...),
                 verdict: str = Form(...), reason: str = Form(""),
                 statement: str = Form("")) -> RedirectResponse:
        # The gate enforces the invariants (a reason to amend or reject, the
        # reviewed evidence recorded); an invalid decision simply stays unreviewed.
        svc.record_verdict(transcript_id, claim_id, verdict,
                           reason=reason, new_statement=statement)
        return RedirectResponse(f"/transcripts/{transcript_id}/review",
                                status_code=303)

    # -- documents ---------------------------------------------------------
    @app.get("/transcripts/{transcript_id}/report", response_class=HTMLResponse)
    def consultant_report(request: Request, transcript_id: str) -> HTMLResponse:
        posture, warn = svc.posture()
        page = svc.consultant_report_page(transcript_id)
        if page is None:
            return HTMLResponse(views.message(title="Not found", text="Unknown transcript.",
                                              posture=posture, warn=warn), status_code=404)
        return HTMLResponse(views.consultant_report_page(
            transcript_id=page["transcript_id"], participant=page["participant"],
            findings=page["findings"], grounding=page["grounding"],
            posture=posture, warn=warn))

    @app.get("/transcripts/{transcript_id}/employer", response_class=HTMLResponse)
    def employer_release(request: Request, transcript_id: str) -> HTMLResponse:
        posture, warn = svc.posture()
        transcript = svc.load_transcript(transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found", text="Unknown transcript.",
                                              posture=posture, warn=warn), status_code=404)
        markdown = svc.employer_release_markdown([transcript_id])
        # k-anonymity needs a group: point the consultant at the engagement-level
        # release, which is where the threshold can actually be met. The anchor
        # is built in views — routes do not hand-assemble HTML.
        note_html = views.engagement_release_note(
            transcript.engagement_id,
            svc.engagement_name(transcript.engagement_id))
        return HTMLResponse(views.document(
            title="Employer release", subtitle=f"{transcript_id} · through the privacy firewall",
            markdown=markdown, back=f"/transcripts/{transcript_id}/review",
            posture=posture, warn=warn,
            note_html=note_html))

    @app.post("/demo/run")
    def run_demo(request: Request):
        from ..application.demo import run_demo_engagement

        result = run_demo_engagement(svc)
        return RedirectResponse(
            f"/engagements/{result.engagement_id}/deliverables", status_code=303)

    @app.get("/engagements/{engagement_id}/synthesis", response_class=HTMLResponse)
    def engagement_synthesis(request: Request, engagement_id: str) -> HTMLResponse:
        posture, warn = svc.posture()
        transcripts = svc.transcripts_for_engagement(engagement_id)
        if not transcripts:
            return HTMLResponse(views.message(
                title="No interviews in this engagement",
                text="Run the demo or start interviews into it first.",
                posture=posture, warn=warn), status_code=404)
        markdown = svc.engagement_synthesis_markdown(engagement_id)
        auto = svc.auto_validated(transcripts)
        return HTMLResponse(views.document(
            title="Engagement synthesis",
            subtitle=f"{svc.engagement_name(engagement_id)} · "
                     f"{len(transcripts)} interviews · attributed verbatim detail "
                     f"(consultant view)",
            markdown=markdown, back="/", posture=posture, warn=warn,
            note=("Some or all verdicts in this engagement were recorded by the "
                  "auto-sim reviewer (a demo), not a human consultant."
                  if auto else
                  "Every verdict in this engagement was recorded by a human "
                  "consultant through the review page.")))

    @app.get("/engagements/{engagement_id}/employer", response_class=HTMLResponse)
    def engagement_employer(request: Request, engagement_id: str) -> HTMLResponse:
        """The employer's document for ONE engagement — the thing you hand over.

        This is the route the per-transcript employer page points at: k-anonymity
        needs a group, and only an engagement can provide one.
        """
        posture, warn = svc.posture()
        try:
            markdown = svc.employer_release_markdown(engagement_id=engagement_id)
        except ValueError:
            # The service contract refuses scopes that resolve to nothing; the
            # route turns that into the honest 404.
            return HTMLResponse(views.message(
                title="No interviews in this engagement",
                text="Run the demo or start interviews into it first.",
                posture=posture, warn=warn), status_code=404)
        return HTMLResponse(views.document(
            title="Employer release",
            subtitle=f"{svc.engagement_name(engagement_id)} · "
                     f"{len(svc.transcripts_for_engagement(engagement_id))} "
                     f"interviews · aggregated, k-anonymity {employer_k}",
            markdown=markdown, back="/", posture=posture, warn=warn,
            note="This is what the employer receives: group-level findings only, no "
                 "names, no verbatim quotes, and disagreements reported without "
                 "sides. Topics below the k threshold are listed as withheld, not "
                 "summarised."))

    @app.get("/engagements/{engagement_id}/deliverables",
             response_class=HTMLResponse)
    def engagement_deliverables(request: Request,
                                engagement_id: str) -> HTMLResponse:
        """Both documents, side by side — the demo's pitch page.

        Consultant synthesis on the left (inside the firewall: attributed,
        verbatim), employer release on the right (aggregate-only, withheld
        ledger visible). The contrast IS the product.
        """
        posture, warn = svc.posture()
        transcripts = svc.transcripts_for_engagement(engagement_id)
        if not transcripts:
            return HTMLResponse(views.message(
                title="No interviews in this engagement",
                text="Run the demo or start interviews into it first.",
                posture=posture, warn=warn), status_code=404)
        synthesis = svc.engagement_synthesis_markdown(engagement_id)
        employer = svc.employer_release_markdown(engagement_id=engagement_id)
        auto = svc.auto_validated(transcripts)
        return HTMLResponse(views.deliverables(
            engagement_name=svc.engagement_name(engagement_id),
            interview_count=len(transcripts), k_anonymity=employer_k,
            synthesis_md=synthesis, employer_md=employer,
            auto_validated=auto, posture=posture, warn=warn))

    @app.get("/engagement", response_class=HTMLResponse)
    def engagement(request: Request) -> HTMLResponse:
        posture, warn = svc.posture()
        markdown = svc.employer_release_markdown()
        count = sum(1 for tid in svc.store.list_ids()
                    if svc.load_transcript(tid) is not None)
        return HTMLResponse(views.document(
            title="Engagement report (employer release)",
            subtitle=f"{count} interviews · aggregated, k-anonymity {employer_k}",
            markdown=markdown, back="/", posture=posture, warn=warn,
            note="This is what the employer receives: group-level findings only, no "
                 "names, no verbatim quotes, and disagreements reported without sides."))

    return app
