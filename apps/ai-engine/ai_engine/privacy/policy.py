"""Who may see what.

The policy is data, not scattered conditionals, so the guarantee offered to
employees can be stated, versioned, printed on the consent form, and tested.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

POLICY_VERSION = "release-policy/v1"


class Audience(Enum):
    #: Neutral third party under NDA. Sees attributed, verbatim testimony — that is
    #: what makes them useful, and what the employee was promised.
    CONSULTANT = "consultant"
    #: The employer. Aggregated findings only. Never raw testimony.
    EMPLOYER = "employer"


@dataclass(frozen=True)
class ReleasePolicy:
    audience: Audience

    #: Minimum distinct participants before a topic may be released at all.
    k_anonymity: int = 3

    #: Verbatim quotes are released only up to this tier. A quote is a fingerprint:
    #: specific detail and writing style identify the author to their own manager
    #: even with the name removed, so sensitive tiers are summarised, never quoted.
    verbatim_max_tier: int = 1

    #: Attribution (even pseudonymous) only up to this tier. Above it, a finding is
    #: released as the group's, not as a person's — otherwise a pseudonym plus a few
    #: attributed findings becomes a profile.
    attribute_max_tier: int = 1

    #: Whether a topic below the k-anonymity threshold is withheld.
    suppress_below_k: bool = True

    #: Whether the sides of a disagreement may be shown. Naming who dissents is the
    #: most dangerous single disclosure in the product.
    reveal_contradiction_sides: bool = False

    #: Whether per-participant confidence may be shown (it reveals the split).
    reveal_per_member_confidence: bool = False

    #: Release the topic as a single aggregate item, with no per-participant
    #: breakdown at all. This is what "aggregated findings only" actually requires:
    #: a per-member statement is per-person disclosure even with the name and the
    #: quote marks removed, because the synthesised statement carries the same words.
    aggregate_only: bool = True

    @classmethod
    def for_consultant(cls) -> "ReleasePolicy":
        """Unredacted. The consultant is inside the firewall, not outside it.

        Even here the artifact is pseudonymous: re-identification requires the
        separately-stored key, so a mislaid report is not a mislaid roster.
        """
        return cls(
            audience=Audience.CONSULTANT,
            k_anonymity=1,
            verbatim_max_tier=4,
            attribute_max_tier=4,
            suppress_below_k=False,
            reveal_contradiction_sides=True,
            reveal_per_member_confidence=True,
            aggregate_only=False,
        )

    @classmethod
    def for_employer(cls, *, k_anonymity: int = 3) -> "ReleasePolicy":
        """The default employer guarantee. Deliberately strict."""
        return cls(
            audience=Audience.EMPLOYER,
            k_anonymity=k_anonymity,
            verbatim_max_tier=1,
            attribute_max_tier=1,
            suppress_below_k=True,
            reveal_contradiction_sides=False,
            reveal_per_member_confidence=False,
            aggregate_only=True,
        )

    def summary(self) -> str:
        if self.audience is Audience.CONSULTANT:
            return ("Consultant view — inside the confidentiality firewall. "
                    "Pseudonymous; re-identification requires the separately held key.")
        return (f"Employer view — aggregated findings only. Each topic is reported at "
                f"the group level and requires at least {self.k_anonymity} independent "
                f"participants. No individual response, verbatim quote, or attribution "
                f"is released, and the sides of a disagreement are never identified.")
