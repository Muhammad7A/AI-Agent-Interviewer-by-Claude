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
import os
import secrets
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path

PSEUDONYM_PREFIX = "P-"
#: Hex characters kept from the digest. Short enough to read aloud, long enough
#: that a birthday collision between participants is negligible for any real
#: engagement (at 6 chars, ~1% around 5,000 participants — and a collision
#: silently *merges* two people's testimony, corrupting corroboration and k).
_PSEUDONYM_HEX = 12


def new_engagement_salt() -> str:
    """A fresh, high-entropy salt. One per engagement; store it with the key."""
    return secrets.token_hex(16)


def restricted_dir(data_dir: Path | str) -> Path:
    """Where re-identification material lives — deliberately not beside deliverables.

    SECURITY.md's rule is that the key is never stored alongside employer-facing
    artifacts; one ``--write`` run emits both into ``data_dir``, so the key gets
    its own subdirectory and only ever shares a tree with them, never a directory.
    """
    return Path(data_dir) / "RESTRICTED"


def _write_restricted(path: Path, text: str) -> Path:
    """Write re-identification material, owner-only where the OS honors modes.

    POSIX: 0600. Windows ACLs are broader than a POSIX mode can express, so the
    stronger guarantee here is the *location* (see :func:`restricted_dir`) — but
    the mode is still set for every filesystem that honors it.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, text.encode("utf-8"))
    finally:
        os.close(fd)
    return path


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
        payload = {
            "warning": (
                "RESTRICTED — consultant only. This file re-identifies employees. "
                "It must never be shared with the employer or stored alongside "
                "employer-facing deliverables."
            ),
            "engagement_salt": self.engagement_salt,
            "key": self.key,
        }
        return _write_restricted(Path(path), json.dumps(payload, indent=2,
                                                       ensure_ascii=False))

    # -- persistence across restarts ---------------------------------------
    # An unpersisted salt means a restarted process assigns the same person a new
    # pseudonym — two transcripts from one participant then count as two voices,
    # silently inflating participant_count *below* the k actually achieved.

    def save_state(self, data_dir: Path | str) -> Path:
        """Persist the salt and the issued mapping to the restricted directory."""
        payload = {
            "warning": (
                "RESTRICTED — consultant only. The engagement salt is the "
                "pseudonymization key; the mapping re-identifies employees."
            ),
            "engagement_salt": self.engagement_salt,
            "issued": self._issued,
        }
        return _write_restricted(
            restricted_dir(data_dir) / "engagement.json",
            json.dumps(payload, indent=2, ensure_ascii=False))

    @classmethod
    def load_or_create(cls, data_dir: Path | str) -> "Pseudonymizer":
        """The engagement's pseudonymizer, surviving restarts.

        The same person keeps the same pseudonym across a process restart, which
        is the module's own determinism invariant; a fresh engagement creates a
        new salt and persists it immediately.
        """
        path = restricted_dir(data_dir) / "engagement.json"
        if path.exists():
            state = json.loads(path.read_text(encoding="utf-8"))
            return cls(engagement_salt=state["engagement_salt"],
                       _issued=dict(state.get("issued", {})))
        pseudonymizer = cls()
        pseudonymizer.save_state(data_dir)
        return pseudonymizer
