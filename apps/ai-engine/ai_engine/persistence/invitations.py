"""Interview invitations — the only thing the two surfaces share.

The consultant creates an invitation; the employee opens it. This is deliberately the
*entire* interface between the two apps, because the employee surface must be able to
do exactly one thing (answer questions) and nothing else.

Two properties matter:

  * **The token is unguessable** (``secrets.token_urlsafe``), not an interview id. A
    sequential or derivable identifier would let anyone with one link enumerate other
    people's interviews.
  * **The pseudonym is assigned at invitation time**, by the consultant. The employee
    therefore never types their name into the tool at all — there is no field for it.
    Identity enters the system once, on the consultant's side, and is never collected
    from the person whose candour depends on its absence.
"""
from __future__ import annotations

import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

TOKEN_BYTES = 24


class InvitationStatus(str, Enum):
    PENDING = "pending"          # created, not yet opened
    IN_PROGRESS = "in_progress"  # the interview has begun
    COMPLETED = "completed"      # finished and the transcript stored
    WITHDRAWN = "withdrawn"      # the participant stopped; nothing was kept


def new_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


@dataclass
class Invitation:
    token: str
    pseudonym: str
    engagement_id: str = "eng-local"
    tenant_id: str = "tenant-local"
    status: str = InvitationStatus.PENDING.value
    transcript_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def is_open(self) -> bool:
        """Can this invitation still be used to answer questions?"""
        return self.status in (InvitationStatus.PENDING.value,
                               InvitationStatus.IN_PROGRESS.value)

    @property
    def is_finished(self) -> bool:
        return self.status in (InvitationStatus.COMPLETED.value,
                               InvitationStatus.WITHDRAWN.value)


class InvitationStore:
    """One JSON file per invitation, so status can be updated in place."""

    def __init__(self, data_dir: Path | str) -> None:
        self._dir = Path(data_dir) / "invitations"

    @property
    def directory(self) -> Path:
        return self._dir

    def _path(self, token: str) -> Path:
        # The token is the filename, so a traversal attempt cannot escape the
        # directory: anything containing a separator is rejected outright.
        if not token or "/" in token or "\\" in token or token.startswith("."):
            raise ValueError("invalid invitation token")
        return self._dir / f"{token}.json"

    def create(self, *, pseudonym: str, engagement_id: str = "eng-local",
               tenant_id: str = "tenant-local") -> Invitation:
        invitation = Invitation(token=new_token(), pseudonym=pseudonym,
                                engagement_id=engagement_id, tenant_id=tenant_id)
        self.save(invitation)
        return invitation

    def save(self, invitation: Invitation) -> Path:
        invitation.updated_at = datetime.now(timezone.utc).isoformat()
        path = self._path(invitation.token)
        self._dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(invitation), indent=2), encoding="utf-8")
        return path

    def get(self, token: str) -> Invitation | None:
        try:
            path = self._path(token)
        except ValueError:
            return None
        if not path.exists():
            return None
        try:
            return Invitation(**json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            return None

    def set_status(self, token: str, status: InvitationStatus, *,
                   transcript_id: str | None = None) -> Invitation | None:
        invitation = self.get(token)
        if invitation is None:
            return None
        invitation.status = status.value
        if transcript_id is not None:
            invitation.transcript_id = transcript_id
        self.save(invitation)
        return invitation

    def list_all(self) -> list[Invitation]:
        if not self._dir.exists():
            return []
        found: list[Invitation] = []
        for path in sorted(self._dir.glob("*.json")):
            try:
                found.append(Invitation(**json.loads(path.read_text(encoding="utf-8"))))
            except Exception:
                continue
        return sorted(found, key=lambda i: i.created_at, reverse=True)
