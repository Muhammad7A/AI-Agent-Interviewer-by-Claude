"""The evaluation runner: scenario → interviewer → output → evaluation → score.

Four case units:

  * ``turn``   — a transcript prefix + candidate answer → the interviewer's
                 next turn (runs through the REAL driver, including resume
                 replay), graded by the scenario's rubric criteria.
  * ``gate``   — a claim/quote pair through the two evidence gates, compared
                 against the expected verdict.
  * ``report`` — a real minimal pipeline (interviews → gates → validation →
                 aggregation → release/report) rendered into a temp workspace,
                 graded for provenance and firewall behavior.
  * ``full``   — a whole conversation against a persona, graded on coverage.

Every run captures latency and an output hash; ``repeats`` runs of the same
scenario feed the consistency grader and the variance report. Results are
plain JSON (schemas.LAB_SCHEMA) so a baseline can be committed and diffed.
"""
from __future__ import annotations

import hashlib
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Settings, get_llm_client
from ..evidence.entailment import Entailment, HeuristicEntailmentChecker
from ..evidence.grounding import ground_proposal
from ..evidence.model import RawProposal
from ..evidence.tagger import EvidenceTagger
from ..interview.driver import InterviewDriver
from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..persistence.event_log import EventLog, NullEventLog
from ..persistence.transcript_store import TranscriptStore
from ..subjects.simulated import LatentTruth, Persona, SimulatedInterviewee
from ..transcript.model import Speaker, Transcript
from ..validation.gate import AutoValidator, ValidationGate, validate_claims
from .rubrics import RUBRIC_VERSION, Unscored, TurnContext, get_rubric
from .schemas import CriterionResult, Scenario, TurnEvaluation


@dataclass
class ScenarioVariance:
    """Repeatability analysis for one scenario across N runs."""

    scenario_id: str
    runs: int
    distinct_outputs: int
    failures: int
    score_min: float | None
    score_max: float | None
    latency_ms_mean: float
    latency_ms_stddev: float


@dataclass
class SuiteResult:
    suite_id: str
    mode: str
    evaluations: list[TurnEvaluation] = field(default_factory=list)
    variance: list[ScenarioVariance] = field(default_factory=list)


class _CapturingLog(NullEventLog):
    """Records emitted events so the lab grades what production recorded.

    The driver emits InterviewerAsked carrying the move's intent (technique),
    target area, and credited tier — the strategy's decision as the real loop
    saw it, not a parallel reconstruction.
    """

    def __init__(self) -> None:
        super().__init__()
        self.events: list[dict] = []

    def emit(self, event: str, **payload) -> None:
        self.events.append({"event": event, **payload})


def _mode(settings: Settings) -> str:
    llm = get_llm_client(settings)
    if llm is None:
        return "mock"
    return f"live:{settings.gemini_model if settings.provider == 'gemini' else settings.model}"


def _build_driver(scenario: Scenario, settings: Settings, log) -> InterviewDriver:
    """A driver positioned at the scenario's prefix, via the REAL resume path."""
    transcript = Transcript()
    history: list[dict] = []
    pending: str | None = None
    interviewer_segments = 0
    for seg in scenario.prefix:
        speaker = (Speaker.INTERVIEWER if seg["role"] == "interviewer"
                   else Speaker.SUBJECT)
        transcript.append(speaker, seg["text"])
        if speaker is Speaker.INTERVIEWER:
            history.append({"role": "assistant", "content": seg["text"]})
            pending = seg["text"]
            interviewer_segments += 1
        else:
            history.append({"role": "user", "content": seg["text"]})

    driver = InterviewDriver.resume(
        engine=InterviewEngine(llm=get_llm_client(settings),
                               max_turns=settings.max_turns),
        transcript=transcript,
        objective="lab scenario",
        pending_question=scenario.pending_question or pending,
        turn_count=(scenario.turn_count
                    if scenario.turn_count is not None else interviewer_segments),
        event_log=log,
        max_turns=settings.max_turns,
    )
    return driver


