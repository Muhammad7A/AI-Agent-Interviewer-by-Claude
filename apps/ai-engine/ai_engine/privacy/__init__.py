"""The privacy firewall — Constitution Article X, in code rather than in prose.

Until now this was documented and unimplemented: the org report attributed Tier-3
criticism to named employees. That is the anonymity paradox (F3) shipping as a
feature, and it attacks the one structural moat the moat analysis identified —
being the party an employee can safely tell the truth to.

The firewall rests on one distinction the system previously did not make: **there
are two audiences with different rights.**

  * The **consultant** is a neutral third party under NDA. They may see attributed,
    verbatim testimony — that is the entire point of the arrangement.
  * The **employer** may see aggregated findings only: above a k-anonymity
    threshold, never attributed for sensitive tiers, and — the subtle part —
    **without verbatim quotes**, because a verbatim quote is a fingerprint. "I use
    my personal ChatGPT to draft the summaries" identifies its author to their own
    manager just as surely as a name does.

Nothing reaches an employer except through :func:`release`, and what it withholds is
recorded in a suppression ledger so the redaction is auditable.
"""

from .identity import Pseudonymizer
from .policy import Audience, ReleasePolicy
from .release import (
    ReleasePackage,
    ReleasedStatement,
    ReleasedTopic,
    Suppression,
    release,
)
from .report import render_release_report

__all__ = [
    "Audience",
    "Pseudonymizer",
    "ReleasePackage",
    "ReleasePolicy",
    "ReleasedStatement",
    "ReleasedTopic",
    "Suppression",
    "release",
    "render_release_report",
]
