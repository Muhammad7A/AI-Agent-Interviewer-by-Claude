"""Run cases through the real pipeline and score them.

The harness evaluates the pipeline up to the *proposal* layer (interview → tag),
not post-validation: human validation is a non-automatable gate, so baking a
simulated reviewer into the metrics would conflate the AI's synthesis with a fake
consultant. We score the grounded claim proposals directly.

A live model is non-deterministic, so a single run means little. Each case can be
run ``repeats`` times; a case passes only if it passes on EVERY run (the strict,
honest reading of "gates, not averages"), and the report shows the spread.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..evidence.tagger import EvidenceTagger
from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..llm.client import LLMClient
from ..persistence.event_log import NullEventLog
from ..subjects.simulated import SimulatedInterviewee
from .dataset import Case, default_suite
from .gates import GateResult, case_passed, evaluate_gates
from .metrics import CaseMetrics, score_case

# A number pulled out of one CaseMetrics, e.g. ``lambda m: m.e2e_recall``.
MetricFn = Callable[[CaseMetrics], float]


@dataclass
class CaseResult:
    name: str
    persona: str
    candor: str
    is_ceiling: bool
    runs: list[CaseMetrics]
    gate_sets: list[list[GateResult]]

    @property
    def passed(self) -> bool:
        return all(case_passed(gs) for gs in self.gate_sets)

    def stat(self, fn: MetricFn) -> tuple[float, float, float]:
        """(min, mean, max) of a metric across the repeated runs."""
        vals = [fn(m) for m in self.runs]
        return min(vals), sum(vals) / len(vals), max(vals)

    def failing_gates(self) -> list[GateResult]:
        seen: dict[str, GateResult] = {}
        for gs in self.gate_sets:
            for g in gs:
                if not g.passed and g.name not in seen:
                    seen[g.name] = g
        return list(seen.values())


@dataclass
class SuiteResult:
    cases: list[CaseResult]
    repeats: int = 1

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.cases)


def _run_once(case: Case, llm: LLMClient | None) -> CaseMetrics:
    persona = case.persona()
    gold = list(persona.latent_truths)

    engine = InterviewEngine(llm=llm, max_turns=case.max_turns)
    subject = SimulatedInterviewee(persona, llm=llm)
    result = run_interview(
        engine=engine, subject=subject, event_log=NullEventLog(), max_turns=case.max_turns
    )
    tagging = EvidenceTagger(llm=llm).tag(result.transcript)
    return score_case(
        persona=case.name.split("/")[0],
        candor=case.candor,
        is_ceiling=case.is_ceiling,
        gold=gold,
        transcript=result.transcript,
        claims=tagging.claims,
        confabulation_rate=tagging.confabulation_rate,  # combined: grounding + entailment
    )


def run_case(case: Case, *, llm: LLMClient | None = None, repeats: int = 1) -> CaseResult:
    runs = [_run_once(case, llm) for _ in range(max(1, repeats))]
    gate_sets = [evaluate_gates(m) for m in runs]
    return CaseResult(
        name=case.name,
        persona=case.name.split("/")[0],
        candor=case.candor,
        is_ceiling=case.is_ceiling,
        runs=runs,
        gate_sets=gate_sets,
    )


def run_suite(
    cases: list[Case] | None = None, *, llm: LLMClient | None = None, repeats: int = 1
) -> SuiteResult:
    cases = cases or default_suite()
    return SuiteResult(
        cases=[run_case(c, llm=llm, repeats=repeats) for c in cases],
        repeats=repeats,
    )
