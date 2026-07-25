"""Confidence scoring and calibration.

Confidence is kept strictly separate from truth (C2): a finding's truth-value comes
from evidence and human validation; its *confidence* is a separate, explicitly
derived number with its own lifecycle. Per Constitution Art. III, confidence here
is derived ONLY from structural signals that are actually observable —

  * how many independent participants agree with this specific finding,
  * how many contradict it (and whether it sits in the majority or the minority),
  * the disclosure tier (a costly admission is less likely to be invented),
  * how exactly its evidence matched the immutable source,

— and NEVER from fluency, verbosity, or the model's own narration.

Every score is explainable: it decomposes into named signal contributions in
log-odds space, so "why do you believe this at 0.84?" always has an answer.

Crucially, a derived confidence is worthless until it is *measured*. The
``calibration`` module scores confidence against known ground truth (ECE, Brier,
AUC, reliability bins) so we can state whether an 0.8 finding is actually right
~80% of the time — the eval-backed source Art. III requires.
"""

from .model import ConfidenceBand, ConfidenceScore, SignalContribution
from .scorer import score_topic, score_all
from .calibration import (
    CalibrationReport,
    ReliabilityBin,
    ScoredOutcome,
    calibrate,
)

__all__ = [
    "CalibrationReport",
    "ConfidenceBand",
    "ConfidenceScore",
    "ReliabilityBin",
    "ScoredOutcome",
    "SignalContribution",
    "calibrate",
    "score_all",
    "score_topic",
]
