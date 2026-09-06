"""The one-click demo engagement — the whole product in sixty seconds.

The demo org's nine synthetic personas are interviewed **in parallel** (the
thing that makes this product interesting is that forty interviews cost the
same wall-clock as one), their claims pass the two evidence gates, an auto-sim
reviewer labels its own verdicts honestly (a machine verdict is never recorded
as a human one), and both deliverables come out the other end: the consultant's
synthesis and the employer's firewalled release — corroborated topics released
at k=3, single- and double-voice topics withheld into the ledger by design.

In mock mode the run is deterministic — a pitch never breaks from a flaky
network. With a live model configured, the same button runs real interviews and
simply takes longer.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from ..config import get_llm_client
from ..evidence.tagger import EvidenceTagger
from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..persistence.event_log import EventLog
from ..persistence.transcript_store import TranscriptStore
from ..subjects.simulated import SimulatedInterviewee
from ..transcript.model import Transcript
from ..validation.gate import AutoValidator, ValidationGate, validate_claims
from .service import ConsultantService


@dataclass
class DemoResult:
    engagement_id: str
    engagement_name: str
    interviews: list[dict] = field(default_factory=list)

    @property
    def claims(self) -> int:
        return sum(i["claims"] for i in self.interviews)


def run_demo_engagement(
    service: ConsultantService,
    *,
    engagement_name: str = "Speedrun demo",
    max_workers: int | None = None,
) -> DemoResult:
    """Interview the demo org in parallel and produce every deliverable.

    ``max_workers`` defaults to the org's size — the whole point being that
    nine interviews cost the same wall-clock as one.
    """
    settings = service.settings
    engagement = service.create_engagement(engagement_name)
    llm = get_llm_client(settings)
    personas = sorted(_personas(), key=lambda p: p.name)
    workers = max_workers or len(personas)

    # Pseudonyms are assigned serially before the threads start: the mapping is
    # in-memory state, and pre-issuing keeps parallelism from racing it.
    assignments = [(persona, service.pseudonymizer.pseudonym(persona.name))
                   for persona in personas]
    service.pseudonymizer.save_state(settings.data_dir, settings.cipher())

    def interview_one(item) -> dict:
        persona, alias = item
        transcript = Transcript(engagement_id=engagement["id"],
                                tenant_id="tenant-demo")
        transcript.interview_id = alias
        engine = InterviewEngine(llm=llm, max_turns=settings.max_turns)
        subject = SimulatedInterviewee(persona, llm=llm)
        result = run_interview(
            engine=engine, subject=subject,
            transcript=transcript,
            event_log=EventLog(settings.data_dir, transcript.id,
                               layer="testimony", cipher=settings.cipher()),
            max_turns=settings.max_turns,
        )
        # Write-once: each thread stores its own fresh transcript.
        TranscriptStore(settings.data_dir, settings.cipher()).save(result.transcript)

        # The auto-sim reviewer labels its own verdicts through the same gate a
        # human uses, into the real validation ledger — the synthesis reads
        # verdicts back from there, so a demo run is indistinguishable in
        # structure from a hand-reviewed one (and the ledger says which is which).
        tagging = EvidenceTagger(llm=llm).tag(result.transcript)
        gate = ValidationGate(
            AutoValidator.VALIDATOR,
            EventLog(settings.data_dir, transcript.id, layer="validation",
                     cipher=settings.cipher()))
        findings = validate_claims(gate, tagging.claims, AutoValidator().decide)
        return {
            "participant": persona.name,
            "pseudonym": alias,
            "transcript_id": transcript.id,
            "claims": len(tagging.claims),
            "validated": sum(1 for f in findings if f.is_reportable),
        }

    with ThreadPoolExecutor(max_workers=workers) as pool:
        interviews = list(pool.map(interview_one, assignments))

    return DemoResult(engagement_id=engagement["id"],
                      engagement_name=engagement["name"], interviews=interviews)


def _personas():
    # Imported here so the module (and the application package) stays importable
    # without the synthetic testbed's dependencies — it has none, but the import
    # graph stays honest about what a demo needs.
    from ..aggregation.scenario import northwind_org

    return northwind_org("open")
