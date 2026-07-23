"""Run cases through the real pipeline and score them.

The harness evaluates the pipeline up to the *proposal* layer (interview → tag),
not post-validation: human validation is a non-automatable gate, so baking a
simulated reviewer into the metrics would conflate the AI's synthesis with a fake
consultant. We score the grounded claim proposals directly.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..evidence.tagger import EvidenceTagger
from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..llm.client import LLMClient
from ..persistence.event_log import NullEventLog
from ..subjects.simulated import SimulatedInterviewee
from .dataset import Case, default_suite
from .gates import GateResult, case_passed, evaluate_gates
from .metrics import CaseMetrics, score_case


@dataclass
class CaseResult:
    metrics: CaseMetrics
    gates: list[GateResult]

    @property
    def passed(self) -> bool:
        return case_passed(self.gates)


@dataclass
class SuiteResult:
    cases: list[CaseResult]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.cases)


def run_case(case: Case, *, llm: LLMClient | None = None) -> CaseResult:
    persona = case.persona()
    gold = list(persona.latent_truths)

    engine = InterviewEngine(llm=llm, max_turns=case.max_turns)
    subject = SimulatedInterviewee(persona, llm=llm)
    result = run_interview(
        engine=engine, subject=subject, event_log=NullEventLog(), max_turns=case.max_turns
    )

    tagging = EvidenceTagger(llm=llm).tag(result.transcript)
    metrics = score_case(
        persona=case.name.split("/")[0],
        candor=case.candor,
        is_ceiling=case.is_ceiling,
        gold=gold,
        transcript=result.transcript,
        claims=tagging.claims,
        confabulation_rate=tagging.report.confabulation_rate,
    )
    return CaseResult(metrics=metrics, gates=evaluate_gates(metrics))


def run_suite(cases: list[Case] | None = None, *, llm: LLMClient | None = None) -> SuiteResult:
    cases = cases or default_suite()
    return SuiteResult(cases=[run_case(c, llm=llm) for c in cases])