def _mk_result(spec, score: float, evidence: str) -> CriterionResult:
    return CriterionResult(
        rubric_id=spec.id, dimension=spec.dimension,
        grader_class=spec.grader_class, score=round(score, 4),
        status="pass" if score >= 1.0 else ("fail" if score <= 0.0 else "partial"),
        evidence=evidence)


def _mk_unscored(spec, reason: str) -> CriterionResult:
    return CriterionResult(rubric_id=spec.id, dimension=spec.dimension,
                           grader_class=spec.grader_class, score=None,
                           status="unscored", evidence=reason)


def _evaluate(scenario: Scenario, settings: Settings, utterance: str,
              log: _CapturingLog, latency_ms: float, error: str | None, *,
              state=None, report_md: str | None = None,
              repeat_utterances: list[str] | None = None,
              closed: bool = False) -> TurnEvaluation:
    last_asked = next((e for e in reversed(log.events)
                       if e.get("event") == "InterviewerAsked"), None)
    move_like = None
    if last_asked is not None:
        move_like = type("MoveView", (), {})()
        move_like.target_area = last_asked.get("target_area")
        intent_view = type("IntentView", (), {})()
        intent_view.value = last_asked.get("technique")
        move_like.intent = intent_view
        move_like.rationale = "recorded by the production loop"

    results = []
    for criterion in scenario.criteria:
        spec = get_rubric(criterion.rubric_id)
        ctx = TurnContext(scenario=scenario, utterance=utterance, state=state,
                          move=move_like, transcript=None,
                          repeat_utterances=repeat_utterances or [],
                          report_markdown=report_md, closed=closed)
        try:
            score, evidence = spec.fn(ctx, criterion.params)
            results.append(_mk_result(spec, score, evidence))
        except Unscored as exc:
            results.append(_mk_unscored(spec, exc.reason))
        except Exception as exc:
            results.append(_mk_result(
                spec, 0.0, f"grader error: {type(exc).__name__}: {exc}"))
    scored = [r.score for r in results if r.score is not None]
    total = (sum(scored) / len(scored)) if scored else None
    return TurnEvaluation(
        scenario_id=scenario.id, suite_id="", rubric_version=RUBRIC_VERSION,
        mode=_mode(settings), produced_utterance=utterance, results=results,
        total_score=round(total, 4) if total is not None else None,
        latency_ms=round(latency_ms, 2),
        output_sha=hashlib.sha256(utterance.encode("utf-8")).hexdigest()[:16],
        error=error)


def run_turn_case(scenario: Scenario, settings: Settings,
                  *, repeats: int = 1) -> list[TurnEvaluation]:
    """Run a `turn` scenario `repeats` times; one evaluation per repeat."""
    evaluations: list[TurnEvaluation] = []
    utterances: list[str] = []
    for _ in range(max(1, repeats)):
        log = _CapturingLog()
        started = time.perf_counter()
        error: str | None = None
        utterance = ""
        state = None
        try:
            driver = _build_driver(scenario, settings, log)
            if driver.closed:
                raise RuntimeError("scenario driver is closed before the turn")
            if scenario.candidate_answer:
                driver.submit_answer(scenario.candidate_answer)
            utterance = driver.next_question() or ""
            state = driver.state
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        latency_ms = (time.perf_counter() - started) * 1000
        utterances.append(utterance)
        evaluations.append(_evaluate(scenario, settings, utterance, log,
                                     latency_ms, error, state=state,
                                     closed=bool(error is None and driver.closed),
                                     repeat_utterances=utterances))

    # Consistency is a property of the WHOLE repeat set: grade it once with
    # every repeat's output and apply the same verdict to all repeats.
    if repeats > 1 and any(c.rubric_id == "consistency/repeat"
                           for c in scenario.criteria):
        spec = get_rubric("consistency/repeat")
        params = next(c.params for c in scenario.criteria
                      if c.rubric_id == "consistency/repeat")
        for evaluation in evaluations:
            ctx = TurnContext(scenario=scenario,
                              utterance=evaluation.produced_utterance,
                              state=None, move=None, transcript=None,
                              repeat_utterances=utterances)
            try:
                score, evidence = spec.fn(ctx, params)
                for r in evaluation.results:
                    if r.rubric_id == "consistency/repeat":
                        r.score, r.status, r.evidence = (
                            round(score, 4),
                            "pass" if score >= 1.0 else "fail", evidence)
            except Unscored as exc:
                for r in evaluation.results:
                    if r.rubric_id == "consistency/repeat":
                        r.evidence = exc.reason
            # The total was computed before consistency was graded — recompute.
            scored = [r.score for r in evaluation.results if r.score is not None]
            evaluation.total_score = (round(sum(scored) / len(scored), 4)
                                      if scored else None)
    return evaluations


