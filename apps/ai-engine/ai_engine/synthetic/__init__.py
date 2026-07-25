"""Synthetic organization generator — the testbed (research program Q16).

Hand-written personas prove a pipeline *runs*. They cannot make an evaluation
*statistically meaningful*: six people and eighteen findings is an anecdote, and a
fixture hand-tuned until it passes measures the fixture, not the system.

This generator produces organizations to order — controllable size, candor
distribution, corroboration depth, planted contradictions, and bias — with ground
truth known by construction and full reproducibility from a seed.

The design decision that makes it a real benchmark rather than a rubber stamp:
``minority_correct_rate``. In some planted contradictions the **majority is
wrong**. A confidence scorer that merely counts votes therefore *cannot* achieve a
perfect AUC on a generated org. If it did, the benchmark would be measuring
agreement, not truth.
"""

from .generator import generate_org
from .model import OrgSpec, SyntheticOrg
from .topics import TOPIC_TEMPLATES, TopicTemplate

__all__ = [
    "OrgSpec",
    "SyntheticOrg",
    "TOPIC_TEMPLATES",
    "TopicTemplate",
    "generate_org",
]
