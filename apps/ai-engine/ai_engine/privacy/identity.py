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

from ..persistence.crypto import Cipher, NullCipher, assert_encrypted_in_production

PSEUDONYM_PREFIX = "P-"
#: Hex characters kept from the digest. Short enough to read aloud, long enough
#: that a birthday collision between participants is negligible for any real
#: engagement — and a collision silently *merges* two people's testimony,
#: corrupting corroboration and k.
#:
#: At the previous 6 chars (24 bits) the birthday bound is ~1% at 581
#: participants and **52%** at 5,000 — not the "~1% around 5,000" an earlier
#: comment here claimed, which understated the exposure by roughly 8x in n. At
#: 12 chars (48 bits) the same 5,000 participants give ~4e-6%.
_PSEUDONYM_HEX = 12

#: Encrypted and plaintext forms of the restricted files. As with the event logs,
#: what is on disk decides how it is read, so a plaintext engagement written in
#: development still loads once a key is introduced.
_ENC_SUFFIX = ".enc"


class CorruptIdentityState(RuntimeError):
    """The engagement's identity state exists but cannot be read."""


def new_engagement_salt() -> str:
    """A fresh, high-entropy salt. One per engagement; store it with the key."""
    return secrets.token_hex(16)


def restricted_dir(data_dir: Path | str) -> Path:
    """Where re-identification material lives — deliberately not beside deliverables.

    SECURITY.md's rule is that the key is never stored alongside employer-facing
    artifacts; one ``--write`` run emits both into ``data_dir``, so the key gets
    its own subdirectory and only ever shares a tree with them, never a directory.

    The directory itself is owner-only (0700), not just the files inside it. The
    file mode is what protects the content, but a world-traversable directory
    still discloses which engagements exist, and that is a list of who has been
    interviewed.
    """
    path = Path(data_dir) / "RESTRICTED"
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:  # pragma: no cover - filesystems that do not honor modes
        pass
    return path


def _write_restricted(path: Path, payload: bytes) -> Path:
    """Write re-identification material atomically, owner-only.

    Two properties, both learned the hard way elsewhere in this package:

    **Owner-only.** POSIX 0600. Windows ACLs are broader than a POSIX mode can
    express, so the stronger guarantee there is the *location*
    (:func:`restricted_dir`) — but the mode is still set wherever it is honored.

    **Atomic.** Written to a temporary file in the same directory and then
    ``os.replace``d, which is atomic on POSIX and Windows alike. A truncate-then-write
    left a window where a crash produced a half-written ``engagement.json``, and
    that file is not reconstructible: losing it makes every pseudonym already
    issued permanently unresolvable, so a partial write is the one failure this
    module cannot absorb.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)
    return path


def _seal(text: str, cipher: Cipher | None) -> bytes:
    effective = cipher or NullCipher()
    raw = text.encode("utf-8")
    return effective.encrypt(raw) if effective.protects_at_rest else raw


def _restricted_path(base: Path, cipher: Cipher | None) -> Path:
    """``base`` or ``base.enc``, according to whether the cipher protects at rest."""
    effective = cipher or NullCipher()
    return base.with_name(base.name + _ENC_SUFFIX) if effective.protects_at_rest else base


def _read_restricted(base: Path, cipher: Cipher | None) -> dict | None:
    """Read whichever form is on disk, or ``None`` when neither exists.

    Prefers the encrypted file when both are present: a plaintext leftover from
    development must never silently win over the sealed copy.
    """
    encrypted = base.with_name(base.name + _ENC_SUFFIX)
    if encrypted.exists():
        effective = cipher or NullCipher()
        if not effective.protects_at_rest:
            raise ValueError(
                f"{encrypted.name} is encrypted but no storage key is configured; "
                f"set {'ONTORA_STORE_KEY'} to read the engagement's identity state")
        return json.loads(effective.decrypt(encrypted.read_bytes()).decode("utf-8"))
    if base.exists():
        return json.loads(base.read_text(encoding="utf-8"))
    return None


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

    def write_key(self, path: Path, cipher: Cipher | None = None) -> Path:
        """Write the re-identification key to its own restricted file.

        Encrypted at rest under the same cipher as everything else when a storage
        key is configured; refused outright in production without one.
        """
        assert_encrypted_in_production(cipher or NullCipher(),
                                       "the re-identification key")
        payload = {
            "warning": (
                "RESTRICTED — consultant only. This file re-identifies employees. "
                "It must never be shared with the employer or stored alongside "
                "employer-facing deliverables."
            ),
            "engagement_salt": self.engagement_salt,
            "key": self.key,
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        return _write_restricted(_restricted_path(Path(path), cipher),
                                 _seal(text, cipher))

    # -- persistence across restarts ---------------------------------------
    # An unpersisted salt means a restarted process assigns the same person a new
    # pseudonym — two transcripts from one participant then count as two voices,
    # silently inflating participant_count *below* the k actually achieved.

    def save_state(self, data_dir: Path | str, cipher: Cipher | None = None) -> Path:
        """Persist the salt and the issued mapping to the restricted directory.

        This file maps real identities to pseudonyms — it is the one artifact that
        converts the whole pseudonymous corpus back to named employees, which makes
        it the most sensitive thing the system writes. It was previously exempt from
        the at-rest rule that the transcript, event log, session and derived-result
        stores all enforce; it is not exempt now.
        """
        assert_encrypted_in_production(cipher or NullCipher(),
                                       "the engagement's identity mapping")
        payload = {
            "warning": (
                "RESTRICTED — consultant only. The engagement salt is the "
                "pseudonymization key; the mapping re-identifies employees."
            ),
            "engagement_salt": self.engagement_salt,
            "issued": self._issued,
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        base = restricted_dir(data_dir) / "engagement.json"
        return _write_restricted(_restricted_path(base, cipher), _seal(text, cipher))

    @classmethod
    def load_or_create(cls, data_dir: Path | str,
                       cipher: Cipher | None = None) -> "Pseudonymizer":
        """The engagement's pseudonymizer, surviving restarts.

        The same person keeps the same pseudonym across a process restart, which
        is the module's own determinism invariant; a fresh engagement creates a
        new salt and persists it immediately.

        A corrupt state file raises rather than silently starting a new engagement:
        re-salting would give every already-interviewed person a new pseudonym, so
        their prior testimony would count as a second voice and the reported k would
        describe a group that does not exist. Refusing to start is recoverable;
        quietly re-issuing is not.
        """
        base = restricted_dir(data_dir) / "engagement.json"
        try:
            state = _read_restricted(base, cipher)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CorruptIdentityState(
                f"{base.name} could not be read ({type(exc).__name__}). Restore it "
                f"from backup — starting a fresh engagement would re-issue every "
                f"pseudonym and silently corrupt corroboration counts."
            ) from exc
        if state is not None:
            if "engagement_salt" not in state:
                raise CorruptIdentityState(
                    f"{base.name} has no engagement_salt; it is not a usable "
                    f"identity state file.")
            return cls(engagement_salt=state["engagement_salt"],
                       _issued=dict(state.get("issued", {})))
        pseudonymizer = cls()
        pseudonymizer.save_state(data_dir, cipher)
        return pseudonymizer
