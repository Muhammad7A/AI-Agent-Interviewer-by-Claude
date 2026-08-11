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

from .crypto import Cipher, NullCipher


class EventLog:
    """Append-only sink for ONE dataset layer.

    Each layer is written to its own file — ``<interview_id>.<layer>.jsonl`` — so
    testimony and interpretation are never fused into one stream (C7). The default
    layer is ``testimony``; the evidence tagger uses ``interpretation``.

    **Encrypted at rest when a cipher is configured.** These logs are not metadata:
    the interpretation layer carries claim statements drawn verbatim from testimony,
    and the validation layer carries them again alongside a consultant's judgement.
    Encrypting the transcript store while leaving these in plaintext protected the
    tidiest copy of the sensitive material and left two untidier ones exposed.

    Because the format is append-only JSONL, each *line* is encrypted independently
    rather than the file as a whole — appending must not require decrypting and
    rewriting everything written so far.
    """

    def __init__(self, data_dir: Path, interview_id: str, layer: str = "testimony",
                 cipher: "Cipher | None" = None) -> None:
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._layer = layer
        self._cipher = cipher or NullCipher()
        suffix = "jsonl.enc" if self._cipher.protects_at_rest else "jsonl"
        self._path = self._dir / f"{interview_id}.{layer}.{suffix}"
        self._interview_id = interview_id

    @property
    def encrypted(self) -> bool:
        return self._cipher.protects_at_rest

    @property
    def path(self) -> Path:
        return self._path

    @property
    def layer(self) -> str:
        return self._layer

    def emit(self, event: str, **payload: Any) -> None:
        record = {
            "layer": self._layer,
            "event": event,
            "interview_id": self._interview_id,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        line = json.dumps(record, ensure_ascii=False)
        if self._cipher.protects_at_rest:
            # One ciphertext per record, base64 already, so the file stays line
            # oriented and appendable without touching what came before.
            blob = self._cipher.encrypt(line.encode("utf-8")).decode("ascii")
            with self._path.open("a", encoding="ascii") as fh:
                fh.write(blob + "\n")
        else:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")

    def read(self) -> list[dict]:
        """Every record, decrypting if needed. A malformed line is skipped, not fatal."""
        return read_events(self._path, self._cipher)


class NullEventLog(EventLog):
    """A no-op log for tests and dry runs."""

    def __init__(self, layer: str = "testimony") -> None:  # noqa: D107
        self._layer = layer
        self._interview_id = "null"
        self._cipher = NullCipher()

    def emit(self, event: str, **payload: Any) -> None:  # noqa: D102
        return None

    def read(self) -> list[dict]:  # noqa: D102
        return []


def find_log(data_dir: Path, interview_id: str, layer: str) -> Path | None:
    """Locate a layer's log, whichever form it was written in."""
    for suffix in ("jsonl.enc", "jsonl"):
        path = Path(data_dir) / f"{interview_id}.{layer}.{suffix}"
        if path.exists():
            return path
    return None


def read_events(path: Path, cipher: "Cipher | None" = None) -> list[dict]:
    """Read a log written in either form.

    Reads what is actually on disk rather than what the caller is configured for, so
    plaintext logs written during development still load once a key is introduced.
    """
    path = Path(path)
    if not path.exists():
        return []
    encrypted = path.name.endswith(".enc")
    if encrypted and (cipher is None or not cipher.protects_at_rest):
        raise ValueError(f"{path.name} is encrypted but no cipher was supplied")

    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw = cipher.decrypt(line.encode("ascii")).decode("utf-8") if encrypted else line
            records.append(json.loads(raw))
        except Exception:
            continue  # a partial or corrupt line must not lose the rest of the log
    return records