def run_gate_case(scenario: Scenario, settings: Settings) -> list[TurnEvaluation]:
    """A claim/quote pair through the two gates, against the expected verdict."""
    gate = scenario.gate or {}
    claim, quote = gate.get("claim", ""), gate.get("quote", "")
    expect = gate.get("expect", "supported")
    started = time.perf_counter()

    transcript = Transcript()
    transcript.append(Speaker.INTERVIEWER, "Tell me about it.")
    transcript.append(Speaker.SUBJECT, quote)
    claim_obj, reason = ground_proposal(
        RawProposal("observation", claim, quote=quote, tier=2), transcript)
    if claim_obj is None:
        verdict, evidence = "rejected", f"grounding rejected: {reason}"
    else:
        checker = HeuristicEntailmentChecker()
        result = checker.check(claim_obj.statement,
                               claim_obj.evidence[0].resolve(transcript))
        verdict = ("supported" if result.verdict is Entailment.SUPPORTED
                   else "rejected")
        evidence = f"entailment: {result.verdict.value} ({result.reason})"
    ok = verdict == expect
    latency_ms = (time.perf_counter() - started) * 1000
    evaluation = TurnEvaluation(
        scenario_id=scenario.id, suite_id="", rubric_version=RUBRIC_VERSION,
        mode=_mode(settings), produced_utterance=verdict, results=[],
        total_score=1.0 if ok else 0.0, latency_ms=round(latency_ms, 2),
        output_sha=hashlib.sha256(f"{claim}{quote}{verdict}".encode()).hexdigest()[:16])
    evaluation.results.append(_mk_result(
        get_rubric("correctness/state"), 1.0 if ok else 0.0,
        f"gate verdict {verdict!r} (expected {expect!r}): {evidence}"))
    return [evaluation]


def _render_employer_deliverable(tmp: Path) -> str:
    from ..aggregation.aggregator import aggregate
    from ..aggregation.model import participant_finding_from_claim
    from ..aggregation.relation import HeuristicRelationChecker
    from ..privacy import ReleasePolicy, release, render_release_report

    statements = [
        ("P-1", "The director's approval is the bottleneck — that slow decision "
                "holds everything up."),
        ("P-2", "Everything waits on the director's approval — that approval "
                "bottleneck stalls the work."),
        ("P-3", "The director's approval is the real bottleneck; that decision "
                "takes days."),
        ("P-4", "VIP customers get bumped up the queue when they ask."),
        ("P-5", "VIP customers get bumped up the queue when they ask."),
        ("P-6", "I sometimes skip the end-of-day reconciliation entirely."),
    ]
    findings = []
    for pid, text in statements:
        transcript = Transcript(engagement_id="eng-lab", tenant_id="tenant-lab")
        transcript.interview_id = pid
        transcript.append(Speaker.INTERVIEWER, "Tell me about it.")
        transcript.append(Speaker.SUBJECT, text)
        transcript.finalize()
        TranscriptStore(tmp, None).save(transcript)
        for claim in EvidenceTagger(llm=None).tag(transcript).claims:
            findings.append(participant_finding_from_claim(
                claim, transcript, participant_id=pid, participant_name=pid))
    aggregation = aggregate(findings, HeuristicRelationChecker())
    package = release(aggregation, policy=ReleasePolicy.for_employer())
    return render_release_report(package, org_name="Lab engagement",
                                 interview_count=3)


