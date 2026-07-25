"""The consultant workspace: routes over the existing pipeline.

Deliberate boundaries:

  * **Consultant-only.** There is no employer surface. The employer's document is
    produced by ``privacy.release`` and read here; it is never a page they log into.
  * **No domain logic.** Every route delegates to the engine — driver, store, tagger,
    validation gate, release gate — so the app cannot drift from the guarantees the
    engine enforces.
  * **No authentication, on purpose.** This is a localhost single-consultant tool for
    the Year-0/1 experiments. Auth arrives with the second user (Art. XIX: do not
    generalise before a second real user exists); the startup banner says so rather
    than leaving it implied.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..aggregation.aggregator import aggregate
from ..aggregation.model import participant_finding_from_claim
from ..aggregation.relation import make_relation_checker
from ..config import Settings, get_llm_client, load_settings
from ..evidence.tagger import EvidenceTagger
from ..interview.driver import InterviewDriver
from ..interview.engine import InterviewEngine
from ..interview.session import DEFAULT_OBJECTIVE
from ..persistence.event_log import EventLog
from ..persistence.invitations import InvitationStore
from ..persistence.transcript_store import TranscriptNotFound, TranscriptStore
from ..privacy import Pseudonymizer, ReleasePolicy, release, render_release_report
from ..report.generator import render_markdown_report
from ..subjects.simulated import SimulatedInterviewee, default_persona
from ..transcript.model import Speaker, Transcript
from ..validation.gate import ValidationGate
from ..validation.model import Correction, ValidatedFinding, Validator, Verdict
from . import views
from .ledger import read_verdicts


@dataclass
class LiveInterview:
    """An interview in progress across HTTP requests."""

    driver: InterviewDriver
    participant_label: str        # pseudonym — the real name is not kept here
    subject: object | None = None  # a simulated persona, when demoing
    question: str | None = None


@dataclass
class Workspace:
    """Process-local state for the single consultant using this instance."""

    settings: Settings
    pseudonymizer: Pseudonymizer
    live: dict[str, LiveInterview] = field(default_factory=dict)

    @property
    def store(self) -> TranscriptStore:
        return TranscriptStore(self.settings.data_dir, self.settings.cipher())

    def posture(self) -> tuple[str, bool]:
        banner = self.settings.posture_banner()
        unsafe = (not self.settings.has_live_model) or (not self.store.encrypted)
        return banner, unsafe


def _tag(transcript: Transcript, settings: Settings):
    return EvidenceTagger(llm=get_llm_client(settings)).tag(transcript)


def _validator() -> Validator:
    # A single-consultant local tool: the operator IS the validator. When a second
    # user exists, this becomes an authenticated identity (see module docstring).
    return Validator(id="val-consultant", display_name="Consultant", kind="consultant")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    # Refuse to serve real interviews from an unsafe configuration.
    settings.assert_deployable()

    workspace = Workspace(settings=settings, pseudonymizer=Pseudonymizer())
    app = FastAPI(title="Ontora consultant workspace", docs_url=None, redoc_url=None)
    app.state.workspace = workspace

    def ws(request: Request) -> Workspace:
        return request.app.state.workspace

    # -- dashboard ---------------------------------------------------------
    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        store = w.store
        interviews = []
        for tid in store.list_ids():
            try:
                transcript = store.load(tid)
            except Exception:
                continue
            tagging = _tag(transcript, w.settings)
            verdicts = read_verdicts(w.settings.data_dir, tid)
            interviews.append({
                "id": tid,
                "participant": transcript.interview_id or "—",
                "segments": len(transcript.segments),
                "claims": len(tagging.claims),
                "validated": sum(1 for c in tagging.claims if c.id in verdicts),
            })
        live = [
            {"id": tid, "turns": item.driver.state.turn_count,
             "status": "closed" if item.driver.closed else "awaiting answer"}
            for tid, item in w.live.items()
        ]
        return HTMLResponse(views.dashboard(
            interviews=interviews, live=live, posture=posture, warn=warn))

    # -- invitations -------------------------------------------------------
    @app.post("/invitations/new")
    def invite(request: Request, participant: str = Form(...),
               base_url: str = Form("http://127.0.0.1:8100")) -> RedirectResponse:
        """Create an invitation for the employee surface.

        The pseudonym is assigned here, on the consultant's side, so the interview
        surface never asks the participant for a name — there is no field for it.
        """
        w = ws(request)
        alias = w.pseudonymizer.pseudonym(participant.strip() or "unknown")
        InvitationStore(w.settings.data_dir).create(pseudonym=alias)
        return RedirectResponse("/invitations", status_code=303)

    @app.get("/invitations", response_class=HTMLResponse)
    def invitations(request: Request) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        items = [
            {"token": i.token, "pseudonym": i.pseudonym, "status": i.status,
             "transcript_id": i.transcript_id or ""}
            for i in InvitationStore(w.settings.data_dir).list_all()
        ]
        return HTMLResponse(views.invitations(
            items=items, posture=posture, warn=warn))

    # -- interview ---------------------------------------------------------
    @app.post("/interviews/new")
    def start_interview(request: Request, participant: str = Form(...),
                        mode: str = Form("manual")) -> RedirectResponse:
        w = ws(request)
        # Pseudonymise at ingest: the real name goes no further than this call.
        alias = w.pseudonymizer.pseudonym(participant.strip() or "unknown")
        transcript = Transcript(engagement_id="eng-local", tenant_id="tenant-local")
        transcript.interview_id = alias

        llm = get_llm_client(w.settings)
        driver = InterviewDriver(
            engine=InterviewEngine(llm=llm, max_turns=w.settings.max_turns),
            transcript=transcript,
            objective=DEFAULT_OBJECTIVE,
            event_log=EventLog(w.settings.data_dir, transcript.id, layer="testimony"),
            max_turns=w.settings.max_turns,
        )
        subject = None
        if mode == "simulated":
            subject = SimulatedInterviewee(default_persona("open"), llm=llm)

        item = LiveInterview(driver=driver, participant_label=alias, subject=subject)
        item.question = driver.next_question()
        if subject is not None:
            _run_simulated(item)
        w.live[transcript.id] = item
        return RedirectResponse(f"/interviews/{transcript.id}", status_code=303)

    def _run_simulated(item: LiveInterview) -> None:
        """Let a simulated persona answer to completion (demo mode)."""
        while item.question is not None and not item.driver.closed:
            item.driver.submit_answer(item.subject.answer(item.question))
            item.question = item.driver.next_question()

    @app.get("/interviews/{interview_id}", response_class=HTMLResponse)
    def interview(request: Request, interview_id: str) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        item = w.live.get(interview_id)
        if item is None:
            return HTMLResponse(views.message(
                title="Interview not found",
                text="It may already be finalised — check the stored interviews.",
                posture=posture, warn=warn), status_code=404)
        segments = [{"id": s.id, "speaker": s.speaker.value, "text": s.text}
                    for s in item.driver.transcript.segments]
        return HTMLResponse(views.runner(
            interview_id=interview_id, participant=item.participant_label,
            question=item.question, turns=item.driver.state.turn_count,
            max_turns=w.settings.max_turns,
            transcript_html=views.transcript_turns(segments),
            closed=item.driver.closed or item.question is None,
            coverage=item.driver.state.summary(), posture=posture, warn=warn))

    @app.post("/interviews/{interview_id}/answer")
    def answer(request: Request, interview_id: str,
               answer: str = Form(...)) -> RedirectResponse:
        w = ws(request)
        item = w.live.get(interview_id)
        if item is not None and not item.driver.closed and item.question is not None:
            item.driver.submit_answer(answer)
            item.question = item.driver.next_question()
        return RedirectResponse(f"/interviews/{interview_id}", status_code=303)

    @app.post("/interviews/{interview_id}/finish")
    def finish(request: Request, interview_id: str) -> RedirectResponse:
        w = ws(request)
        item = w.live.pop(interview_id, None)
        if item is None:
            return RedirectResponse("/", status_code=303)
        transcript = item.driver.finish()
        # Store it, so every quote stays verifiable after this process exits.
        w.store.save(transcript, overwrite=True)
        return RedirectResponse(f"/transcripts/{transcript.id}/review", status_code=303)

    # -- transcript & review ----------------------------------------------
    def _load(w: Workspace, transcript_id: str) -> Transcript | None:
        try:
            return w.store.load(transcript_id)
        except (TranscriptNotFound, Exception):
            return None

    @app.get("/transcripts/{transcript_id}", response_class=HTMLResponse)
    def transcript_view(request: Request, transcript_id: str) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        transcript = _load(w, transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found",
                                              text="No stored transcript with that id.",
                                              posture=posture, warn=warn), status_code=404)
        segments = [{"id": s.id, "speaker": s.speaker.value, "text": s.text}
                    for s in transcript.segments]
        body = views.document(
            title=f"Transcript {transcript_id}",
            subtitle=f"{len(segments)} segments · immutable",
            markdown=transcript.render(),
            back=f"/transcripts/{transcript_id}/review",
            posture=posture, warn=warn,
            note="The stored record. Every quote in every report resolves to a span here.")
        return HTMLResponse(body)

    @app.get("/transcripts/{transcript_id}/review", response_class=HTMLResponse)
    def review(request: Request, transcript_id: str) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        transcript = _load(w, transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found",
                                              text="No stored transcript with that id.",
                                              posture=posture, warn=warn), status_code=404)
        tagging = _tag(transcript, w.settings)
        verdicts = read_verdicts(w.settings.data_dir, transcript_id)
        items = []
        for claim in tagging.claims:
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
        w = ws(request)
        transcript = _load(w, transcript_id)
        if transcript is None:
            return RedirectResponse("/", status_code=303)
        claim = next((c for c in _tag(transcript, w.settings).claims
                      if c.id == claim_id), None)
        if claim is None:
            return RedirectResponse(f"/transcripts/{transcript_id}/review",
                                    status_code=303)

        gate = ValidationGate(_validator(),
                              EventLog(w.settings.data_dir, transcript_id,
                                       layer="validation"))
        try:
            chosen = Verdict(verdict)
        except ValueError:
            return RedirectResponse(f"/transcripts/{transcript_id}/review",
                                    status_code=303)
        correction = None
        if chosen is Verdict.AMENDED:
            correction = Correction(new_statement=statement.strip() or None)
        try:
            # The gate enforces the invariants: a reason is required to amend or
            # reject, and the evidence reviewed is recorded with the decision.
            gate.decide(claim, chosen, reason.strip(), correction)
        except Exception:
            pass  # invalid decision (e.g. no reason) — the page will still show it unreviewed
        return RedirectResponse(f"/transcripts/{transcript_id}/review", status_code=303)

    # -- documents ---------------------------------------------------------
    def _validated_findings(w: Workspace, transcript: Transcript) -> list[ValidatedFinding]:
        """Rebuild ValidatedFindings from the recorded decisions."""
        from ..validation.model import ValidationDecision

        tagging = _tag(transcript, w.settings)
        verdicts = read_verdicts(w.settings.data_dir, transcript.id)
        findings: list[ValidatedFinding] = []
        for claim in tagging.claims:
            recorded = verdicts.get(claim.id)
            if recorded is None:
                continue
            try:
                decision = ValidationDecision(
                    id=f"val-{claim.id}",
                    claim_id=claim.id,
                    verdict=Verdict(recorded.verdict),
                    validator=_validator(),
                    reviewed_evidence=tuple(e.ref for e in claim.evidence),
                    reason=recorded.reason or "recorded",
                    correction=(Correction(new_statement=recorded.new_statement)
                                if recorded.verdict == Verdict.AMENDED.value
                                and recorded.new_statement else None),
                )
            except Exception:
                continue
            findings.append(ValidatedFinding(claim=claim, decision=decision))
        return findings

    @app.get("/transcripts/{transcript_id}/report", response_class=HTMLResponse)
    def consultant_report(request: Request, transcript_id: str) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        transcript = _load(w, transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found", text="Unknown transcript.",
                                              posture=posture, warn=warn), status_code=404)
        markdown = render_markdown_report(
            transcript=transcript,
            findings=_validated_findings(w, transcript),
            objective=DEFAULT_OBJECTIVE,
            engagement_id=transcript.engagement_id,
            interview_id=transcript.id,
            validator_kind="consultant",
            validator_name="Consultant",
        )
        return HTMLResponse(views.document(
            title="Consultant report", subtitle=f"{transcript_id} · validated findings only",
            markdown=markdown, back=f"/transcripts/{transcript_id}/review",
            posture=posture, warn=warn,
            note="Only findings you accepted or amended appear. Each carries the quote "
                 "it rests on."))

    @app.get("/transcripts/{transcript_id}/employer", response_class=HTMLResponse)
    def employer_release(request: Request, transcript_id: str) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        transcript = _load(w, transcript_id)
        if transcript is None:
            return HTMLResponse(views.message(title="Not found", text="Unknown transcript.",
                                              posture=posture, warn=warn), status_code=404)
        findings = [
            participant_finding_from_claim(
                f.claim, transcript,
                participant_id=transcript.interview_id or "P-unknown",
                participant_name=transcript.interview_id or "P-unknown")
            for f in _validated_findings(w, transcript) if f.is_reportable
        ]
        aggregation = aggregate(findings, make_relation_checker(get_llm_client(w.settings)))
        # A single interview cannot satisfy k-anonymity; k=1 here is honest about
        # that rather than pretending one voice is a group.
        package = release(aggregation, policy=ReleasePolicy.for_employer(k_anonymity=1))
        markdown = render_release_report(package, org_name="This engagement",
                                         interview_count=1)
        return HTMLResponse(views.document(
            title="Employer release", subtitle=f"{transcript_id} · through the privacy firewall",
            markdown=markdown, back=f"/transcripts/{transcript_id}/review",
            posture=posture, warn=warn,
            note="A single interview cannot be anonymous within itself. Release an "
                 "engagement-level report instead once several people have been "
                 "interviewed — see the engagement report."))

    @app.get("/engagement", response_class=HTMLResponse)
    def engagement(request: Request) -> HTMLResponse:
        w = ws(request)
        posture, warn = w.posture()
        store = w.store
        findings = []
        count = 0
        for tid in store.list_ids():
            transcript = _load(w, tid)
            if transcript is None:
                continue
            count += 1
            alias = transcript.interview_id or f"P-{tid[-6:]}"
            for f in _validated_findings(w, transcript):
                if f.is_reportable:
                    findings.append(participant_finding_from_claim(
                        f.claim, transcript, participant_id=alias, participant_name=alias))
        aggregation = aggregate(findings, make_relation_checker(get_llm_client(w.settings)))
        package = release(aggregation, policy=ReleasePolicy.for_employer(k_anonymity=2))
        markdown = render_release_report(package, org_name="This engagement",
                                         interview_count=count)
        return HTMLResponse(views.document(
            title="Engagement report (employer release)",
            subtitle=f"{count} interviews · aggregated, k-anonymity 2",
            markdown=markdown, back="/", posture=posture, warn=warn,
            note="This is what the employer receives: group-level findings only, no "
                 "names, no verbatim quotes, and disagreements reported without sides."))

    return app
