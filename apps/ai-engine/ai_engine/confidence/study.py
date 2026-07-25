"""The calibration study: does derived confidence actually predict truth?

Runs the full real pipeline over a study organization (interview → tag → verify →
aggregate → score), labels every finding against the org's known ground truth, and
measures calibration and discrimination.

**An important honesty note about mock mode.** The proportion of false findings in
the study org is a *design choice*, not a measurement of reality. That means:

  * **AUC / discrimination is meaningful** — it is base-rate independent, so
    "does confidence rank true findings above false ones?" is a real answer.
  * **ECE is NOT a verdict on the scorer** — it is dominated by the invented base
    rate. Tuning the weights to minimise mock ECE would be fitting to a fiction.

So we report ECE, and we refuse to tune against it. Real calibration requires real
outcomes (research program Q4).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from ..aggregation.aggregator import aggregate
from ..aggregation.model import AggregatedFinding, participant_finding_from_claim
from ..aggregation.relation import make_relation_checker
from ..eval.matching import MATCH_THRESHOLD, match_score
from ..evidence.tagger import EvidenceTagger
from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..llm.client import LLMClient
from ..persistence.event_log import NullEventLog
from ..subjects.simulated import LatentTruth, Persona, SimulatedInterviewee
from .calibration import CalibrationReport, ScoredOutcome, calibrate
from .model import ConfidenceScore
from .scenario import gold_truths, is_veridical, meridian_org
from .scorer import score_topic


@dataclass
class StudyOrg:
    """An organization to study: its people, its ground truth, and a label.

    Adapting both the hand-written scenario and a generated org to one shape keeps
    the study logic identical for each — the only difference is where the personas
    and the veridicality key come from.
    """

    label: str
    personas: list[Persona]
    gold: list[LatentTruth]
    is_veridical: Callable[[str], bool]
    detail: str = ""


def meridian_study_org(candor: str = "open") -> StudyOrg:
    personas = meridian_org(candor)
    return StudyOrg(
        label="Meridian (hand-written)",
        personas=personas,
        gold=gold_truths(personas),
        is_veridical=is_veridical,
        detail=f"{len(personas)} employees, candor={candor}",
    )


def synthetic_study_org(spec) -> StudyOrg:
    """Adapt a generated organization (research program Q16 infrastructure)."""
    from ..synthetic import generate_org

    org = generate_org(spec)
    minority_correct = sum(1 for c in org.contradictions if c.minority_is_correct)
    return StudyOrg(
        label=f"{spec.name} (generated, seed={spec.seed})",
        personas=org.fresh_personas(),
        gold=org.gold_truths(),
        is_veridical=org.is_veridical,
        detail=(
            f"{len(org.personas)} employees · candor {org.candor_counts()} · "
            f"{org.total_truths} planted beliefs ({org.total_mistaken} false) · "
            f"{len(org.contradictions)} contradictions "
            f"({minority_correct} where the minority is right) · "
            f"{len(org.bias_holders)} unfounded attributions"
        ),
    )


@dataclass
class StudyRow:
    participant: str
    statement: str
    confidence: ConfidenceScore
    correct: bool
    matched_truth_id: str | None
    topic_id: str
    corroboration: int
    contested: bool


@dataclass
class StudyResult:
    rows: list[StudyRow]
    calibration: CalibrationReport
    topics: list[AggregatedFinding]
    interview_count: int
    org_label: str = ""
    org_detail: str = ""


def _best_match(text: str, gold: list[LatentTruth]) -> LatentTruth | None:
    best, best_score = None, 0
    for truth in gold:
        score = match_score(text, truth)
        if score > best_score:
            best, best_score = truth, score
    return best if best_score >= MATCH_THRESHOLD else None


def run_study(
    *,
    org: StudyOrg | None = None,
    llm: LLMClient | None = None,
    candor: str = "open",
    max_turns: int = 14,
) -> StudyResult:
    org = org or meridian_study_org(candor)
    personas: list[Persona] = org.personas
    gold = org.gold

    # 1. Interview everyone and tag their findings (the real pipeline).
    participant_findings = []
    for persona in personas:
        engine = InterviewEngine(llm=llm, max_turns=max_turns)
        subject = SimulatedInterviewee(persona, llm=llm)
        result = run_interview(
            engine=engine, subject=subject, event_log=NullEventLog(), max_turns=max_turns
        )
        for claim in EvidenceTagger(llm=llm).tag(result.transcript).claims:
            participant_findings.append(participant_finding_from_claim(
                claim, result.transcript,
                participant_id=persona.name, participant_name=persona.name,
            ))

    # 2. Aggregate across interviews, then score each member's confidence.
    aggregation = aggregate(participant_findings, make_relation_checker(llm))

    rows: list[StudyRow] = []
    for topic in aggregation.findings:
        scores = score_topic(topic)
        for i, (member, score) in enumerate(zip(topic.members, scores)):
            matched = _best_match(f"{member.statement} {member.evidence_quote}", gold)
            correct = matched is not None and org.is_veridical(matched.id)
            rows.append(StudyRow(
                participant=member.participant_name,
                statement=member.statement,
                confidence=score,
                correct=correct,
                matched_truth_id=matched.id if matched else None,
                topic_id=topic.topic_id,
                corroboration=1 + len({
                    topic.members[k].participant_id for k in topic.agreeing_with(i)
                } - {member.participant_id}),
                contested=bool(topic.conflicting_with(i)),
            ))

    outcomes = [
        ScoredOutcome(label=f"{r.participant}: {r.statement[:40]}",
                      confidence=r.confidence.value, correct=r.correct)
        for r in rows
    ]
    return StudyResult(
        rows=rows,
        calibration=calibrate(outcomes),
        topics=aggregation.findings,
        interview_count=len(personas),
        org_label=org.label,
        org_detail=org.detail,
    )


def render_study_report(study: StudyResult, *, mode: str) -> str:
    c = study.calibration
    lines: list[str] = []
    lines.append("# Confidence Calibration Study")
    lines.append("")
    lines.append(f"- **Mode:** {mode}")
    if study.org_label:
        lines.append(f"- **Organization:** {study.org_label}")
    if study.org_detail:
        lines.append(f"- **Composition:** {study.org_detail}")
    lines.append(f"- **Interviews:** {study.interview_count}   "
                 f"**Findings scored:** {c.n}   "
                 f"**Actually true:** {c.n_correct} (base rate {c.base_rate:.0%})")
    lines.append("")
    lines.append("## Does confidence mean anything?")
    lines.append("")
    auc = f"{c.auc:.2f}" if c.auc is not None else "n/a (one class only)"
    lines.append(f"- **Discrimination (AUC):** {auc} "
                 f"— probability a random true finding outranks a random false one. "
                 f"0.5 = useless, 1.0 = perfect. **Base-rate independent, so this is "
                 f"the meaningful number in mock mode.**")
    lines.append(f"- **Brier score:** {c.brier:.3f} (lower is better; combines "
                 f"calibration and discrimination)")
    lines.append(f"- **ECE:** {c.ece:.3f} — expected calibration error. "
                 f"**Not a verdict here:** the share of false findings in the study "
                 f"org is a design choice, so ECE reflects an invented base rate. "
                 f"We report it and refuse to tune against it; real calibration "
                 f"needs real outcomes.")
    if c.separation is not None:
        lines.append(f"- **Separation:** mean confidence {c.mean_conf_correct:.2f} on true "
                     f"findings vs {c.mean_conf_incorrect:.2f} on false "
                     f"(gap {c.separation:+.2f})")
    lines.append("")

    # A scorer that is worse than chance must say so loudly.
    if c.auc is not None and c.auc < 0.5:
        lines.append("> ### ⚠ Confidence is INVERTED on this organization")
        lines.append(">")
        lines.append("> AUC is below chance: the score ranks false findings *above* true "
                     "ones. This is the known failure mode of corroboration-weighted "
                     "confidence — independent agreement is only evidence when the "
                     "errors are independent. Where a **wrong majority** outvotes a "
                     "correct minority, or where a **shared misconception** corroborates "
                     "itself, the signal reverses. It is a documented limitation of the "
                     "scorer, reproducible on demand via `minority_correct_rate` and "
                     "`correlated_bias_rate`, not a defect in this run.")
        lines.append("")

    if c.bins:
        lines.append("## Reliability")
        lines.append("")
        lines.append("| confidence bin | n | mean conf | actual accuracy | gap |")
        lines.append("|---|---|---|---|---|")
        for b in c.bins:
            lines.append(f"| {b.lower:.1f}–{b.upper:.1f} | {b.n} | {b.mean_confidence:.2f} "
                         f"| {b.accuracy:.2f} | {b.gap:.2f} |")
        lines.append("")

    # Where confidence was wrong — the rows that matter most for diagnosis.
    misses = [r for r in study.rows if not r.correct]
    if misses:
        lines.append("## False findings, most confident first")
        lines.append("")
        lines.append("A false finding with high confidence is the dangerous case. "
                     "These are ranked so the worst is at the top.")
        lines.append("")
        lines.append("| conf | band | participant | corrob. | contested | finding |")
        lines.append("|---|---|---|---|---|---|")
        for r in sorted(misses, key=lambda r: r.confidence.value, reverse=True)[:15]:
            lines.append(
                f"| {r.confidence.value:.2f} | {r.confidence.band.value} | {r.participant} "
                f"| {r.corroboration} | {'yes' if r.contested else '—'} "
                f"| {r.statement[:56]} |"
            )
        lines.append("")

    lines.append("## Findings, most confident first")
    lines.append("")
    rows_sorted = sorted(study.rows, key=lambda r: r.confidence.value, reverse=True)
    shown = rows_sorted[:40]
    lines.append("| conf | band | true? | participant | corrob. | contested | finding |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in shown:
        lines.append(
            f"| {r.confidence.value:.2f} | {r.confidence.band.value} "
            f"| {'✓' if r.correct else '✗ FALSE'} | {r.participant} "
            f"| {r.corroboration} | {'yes' if r.contested else '—'} "
            f"| {r.statement[:58]} |"
        )
    if len(rows_sorted) > len(shown):
        lines.append(f"| … | | | | | | _{len(rows_sorted) - len(shown)} more_ |")
    lines.append("")

    # Show one full explanation so the score is never a black box.
    if study.rows:
        top = max(study.rows, key=lambda r: r.confidence.value)
        low = min(study.rows, key=lambda r: r.confidence.value)
        lines.append("## Why these numbers (explainability)")
        lines.append("")
        for label, row in (("Highest", top), ("Lowest", low)):
            lines.append(f"**{label} — {row.participant}: {row.statement[:60]}**")
            lines.append("")
            lines.append("```")
            lines.append(row.confidence.explain())
            lines.append("```")
            lines.append("")
    return "\n".join(lines)