def _render_consultant_deliverable(tmp: Path) -> str:
    from ..persistence.ledger import read_verdicts
    from ..report.generator import render_markdown_report
    from ..validation.model import (ValidatedFinding, ValidationDecision,
                                    Validator, Verdict)

    store = TranscriptStore(tmp, None)
    transcript = store.load(_find_txn(tmp, "P-1"))  # the validated participant
    tagging = EvidenceTagger(llm=None).tag(transcript)
    verdicts = read_verdicts(tmp, transcript.id, None)
    findings: list[ValidatedFinding] = []
    for claim in tagging.claims:
        recorded = verdicts.get(claim.id)
        if recorded is None:
            continue  # unvalidated statements must not reach any report
        findings.append(ValidatedFinding(
            claim=claim,
            decision=ValidationDecision(
                id=f"val-{claim.id}", claim_id=claim.id,
                verdict=Verdict(recorded.verdict),
                validator=Validator(id="val-auto", display_name="Auto-Sim",
                                    kind="auto-sim"),
                reviewed_evidence=tuple(e.ref for e in claim.evidence),
                reason=recorded.reason or "recorded")))
    return render_markdown_report(
        transcript=transcript, findings=findings, objective="lab scenario",
        engagement_id="eng-lab", interview_id=transcript.id,
        validator_kind="consultant", validator_name="Consultant",
        grounding_summary={"proposed": len(tagging.claims),
                           "grounded": tagging.report.grounded,
                           "unsourced": tagging.report.ungrounded,
                           "unsupported": len(tagging.entailment_rejected),
                           "confabulation": tagging.report.confabulation_rate})


def _stable_output_sha(text: str) -> str:
    """Hash the STABLE content of a produced output.

    Report markdown embeds random transcript ids and a generation date — those
    are volatiles, not behavior. Normalizing them lets the mock-mode
    regression compare detect real rewordings without tripping on identifiers.
    """
    import re as _re

    stable = _re.sub(r"txn-[0-9a-f]+", "txn", text)
    stable = _re.sub(r"seg-[0-9a-f]+", "seg", stable)
    stable = _re.sub(r"clm-[0-9a-f]+", "clm", stable)
    stable = _re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", stable)
    stable = _re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", "<ts>", stable)
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]


def run_report_case(scenario: Scenario, settings: Settings) -> list[TurnEvaluation]:
    """Render a real deliverable in a temp workspace and grade its content."""
    started = time.perf_counter()
    kind = "employer"
    if any("provenance" in tag or "consultant" in tag for tag in scenario.tags):
        kind = "consultant"
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    statements = [
        ("P-1", "The director's approval is the bottleneck — that slow decision "
                "holds everything up."),
        ("P-2", "Everything waits on the director's approval — that approval "
                "bottleneck stalls the work."),
        ("P-3", "The director's approval is the real bottleneck; that decision "
                "takes days."),
        ("P-4", "VIP customers get bumped up the queue when they ask."),
        ("P-6", "I sometimes skip the end-of-day reconciliation entirely."),
    ]
    for pid, text in statements:
        transcript = Transcript(engagement_id="eng-lab", tenant_id="tenant-lab")
        transcript.interview_id = pid
        transcript.append(Speaker.INTERVIEWER, "Tell me about it.")
        transcript.append(Speaker.SUBJECT, text)
        transcript.finalize()
        TranscriptStore(tmp, None).save(transcript)
        claims = EvidenceTagger(llm=None).tag(transcript).claims
        if kind == "employer" or pid == "P-1":
            # Validate every claim for P-1 (consultant report needs verdicts in
            # the LEDGER — that is where the report reads them back from) and
            # none elsewhere (the employer release ignores validation anyway).
            gate = ValidationGate(
                AutoValidator.VALIDATOR,
                EventLog(tmp, transcript.id, layer="validation", cipher=None))
            from ..validation.model import Verdict

            for claim in claims:
                gate.decide(claim, Verdict.ACCEPTED, "lab scenario")

    if kind == "employer":
        from ..aggregation.aggregator import aggregate
        from ..aggregation.model import participant_finding_from_claim
        from ..aggregation.relation import HeuristicRelationChecker
        from ..privacy import ReleasePolicy, release, render_release_report

        findings = []
        for pid, text in statements:
            transcript = TranscriptStore(tmp, None).load(_find_txn(tmp, pid))
            for claim in EvidenceTagger(llm=None).tag(transcript).claims:
                findings.append(participant_finding_from_claim(
                    claim, transcript, participant_id=pid, participant_name=pid))
        package = release(aggregate(findings, HeuristicRelationChecker()),
                          policy=ReleasePolicy.for_employer())
        md = render_release_report(package, org_name="Lab engagement",
                                   interview_count=3)
    else:
        md = _render_consultant_deliverable(tmp)

    latency_ms = (time.perf_counter() - started) * 1000
    evaluation = _evaluate(scenario, settings, md, _CapturingLog(), latency_ms,
                           None, report_md=md)
    # Reports embed volatile identifiers (fresh workspace = fresh txn/seg/clm
    # ids and a new date); hash the STABLE content so the regression compare
    # detects real rewordings, not new random ids.
    evaluation.output_sha = _stable_output_sha(md)
    return [evaluation]


