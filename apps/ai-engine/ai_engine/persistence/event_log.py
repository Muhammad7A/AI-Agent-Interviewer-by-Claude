"""Append-only, event-sourced sink for the *testimony* layer only.

This is the seed corn the roadmap tells us to capture from day one. It writes
one JSONL line per event. It deliberately records **only** raw testimony
(who said what, when, which segment) — never interpretation, validation, or
outcome. Fusing those layers is a constitutional violation (C7), so the schema
here has no field that could hold them.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EventLog:
    """Writes testimony-layer events to ``<data_dir>/<interview_id>.testimony.jsonl``."""

    LAYER = "testimony"

    def __init__(self, data_dir: Path, interview_id: str) -> None:
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._path = self._dir / f"{interview_id}.testimony.jsonl"
        self._interview_id = interview_id

    @property
    def path(self) -> Path:
        return self._path

    def emit(self, event: str, **payload: Any) -> None:
        record = {
            "layer": self.LAYER,
            "event": event,
            "interview_id": self._interview_id,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


class NullEventLog(EventLog):
    """A no-op log for tests and dry runs."""

    def __init__(self) -> None:  # noqa: D107 - intentionally skips file setup
        self._interview_id = "null"

    def emit(self, event: str, **payload: Any) -> None:  # noqa: D102
        return None
