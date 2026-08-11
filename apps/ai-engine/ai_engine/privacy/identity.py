"""Pseudonymization at ingest.

A participant's real identity enters the pipeline once, at the boundary, and is
immediately replaced by a per-engagement pseudonym. Everything downstream — the
event logs, the aggregation, the confidence scores, the reports — carries only the
pseudonym, so the sensitive artifacts are not the same artifacts as the identity key.

Properties that matter:

  * **Deterministic within an engagement** — the same person is the same pseudonym
    across their whole interview and across aggregation, or corroboration counting
    would break.
  * **Not linkable across engagements** — a different engagement salt yields a
    different pseudonym for the same person, so two clients' data cannot be joined.
  * **Not reversible from the pseudonym** — HMAC-SHA256, so the mapping cannot be
    recovered without the salt. Re-identification requires the key, deliberately.

The key (pseudonym → real identity) is written separately and only for the
consultant. Losing it means losing the ability to re-identify, which is the intended
failure direction.
"""
from __future__ import annotations

import hmac
import json
import secrets
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

PSEUDONYM_PREFIX = "P-"
_PSEUDONYM_HEX = 6


def new_engagement_salt() -> str:
    """A fresh, high-entropy salt. One per engagement; store it with the key."""
    return secrets.token_hex(16)


@dataclass
class Pseudonymizer:
    """Maps real participant identities to per-engagement pseudonyms."""

    engagement_salt: str = field(default_factory=new_engagement_salt)
    _issued: dict[str, str] = field(default_factory=dict, repr=False)

    def pseudonym(self, participant_id: str) -> str:
        if participant_id not in self._issued:
            digest = hmac.new(
                self.engagement_salt.encode("utf-8"),
                participant_id.encode("utf-8"),
                sha256,
            ).hexdigest()
            self._issued[participant_id] = f"{PSEUDONYM_PREFIX}{digest[:_PSEUDONYM_HEX]}"
        return self._issued[participant_id]

    @property
    def key(self) -> dict[str, str]:
        """pseudonym -> real identity. Consultant-only; never leaves the firewall."""
        return {pseudo: real for real, pseudo in self._issued.items()}

    def write_key(self, path: Path) -> Path:
        """Write the re-identification key to its own restricted file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "warning": (
                "RESTRICTED — consultant only. This file re-identifies employees. "
                "It must never be shared with the employer or stored alongside "
                "employer-facing deliverables."
            ),
            "engagement_salt": self.engagement_salt,
            "key": self.key,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
