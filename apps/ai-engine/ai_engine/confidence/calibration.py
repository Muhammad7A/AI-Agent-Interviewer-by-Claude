"""Measuring whether confidence means anything.

A derived confidence number is worthless until it is validated against outcomes.
Two *different* properties matter, and a scorer can have one without the other:

  * **Calibration** — does 0.8 confidence mean right ~80% of the time?
    Measured by reliability bins and **ECE** (expected calibration error).
  * **Discrimination** — does it rank true findings above false ones?
    Measured by **AUC**. A scorer can be perfectly ranked yet badly calibrated
    (all values squashed), or well calibrated on average yet unable to separate
    anything (predicting the base rate for everything).

**Brier score** combines both (lower is better) and is the honest single number.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScoredOutcome:
    """One prediction paired with what turned out to be true."""

    label: str
    confidence: float
    correct: bool


@dataclass(frozen=True)
class ReliabilityBin:
    lower: float
    upper: float
    n: int
    mean_confidence: float
    accuracy: float

    @property
    def gap(self) -> float:
        return abs(self.accuracy - self.mean_confidence)


@dataclass
class CalibrationReport:
    n: int
    n_correct: int
    base_rate: float
    ece: float
    brier: float
    auc: float | None            # None when only one class is present
    mean_conf_correct: float | None
    mean_conf_incorrect: float | None
    bins: list[ReliabilityBin] = field(default_factory=list)

    @property
    def discriminates(self) -> bool:
        """Does confidence separate true from false at all?"""
        return self.auc is not None and self.auc > 0.5

    @property
    def separation(self) -> float | None:
        if self.mean_conf_correct is None or self.mean_conf_incorrect is None:
            return None
        return self.mean_conf_correct - self.mean_conf_incorrect


def _auc(outcomes: list[ScoredOutcome]) -> float | None:
    """Mann-Whitney AUC: probability a random true outranks a random false."""
    pos = [o.confidence for o in outcomes if o.correct]
    neg = [o.confidence for o in outcomes if not o.correct]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for q in neg:
            if p > q:
                wins += 1.0
            elif p == q:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def calibrate(outcomes: list[ScoredOutcome], *, bin_count: int = 5) -> CalibrationReport:
    n = len(outcomes)
    if n == 0:
        return CalibrationReport(0, 0, 0.0, 0.0, 0.0, None, None, None, [])

    n_correct = sum(1 for o in outcomes if o.correct)
    brier = sum((o.confidence - (1.0 if o.correct else 0.0)) ** 2 for o in outcomes) / n

    bins: list[ReliabilityBin] = []
    ece = 0.0
    for b in range(bin_count):
        lower = b / bin_count
        upper = (b + 1) / bin_count
        # Last bin is closed on the right so confidence == 1.0 lands somewhere.
        members = [
            o for o in outcomes
            if (lower <= o.confidence < upper) or (b == bin_count - 1 and o.confidence == 1.0)
        ]
        if not members:
            continue
        mean_conf = sum(o.confidence for o in members) / len(members)
        accuracy = sum(1 for o in members if o.correct) / len(members)
        bins.append(ReliabilityBin(lower, upper, len(members), mean_conf, accuracy))
        ece += (len(members) / n) * abs(accuracy - mean_conf)

    correct_confs = [o.confidence for o in outcomes if o.correct]
    wrong_confs = [o.confidence for o in outcomes if not o.correct]
    return CalibrationReport(
        n=n,
        n_correct=n_correct,
        base_rate=n_correct / n,
        ece=ece,
        brier=brier,
        auc=_auc(outcomes),
        mean_conf_correct=(sum(correct_confs) / len(correct_confs)) if correct_confs else None,
        mean_conf_incorrect=(sum(wrong_confs) / len(wrong_confs)) if wrong_confs else None,
        bins=bins,
    )
