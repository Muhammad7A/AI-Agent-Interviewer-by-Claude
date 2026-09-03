"""Resumable in-flight interviews.

In-flight interviews were held in memory, deliberately: an interview that was never
submitted has not been consented to, so writing it to disk felt like retaining
testimony the participant never agreed to hand over.

That reasoning protected the wrong thing. A fifteen-minute interview that vanishes
because a tab closed, a phone slept, or a process restarted does not protect anyone —
it loses their time, produces abandoned interviews, and biases the data toward whoever
happened to have a stable connection. The participant's actual interest is that their
answers survive long enough for *them* to decide, and disappear completely if they
decide against it.

So the resolution is not "never persist" but **persist under the same guarantees as
everything else**:

  * Encrypted at rest with the configured cipher, exactly like the transcript store.
  * Marked ``submitted = false`` — an unsubmitted interview is working state, never a
    consented record, and nothing downstream reads it.
  * **Deleted on withdrawal**, and the deletion is what makes the right to withdraw
    real. A test withdraws mid-interview and then greps the data directory.
  * Expired and swept after a fixed window, so an abandoned draft does not linger
    indefinitely as testimony nobody agreed to leave behind.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..transcript.model import Speaker, Transcript
from .crypto import Cipher, NullCipher
from .transcript_store import transcript_from_dict, transcript_to_dict

SCHEMA = "ontora.session/v1"
_PLAIN = ".session.json"
_ENCRYPTED = ".session.enc"

#: An unsubmitted draft older than this is swept. Long enough to survive a broken
#: connection or a lunch break; short enough that it is not an archive.
DEFAULT_TTL = timedelta(hours=24)


@dataclass
class SavedSession:
    token: str
    transcript: Transcript
    pending_question: str | None
    turn_count: int
    closed: bool
    updated_at: datetime | None = None
    #: Always false on disk. A submitted interview lives in the transcript store.
    submitted: bool = False

    def is_expired(self, ttl: timedelta = DEFAULT_TTL, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return (now - self.updated_at) > ttl

    def answered_pairs(self) -> list[dict]:
        pairs: list[dict] = []
        pending: str | None = None
        for segment in self.transcript.segments:
            if segment.speaker is Speaker.INTERVIEWER:
                pending = segment.text
            elif pending is not None:
                pairs.append({"question": pending, "answer": segment.text})
                pending = None
        return pairs


class SessionStore:
    """Encrypted, expiring storage for interviews that are not yet submitted."""

    def __init__(self, data_dir: Path | str, cipher: Cipher | None = None) -> None:
        self._dir = Path(data_dir) / "sessions"
        self._cipher = cipher or NullCipher()
        from .crypto import assert_encrypted_in_production

        assert_encrypted_in_production(self._cipher, "the session-draft store")

    @property
    def directory(self) -> Path:
        return self._dir

    @property
    def encrypted(self) -> bool:
        return self._cipher.protects_at_rest

    def _path(self, token: str) -> Path:
        if not token or "/" in token or "\\" in token or token.startswith("."):
            raise ValueError("invalid session token")
        return self._dir / f"{token}{_ENCRYPTED if self.encrypted else _PLAIN}"

    def save(self, session: SavedSession) -> Path:
        payload = {
            "schema": SCHEMA,
            "token": session.token,
            "pending_question": session.pending_question,
            "turn_count": session.turn_count,
            "closed": session.closed,
            "submitted": False,  # never true on disk, by construction
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "transcript": transcript_to_dict(session.transcript),
        }
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._path(session.token)
        path.write_bytes(self._cipher.encrypt(
            json.dumps(payload, ensure_ascii=False).encode("utf-8")))
        return path

    def load(self, token: str) -> SavedSession | None:
        for suffix, encrypted in ((_ENCRYPTED, True), (_PLAIN, False)):
            try:
                path = self._dir / f"{token}{suffix}"
            except (ValueError, TypeError):
                return None
            if not path.exists():
                continue
            try:
                blob = path.read_bytes()
                raw = self._cipher.decrypt(blob) if encrypted else blob
                data = json.loads(raw.decode("utf-8"))
                if data.get("schema") != SCHEMA:
                    return None
                transcript = transcript_from_dict(data["transcript"])
                # A stored draft is by definition unfinalized; restore it that way so
                # the interview can continue.
                transcript.finalized = False
                return SavedSession(
                    token=data["token"],
                    transcript=transcript,
                    pending_question=data.get("pending_question"),
                    turn_count=int(data.get("turn_count", 0)),
                    closed=bool(data.get("closed", False)),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                )
            except Exception:
                return None
        return None

    def delete(self, token: str) -> bool:
        """Remove a draft entirely. This is what makes withdrawal real."""
        removed = False
        for suffix in (_ENCRYPTED, _PLAIN):
            try:
                path = self._dir / f"{token}{suffix}"
            except (ValueError, TypeError):
                continue
            if path.exists():
                path.unlink()
                removed = True
        return removed

    def sweep(self, ttl: timedelta = DEFAULT_TTL, now: datetime | None = None) -> int:
        """Delete expired drafts. An abandoned draft is not an archive."""
        if not self._dir.exists():
            return 0
        removed = 0
        for path in list(self._dir.iterdir()):
            token = path.name
            for suffix in (_ENCRYPTED, _PLAIN):
                if token.endswith(suffix):
                    token = token[: -len(suffix)]
                    break
            else:
                continue
            session = self.load(token)
            if session is None or session.is_expired(ttl, now):
                self.delete(token)
                removed += 1
        return removed
