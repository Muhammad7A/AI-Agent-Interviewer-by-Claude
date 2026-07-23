"""The evaluation harness — the system's conscience (Constitution Art. VIII).

Measures the pipeline against *known ground truth*: the simulated personas hold a
fixed set of tier-tagged latent truths, so we can score what fraction of the
achievable truth the pipeline recovers and whether it fabricates anything.

Two layers, evaluated separately (they fail independently):
  * Elicitation — did the interview get the truth OUT of the person into the
    transcript? (recall vs the candor-achievable set)
  * Synthesis — did tagging turn transcript truth into correct, grounded claims?
    (precision, confabulation, value density)

Gates, not averages: safety gates (no fabrication) must hold on every case;
capability gates (recovery, value) are judged at the candor ceiling. Calibration
is deliberately NOT scored — there is no confidence signal yet (C2), and faking
one would be the exact sin the harness exists to catch.
"""

from .dataset import Case, default_suite
from .metrics import CaseMetrics, score_case
from .runner import CaseResult, SuiteResult, run_case, run_suite

__all__ = [
    "Case",
    "CaseMetrics",
    "CaseResult",
    "SuiteResult",
    "default_suite",
    "run_case",
    "run_suite",
    "score_case",
]
