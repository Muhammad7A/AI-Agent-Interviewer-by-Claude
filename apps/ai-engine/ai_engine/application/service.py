"""The consultant's use-cases, as one service.

Every public method is a use-case the product actually performs:

  invite → start → answer … → finish → tag → validate → report → release

The web routes and the CLI are presentations of these; none of the orchestration
lives in them anymore. A use-case method either completes and returns data, or
raises — it never returns a half-applied state, because the pipeline behind it
(the driver's fold-before-model-call, the write-once stores, the validation gate)
enforces that itself.

The service is deliberately in-memory only for *live* interviews (an interview in
progress has not been consented to); everything that crosses a request boundary
is durable through the same stores the engine uses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..aggregation.aggregator import aggregate
from ..aggregation.model import participant_finding_from_claim
from ..aggregation.relation import make_relation_checker
from ..config import Settings, get_llm_client
from ..evidence.tagger import EvidenceTagger
from ..interview.driver import InterviewDriver
from ..interview.engine import InterviewEngine
from ..interview.session import DEFAULT_OBJECTIVE
from ..llm.retry import LLMError
from ..persistence.engagements import DEFAULT_ENGAGEMENT, EngagementStore
from ..persistence.event_log import EventLog
from ..persistence.invitations import InvitationStore
from ..persistence.ledger import read_verdicts
from ..persistence.reports import save_report
from ..persistence.transcript_store import TranscriptStore
from ..privacy import Pseudonymizer, ReleasePolicy, release, render_release_report
from ..report.generator import render_markdown_report
from ..subjects.simulated import SimulatedInterviewee, default_persona
from ..transcript.model import Speaker, Transcript
from ..validation.gate import ValidationGate
from ..validation.model import (
    Correction,
    ValidatedFinding,
    ValidationDecision,
    Validator,
    Verdict,
)


@dataclass
class LiveInterview:
    """A consultant-run interview in progress across requests."""

    driver: InterviewDriver
    participant_label: str          # pseudonym — the real name is not kept here
    subject: object | None = None   # a simulated persona, when demoing
    question: str | None = None
    #: Set when a model call failed after an answer was recorded; the next
    #: :meth:`view` retries the pending question. Recoverable, not over.
    stalled: bool = False

    @property
    def transcript_id(self) -> str:
        return self.driver.transcript.id


ANSWER_RECORDED = "recorded"
ANSWER_TOO_LONG = "too_long"
ANSWER_INACTIVE = "inactive"


class ConsultantService:
    """Use-cases over the engine. One instance per consultant workspace."""

    def __init__(self, settings: Settings,
                 pseudonymizer: Pseudonymizer | None = None) -> None:
        self.settings = settings
        # The identity mapping goes through the same cipher as every other store.
        # It maps real names to pseudonyms, so it is the one artifact that converts
        # the whole pseudonymous corpus back to named employees — it was the only
        # store exempt from the at-rest rule, and in production it now refuses to
        # be written in plaintext like the rest.
        self.pseudonymizer = pseudonymizer or Pseudonymizer.load_or_create(
            settings.data_dir, settings.cipher())
        self._live: dict[str, LiveInterview] = {}

    # -- posture ------------------------------------------------------------
    @property
    def store(self) -> TranscriptStore:
        return TranscriptStore(self.settings.data_dir, self.settings.cipher())

    def posture(self) -> tuple[str, bool]:
        banner = self.settings.posture_banner()
        unsafe = (not self.settings.has_live_model) or (not self.store.encrypted)
        return banner, unsafe

    # -- engagements ----------------------------------------------------------
    def create_engagement(self, name: str) -> dict:
        """A named mandate: the group of interviews one synthesis will come from."""
        return EngagementStore(self.settings.data_dir).create(name)

    def list_engagements(self) -> list[dict]:
        store = EngagementStore(self.settings.data_dir)
        counts: dict[str, int] = {}
        for tid in self.store.list_ids():
            transcript = self.load_transcript(tid)
            if transcript is None:
                continue
            counts[transcript.engagement_id] = counts.get(transcript.engagement_id, 0) + 1
        rows = []
        for e in store.list():
            rows.append({**e, "interviews": counts.get(e["id"], 0)})
        return rows

    def engagement_name(self, engagement_id: str) -> str:
        e = EngagementStore(self.settings.data_dir).get(engagement_id)
        return e["name"] if e else engagement_id

    def resolve_engagement(self, name: str) -> str:
        """The engagement id for a name — matched case-insensitively, created
        when new. Blank means the ad-hoc default engagement."""
        store = EngagementStore(self.settings.data_dir)
        wanted = name.strip()
        if not wanted:
            store.ensure(DEFAULT_ENGAGEMENT)
            return DEFAULT_ENGAGEMENT
        for e in store.list():
            if e["name"].lower() == wanted.lower():
                return e["id"]
        return store.create(wanted)["id"]

    # -- invitations ----------------------------------------------------------
    def invite(self, participant: str) -> str:
        """Pseudonymize at ingest and create an invitation for the employee surface."""
        alias = self.pseudonymizer.pseudonym(participant.strip() or "unknown")
        self.pseudonymizer.save_state(self.settings.data_dir, self.settings.cipher())
        return InvitationStore(self.settings.data_dir).create(pseudonym=alias).token

    def list_invitations(self) -> list:
        return InvitationStore(self.settings.data_dir).list_all()

    def invite_batch(self, names: str) -> list[str]:
        """One invitation per line of a pasted roster; blank lines skipped."""
        tokens = []
        for line in names.splitlines():
            if not line.strip():
                continue
            tokens.append(self.invite(line))
        return tokens

    def transcripts_for_engagement(self, engagement_id: str) -> list[str]:
        return [tid for tid in self.store.list_ids()
                if (t := self.load_transcript(tid)) is not None
                and t.engagement_id == engagement_id]

    # -- consultant-run interviews -------------------------------------------
    def start(self, participant: str, *, simulated: bool = False,
              engagement_id: str = DEFAULT_ENGAGEMENT) -> str:
        """Begin an interview; returns the transcript id.

        Raises :class:`LLMError` when the first model call fails — nothing has
        been registered, so the caller can simply offer a retry.
        """
        EngagementStore(self.settings.data_dir).ensure(engagement_id)
        alias = self.pseudonymizer.pseudonym(participant.strip() or "unknown")
        self.pseudonymizer.save_state(self.settings.data_dir, self.settings.cipher())
        transcript = Transcript(engagement_id=engagement_id, tenant_id="tenant-local")
        transcript.interview_id = alias

        llm = get_llm_client(self.settings)
        driver = InterviewDriver(
            engine=InterviewEngine(llm=llm, max_turns=self.settings.max_turns),
            transcript=transcript,
            objective=DEFAULT_OBJECTIVE,
            event_log=EventLog(self.settings.data_dir, transcript.id,
                               layer="testimony", cipher=self.settings.cipher()),
            max_turns=self.settings.max_turns,
        )
        item = LiveInterview(driver=driver, participant_label=alias)
        item.question = driver.next_question()
        if simulated:
            item.subject = SimulatedInterviewee(default_persona("open"), llm=llm)
            self._run_simulated(item)
        self._live[transcript.id] = item
        return transcript.id

    def _run_simulated(self, item: LiveInterview) -> None:
        """Let a simulated persona answer to completion (demo mode)."""
        while item.question is not None and not item.driver.closed:
            item.driver.submit_answer(item.subject.answer(item.question))
            item.question = item.driver.next_question()

    def view(self, transcript_id: str) -> dict | None:
        """Everything the interview page needs, retrying a stalled turn first."""
        item = self._live.get(transcript_id)
        if item is None:
            return None
        stalled = False
        if item.stalled and not item.driver.closed:
            try:
                item.question = item.driver.next_question()
                item.stalled = False
            except LLMError:
                stalled = True
        segments = [{"id": s.id, "speaker": s.speaker.value, "text": s.text}
                    for s in item.driver.transcript.segments]
        return {
            "participant": item.participant_label,
            "question": item.question,
            "turns": item.driver.state.turn_count,
            "closed": item.driver.closed or item.question is None,
            "stalled": stalled,
            "coverage": item.driver.state.summary(),
            "segments": segments,
        }

    def submit_answer(self, transcript_id: str, answer: str) -> str:
        """Record an answer and fetch the next question.

        Returns :data:`ANSWER_RECORDED`, :data:`ANSWER_TOO_LONG` (nothing was
        recorded — the cap exists so one oversized paste cannot wedge the
        session), or :data:`ANSWER_INACTIVE` when there is no live interview
        awaiting an answer.
        """
        item = self._live.get(transcript_id)
        if item is None or item.driver.closed or item.question is None:
            return ANSWER_INACTIVE
        if len(answer) > self.settings.max_answer_chars:
            return ANSWER_TOO_LONG
        item.driver.submit_answer(answer)
        try:
            item.question = item.driver.next_question()
        except LLMError:
            # The answer is recorded; only the NEXT question failed. The view
            # retries rather than losing the session to one transient failure.
            item.question = None
            item.stalled = True
        return ANSWER_RECORDED

    def finish(self, transcript_id: str) -> str | None:
        """Close, finalize, and store — the transcript becomes immutable."""
        item = self._live.pop(transcript_id, None)
        if item is None:
            return None
        transcript = item.driver.finish()
        try:
            self.store.save(transcript)
        except FileExistsError:
            pass  # already stored; write-once wins, the review page is next
        return transcript.id

    def auto_validated(self, transcript_ids: list[str]) -> bool:
        """Whether any verdict across these interviews was recorded by a machine.

        The surfaces must disclose machine validation (the demo pages say so
        next to the deliverables), and the kind string lives in one place —
        validation.gate.AUTO_SIM_KIND — so a rename there cannot silently turn
        auto-validated work into something that presents as human-validated.
        """
        from ..validation.gate import AUTO_SIM_KIND

        return any(AUTO_SIM_KIND in (v.validator_kind or "")
                   for tid in transcript_ids
                   for v in self.verdicts(tid).values())

    def live_summary(self) -> list[dict]:
        return [{"id": tid, "turns": item.driver.state.turn_count,
                 "status": "closed" if item.driver.closed else "awaiting answer"}
                for tid, item in self._live.items()]

    # -- stored-review pipeline ------------------------------------------------
    def load_transcript(self, transcript_id: str) -> Transcript | None:
        try:
            return self.store.load(transcript_id)
        except Exception:
            return None

    def tag(self, transcript_id: str) -> TaggingResult | None:
        transcript = self.load_transcript(transcript_id)
        if transcript is None:
            return None
        return EvidenceTagger(llm=get_llm_client(self.settings)).tag(transcript)

    def verdicts(self, transcript_id: str) -> dict:
        return read_verdicts(self.settings.data_dir, transcript_id,
                             self.settings.cipher())

    @staticmethod
    def _validator() -> Validator:
        # A single-consultant local tool: the operator IS the validator. When a
        # second user exists, this becomes an authenticated identity.
        return Validator(id="val-consultant", display_name="Consultant",
                         kind="consultant")

    def record_verdict(self, transcript_id: str, claim_id: str, verdict: str,
                       reason: str = "", new_statement: str = "",
                       validator: Validator | None = None) -> bool:
        """Record one validation decision through the gate's invariants.

        The validator defaults to the consultant identity; the demo passes the
        auto-sim validator, because a machine verdict must never be recorded as
        a human one.
        """
        transcript = self.load_transcript(transcript_id)
        if transcript is None:
            return False
        tagging = self.tag(transcript_id)
        claim = next((c for c in tagging.claims if c.id == claim_id), None) \
            if tagging else None
        if claim is None:
            return False
        try:
            chosen = Verdict(verdict)
        except ValueError:
            return False
        correction = None
        if chosen is Verdict.AMENDED:
            correction = Correction(new_statement=new_statement.strip() or None)
        gate = ValidationGate(
            validator or self._validator(),
            EventLog(self.settings.data_dir, transcript_id, layer="validation",
                     cipher=self.settings.cipher()))
        try:
            gate.decide(claim, chosen, reason.strip(), correction)
        except Exception:
            return False  # invalid decision (e.g. no reason); stays unreviewed
        return True

    def validated_findings(self, transcript_id: str) -> list[ValidatedFinding]:
        """Rebuild ValidatedFindings from the recorded decisions."""
        transcript = self.load_transcript(transcript_id)
        if transcript is None:
            return []
        tagging = self.tag(transcript_id)
        verdicts = self.verdicts(transcript_id)
        findings: list[ValidatedFinding] = []
        for claim in (tagging.claims if tagging else []):
            recorded = verdicts.get(claim.id)
            if recorded is None:
                continue
            try:
                decision = ValidationDecision(
                    id=f"val-{claim.id}",
                    claim_id=claim.id,
                    verdict=Verdict(recorded.verdict),
                    validator=self._validator(),
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

    # -- reports ---------------------------------------------------------------
    def _grounding_summary(self, transcript_id: str) -> dict | None:
        """What the gates admitted and refused, for the grounded-by-construction
        header. This is data from the tagging run, not copy."""
        tagging = self.tag(transcript_id)
        if tagging is None or tagging.report is None:
            return None
        r = tagging.report
        return {
            "proposed": r.total,
            "grounded": r.grounded,
            "unsourced": r.ungrounded,
            "unsupported": len(tagging.entailment_rejected),
            "confabulation": r.confabulation_rate,
        }

    def consultant_report_markdown(self, transcript_id: str) -> str | None:
        """The consultant's deliverable: validated findings only, quotes attached.

        Saved under the same at-rest policy as the testimony it cites.
        """
        transcript = self.load_transcript(transcript_id)
        if transcript is None:
            return None
        markdown = render_markdown_report(
            transcript=transcript,
            findings=self.validated_findings(transcript_id),
            objective=DEFAULT_OBJECTIVE,
            engagement_id=transcript.engagement_id,
            interview_id=transcript.id,
            validator_kind="consultant",
            validator_name="Consultant",
            grounding_summary=self._grounding_summary(transcript_id),
        )
        save_report(Path(self.settings.data_dir), f"{transcript_id}.report",
                    markdown, self.settings.cipher())
        return markdown

    def consultant_report_page(self, transcript_id: str) -> dict | None:
        """Everything the structured report page needs, or None if unknown."""
        transcript = self.load_transcript(transcript_id)
        if transcript is None:
            return None
        return {
            "transcript_id": transcript_id,
            "participant": transcript.interview_id or "—",
            "findings": self.validated_findings(transcript_id),
            "grounding": self._grounding_summary(transcript_id),
        }

    def _findings_for(self, transcripts: list[Transcript]) -> list:
        findings = []
        for transcript in transcripts:
            alias = transcript.interview_id or f"P-{transcript.id[-6:]}"
            for f in self.validated_findings(transcript.id):
                if f.is_reportable:
                    findings.append(participant_finding_from_claim(
                        f.claim, transcript,
                        participant_id=alias, participant_name=alias))
        # Transcript ids are random, so list order is random per run — and the
        # aggregation renders members in findings order. Sorting here makes the
        # rendered documents byte-stable between two demo runs (the
        # "deterministic pitch" promise survives a page diff).
        findings.sort(key=lambda f: (f.participant_id, f.statement))
        return findings

    def engagement_synthesis_markdown(self, engagement_id: str) -> str:
        """The consultant's cross-interview synthesis: corroboration, contradictions,
        candour. The consultant is inside the firewall, so this view keeps
        attributed, verbatim detail (policy: for_consultant)."""
        transcripts = [t for t in (self.load_transcript(tid)
                                   for tid in self.transcripts_for_engagement(engagement_id))
                       if t is not None]
        aggregation = aggregate(
            self._findings_for(transcripts),
            make_relation_checker(get_llm_client(self.settings)))
        package = release(aggregation, policy=ReleasePolicy.for_consultant())
        markdown = render_release_report(
            package, org_name=self.engagement_name(engagement_id),
            interview_count=len(transcripts))
        save_report(Path(self.settings.data_dir), f"synthesis.{engagement_id}",
                    markdown, self.settings.cipher())
        return markdown

    def employer_release_markdown(self, transcript_ids: list[str] | None = None, *,
                                  engagement_id: str | None = None,
                                  org_name: str | None = None) -> str:
        """The employer's document, through the firewall at the documented k.

        Scope it either with ``engagement_id`` or with an explicit
        ``transcript_ids`` list — never both. The contract is loud on purpose:
        a scope that resolves to nothing raises rather than rendering a
        plausible, completely empty report (passing an engagement id here used
        to iterate it character by character — fourteen "transcript ids" that
        all failed to load, zero exceptions, blank deliverable).
        """
        if engagement_id is not None and transcript_ids is not None:
            raise ValueError(
                "scope the release with engagement_id or transcript_ids, not both")
        if engagement_id is not None:
            transcript_ids = self.transcripts_for_engagement(engagement_id)
            if not transcript_ids:
                raise ValueError(
                    f"engagement {engagement_id!r} has no stored transcripts")
            if org_name is None:
                org_name = self.engagement_name(engagement_id)
        if transcript_ids is not None:
            if not isinstance(transcript_ids, list) or not transcript_ids:
                raise ValueError(
                    "transcript_ids must be a non-empty list of transcript ids")
            unknown = [tid for tid in transcript_ids
                       if self.load_transcript(tid) is None]
            if unknown:
                raise ValueError(f"unknown transcript id(s): {unknown[:3]}")
        if transcript_ids is None:
            transcripts = [t for t in (self.load_transcript(tid)
                                       for tid in self.store.list_ids())
                           if t is not None]
        else:
            transcripts = [t for t in (self.load_transcript(tid)
                                       for tid in transcript_ids)
                           if t is not None]
        aggregation = aggregate(
            self._findings_for(transcripts),
            make_relation_checker(get_llm_client(self.settings)))
        policy = ReleasePolicy.for_employer()
        package = release(aggregation, policy=policy)
        markdown = render_release_report(
            package,
            org_name=org_name or "This engagement",
            interview_count=len(transcripts))
        stem = ("org_report.employer" if engagement_id is None
                else f"org_report.employer.{engagement_id}")
        save_report(Path(self.settings.data_dir), stem,
                    markdown, self.settings.cipher())
        return markdown

    # -- dashboard ---------------------------------------------------------------
    def dashboard_rows(self) -> list[dict]:
        rows = []
        for tid in self.store.list_ids():
            transcript = self.load_transcript(tid)
            if transcript is None:
                continue
            tagging = self.tag(tid)
            verdicts = self.verdicts(tid)
            claims = tagging.claims if tagging else []
            rows.append({
                "id": tid,
                "participant": transcript.interview_id or "—",
                "engagement": self.engagement_name(transcript.engagement_id),
                "segments": len(transcript.segments),
                "claims": len(claims),
                "validated": sum(1 for c in claims if c.id in verdicts),
            })
        return rows