def _find_txn(tmp: Path, pid: str) -> str:
    store = TranscriptStore(tmp, None)
    for tid in store.list_ids():
        transcript = store.load(tid)
        if transcript is not None and transcript.interview_id == pid:
            return tid
    raise KeyError(f"no transcript for {pid}")


def run_full_case(scenario: Scenario, settings: Settings) -> list[TurnEvaluation]:
    """A whole conversation against the scenario's persona."""
    started = time.perf_counter()
    spec = scenario.persona or {}
    persona = Persona(
        name=spec.get("name", "Lab"), role=spec.get("role", "Coordinator"),
        candor=spec.get("candor", "open"), background=spec.get("background", ""),
        latent_truths=[LatentTruth(**t) for t in spec.get("truths", [])])
    llm = get_llm_client(settings)
    engine = InterviewEngine(llm=llm, max_turns=settings.max_turns)
    subject = SimulatedInterviewee(persona, llm=llm)
    result = run_interview(engine=engine, subject=subject,
                           event_log=NullEventLog(),
                           max_turns=settings.max_turns)
    latency_ms = (time.perf_counter() - started) * 1000
    return [_evaluate(scenario, settings, "", _CapturingLog(), latency_ms, None,
                      state=result.state)]


def run_suite(scenarios: list[Scenario], settings: Settings, *,
              suite_id: str = "lab", repeats: int = 1) -> SuiteResult:
    """Run every scenario in the dataset; collect evaluations and variance."""
    result = SuiteResult(suite_id=suite_id, mode=_mode(settings))
    by_scenario: dict[str, list[TurnEvaluation]] = {}
    for scenario in scenarios:
        if scenario.unit == "turn":
            runs = run_turn_case(scenario, settings, repeats=max(1, repeats))
        elif scenario.unit == "gate":
            runs = run_gate_case(scenario, settings)
        elif scenario.unit == "report":
            runs = run_report_case(scenario, settings)
        elif scenario.unit == "full":
            runs = run_full_case(scenario, settings)
        else:
            raise ValueError(f"scenario {scenario.id!r}: unknown unit "
                             f"{scenario.unit!r}")
        result.evaluations.extend(runs)
        by_scenario[scenario.id] = runs

    for scenario in scenarios:
        runs = by_scenario[scenario.id]
        scores = [e.total_score for e in runs if e.total_score is not None]
        latencies = [e.latency_ms for e in runs]
        result.variance.append(ScenarioVariance(
            scenario_id=scenario.id, runs=len(runs),
            distinct_outputs=len({e.output_sha for e in runs}),
            failures=sum(1 for e in runs if e.error),
            score_min=min(scores) if scores else None,
            score_max=max(scores) if scores else None,
            latency_ms_mean=round(statistics.fmean(latencies), 2),
            latency_ms_stddev=round(statistics.pstdev(latencies), 2)
            if len(latencies) > 1 else 0.0))
    return result
