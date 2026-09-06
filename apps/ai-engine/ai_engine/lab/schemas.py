"""Schemas for the evaluation laboratory.

Everything the lab produces or consumes is a plain dataclass with an explicit
JSON round-trip, versioned by schema string — the same discipline the
persistence stores use. No implicit shapes: a dataset file or a stored result
that does not match its schema is refused, not guessed at.

The lab measures THREE grader classes, and every rubric criterion declares
which one it uses — the distinction is the anti-fake-confidence rule:

  * ``deterministic`` — computed from the system's own structures (state,
    strategy decisions, gates, report content). Same input, same verdict,
    forever. These are proofs, not opinions.
  * ``heuristic`` — a computed approximation that could disagree with a
    human (keyword overlap, length bands, leak patterns). Useful signal;
    never presented as ground truth.
  * ``model`` — requires a live model to judge. Declared in the rubric,
    reported as UNSCORED whenever no live provider is configured. A missing
    model never produces a invented score.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

LAB_SCHEMA = "groundwork.lab/v1"

#: Grader classes, in decreasing order of evidentiary weight.
DETERMINISTIC = "deterministic"
HEURISTIC = "heuristic"
MODEL = "model"
_GRADER_CLASSES = (DETERMINISTIC, HEURISTIC, MODEL)

#: Rubric dimensions. Each maps onto an artifact this system actually
#: produces — an interviewer turn, a claim, a report — never an abstraction.
DIMENSIONS = (
    "relevance",          # does the turn address the current interview target
    "correctness",        # does the recorded state match the expected transitions
    "reasoning",          # does the strategy choose the intent the state demands
    "communication",      # is the utterance clean, sized, leak-free
    "consistency",        # does the behavior repeat identically across repeats
    "interview_quality",  # does the full conversation elicit what the persona holds
    "feedback_quality",   # does the report carry provenance and stay inside the firewall
)


@dataclass
class CriterionExpectation:
    """One expected criterion inside a scenario: rubric id + how to judge it."""

    rubric_id: str
    #: Grader-specific parameters (e.g. {"expected_intent": "DE_ESCALATE"}).
    params: dict = field(default_factory=dict)


@dataclass
class Scenario:
    """One measurable situation: a prefix, an answer, and what should happen."""

    id: str
    title: str
    kind: str                     # golden | standard | edge | adversarial
    dimension: str                # primary rubric dimension under test
    #: What the runner executes: `turn` (one interviewer turn over a prefix),
    #: `full` (whole conversation vs a persona), `gate` (evidence-gate case:
    #: claim/quote/expected verdict), `report` (render + firewalled document).
    unit: str = "turn"
    #: Prior conversation as (speaker, text) pairs — "interviewer"/"subject".
    prefix: list = field(default_factory=list)  # list[dict] {"role": ..., "text": ...}
    pending_question: str | None = None  # the question awaiting the candidate answer
    candidate_answer: str = ""            # the participant's reply under evaluation
    #: Override the replayed turn count (close-by-budget scenarios).
    turn_count: int | None = None
    criteria: list = field(default_factory=list)  # list[CriterionExpectation]
    tags: list[str] = field(default_factory=list)
    #: For full-conversation scenarios: the persona's disclosures (truth specs).
    persona: dict | None = None   # {name, role, background, candor, truths: [...]}
    #: For `gate` scenarios: the claim/quote pair and the expected verdict.
    gate: dict | None = None      # {"claim": ..., "quote": ..., "expect": "supported"|"rejected"}

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "kind": self.kind,
            "dimension": self.dimension, "unit": self.unit,
            "prefix": self.prefix,
            "pending_question": self.pending_question,
            "candidate_answer": self.candidate_answer,
            "turn_count": self.turn_count,
            "criteria": [{"rubric_id": c.rubric_id, "params": c.params}
                         for c in self.criteria],
            "tags": self.tags, "persona": self.persona, "gate": self.gate,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scenario":
        unknown = set(data) - {"id", "title", "kind", "dimension", "unit",
                               "prefix", "pending_question", "candidate_answer",
                               "turn_count", "criteria", "tags", "persona",
                               "gate"}
        if unknown:
            raise ValueError(f"scenario {data.get('id')!r} has unknown fields: "
                             f"{sorted(unknown)}")
        return cls(
            id=data["id"], title=data["title"], kind=data["kind"],
            dimension=data["dimension"], unit=data.get("unit", "turn"),
            prefix=data.get("prefix", []),
            pending_question=data.get("pending_question"),
            candidate_answer=data.get("candidate_answer", ""),
            criteria=[CriterionExpectation(**c) for c in data["criteria"]],
            tags=list(data.get("tags", [])),
            persona=data.get("persona"),
            gate=data.get("gate"),
            turn_count=data.get("turn_count"),
        )


@dataclass
class CriterionResult:
    rubric_id: str
    dimension: str
    grader_class: str             # deterministic | heuristic | model
    score: float | None           # 0.0..1.0, or None when UNSCORED
    status: str                   # pass | fail | unscored
    evidence: str                 # what was observed — never a bare number


@dataclass
class TurnEvaluation:
    """The structured evaluation of one scenario run."""

    scenario_id: str
    suite_id: str
    rubric_version: str
    mode: str                     # mock | live:<model>
    produced_utterance: str
    results: list[CriterionResult]
    total_score: float | None     # mean of scored criteria; None if all unscored
    latency_ms: float
    output_sha: str               # hash of the produced utterance — variance input
    error: str | None = None      # engine/model failure during the run

    def to_dict(self) -> dict:
        return {
            "schema": LAB_SCHEMA, "scenario_id": self.scenario_id,
            "suite_id": self.suite_id, "rubric_version": self.rubric_version,
            "mode": self.mode, "produced_utterance": self.produced_utterance,
            "results": [
                {"rubric_id": r.rubric_id, "dimension": r.dimension,
                 "grader_class": r.grader_class, "score": r.score,
                 "status": r.status, "evidence": r.evidence}
                for r in self.results],
            "total_score": self.total_score, "latency_ms": self.latency_ms,
            "output_sha": self.output_sha, "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TurnEvaluation":
        if data.get("schema") != LAB_SCHEMA:
            raise ValueError(f"unsupported lab result schema: {data.get('schema')!r}")
        return cls(
            scenario_id=data["scenario_id"], suite_id=data["suite_id"],
            rubric_version=data["rubric_version"], mode=data["mode"],
            produced_utterance=data["produced_utterance"],
            results=[CriterionResult(**r) for r in data["results"]],
            total_score=data["total_score"], latency_ms=data["latency_ms"],
            output_sha=data["output_sha"], error=data.get("error"),
        )


def write_results(evaluations: list[TurnEvaluation], path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": LAB_SCHEMA,
               "evaluations": [e.to_dict() for e in evaluations]}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    return path


def load_results(path: Path) -> list[TurnEvaluation]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != LAB_SCHEMA:
        raise ValueError(f"unsupported lab result schema: {data.get('schema')!r}")
    return [TurnEvaluation.from_dict(e) for e in data["evaluations"]]
