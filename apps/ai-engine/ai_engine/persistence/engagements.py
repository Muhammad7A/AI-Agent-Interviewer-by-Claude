"""Engagement registry — the consultant's unit of work.

An engagement is a client mandate: a named group of interviews that produces one
synthesis and one employer release. The registry is deliberately a small JSON
index (names and dates only — no testimony, no participant data), so grouping
never touches the privacy firewall: transcripts stay exactly where they were,
each still carrying its own ``engagement_id``.
"""
from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "groundwork.engagements/v1"
DEFAULT_ENGAGEMENT = "eng-local"


class EngagementStore:
    """One JSON index under the data dir."""

    def __init__(self, data_dir: Path | str) -> None:
        self._path = Path(data_dir) / "engagements" / "index.json"

    def _read(self) -> dict:
        if not self._path.exists():
            return {"schema": SCHEMA, "engagements": {}}
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return self._quarantine_corrupt()
        if data.get("schema") != SCHEMA:
            return self._quarantine_corrupt()
        return data

    def _quarantine_corrupt(self) -> dict:
        """A corrupt index is preserved, never silently reset.

        The worst version of this failure used to be silent: a corrupt index
        read as empty, and the next ``create()`` overwrote the file — every
        engagement name gone without a trace. Now the corrupt file is moved
        aside (forensics stay possible) and the registry starts fresh, loudly.
        Transcripts are unaffected: each still carries its own engagement_id.
        """
        import sys
        from datetime import datetime, timezone as _tz

        backup = self._path.with_name(
            f"{self._path.name}.corrupt-"
            f"{datetime.now(_tz.utc).strftime('%Y%m%dT%H%M%S')}")
        try:
            self._path.replace(backup)
            print(f"WARNING: corrupt engagement index quarantined as {backup.name} "
                  f"— the registry starts fresh; transcript grouping is unaffected "
                  f"(transcripts carry their own engagement_id).", file=sys.stderr)
        except OSError:
            print("WARNING: corrupt engagement index could not be quarantined; "
                  "proceeding with a fresh registry.", file=sys.stderr)
        return {"schema": SCHEMA, "engagements": {}}

    def _write(self, data: dict) -> Path:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                              encoding="utf-8")
        return self._path

    def create(self, name: str) -> dict:
        data = self._read()
        engagement_id = f"eng-{secrets.token_hex(5)}"
        entry = {
            "id": engagement_id,
            "name": name.strip() or "Untitled engagement",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data["engagements"][engagement_id] = entry
        self._write(data)
        return entry

    def ensure(self, engagement_id: str, name: str | None = None) -> dict:
        """Registered or not, the id will be — lazy default-engagement support."""
        data = self._read()
        existing = data["engagements"].get(engagement_id)
        if existing is not None:
            return existing
        entry = {
            "id": engagement_id,
            "name": (name or ("Ad-hoc interviews" if engagement_id == DEFAULT_ENGAGEMENT
                              else engagement_id)),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data["engagements"][engagement_id] = entry
        self._write(data)
        return entry

    def list(self) -> list[dict]:
        return sorted(self._read()["engagements"].values(),
                      key=lambda e: e["created_at"])

    def get(self, engagement_id: str) -> dict | None:
        return self._read()["engagements"].get(engagement_id)
