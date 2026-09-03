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


class TamperedEventLog(RuntimeError):
    """A log line failed authentication mid-file — the log was modified or corrupted.

    Distinguished from a *torn final line* (a process that died mid-append), which
    is tolerated: truncation damage lands at the end of an append-only file, so an
    authentication failure on any earlier line is tampering, not a crash. Swallowing
    it would erase an event rather than surface the modification — the exact
    opposite of what authenticated encryption is for.
    """


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
        from .crypto import assert_encrypted_in_production

        assert_encrypted_in_production(self._cipher, f"the {layer} event log")
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

    Tampering is loud: a line that fails authentication anywhere but the end of the
    file raises :class:`TamperedEventLog` rather than quietly dropping the event it
    used to carry. Only the final line may fail silently — a process that died
    mid-append leaves a torn line there, and that is damage, not tampering.
    """
    path = Path(path)
    if not path.exists():
        return []
    encrypted = path.name.endswith(".enc")
    if encrypted and (cipher is None or not cipher.protects_at_rest):
        raise ValueError(f"{path.name} is encrypted but no cipher was supplied")

    records: list[dict] = []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
             if line.strip()]
    for index, line in enumerate(lines):
        last = index == len(lines) - 1
        if encrypted:
            try:
                raw = cipher.decrypt(line.encode("ascii")).decode("utf-8")
            except Exception as exc:
                if last:
                    continue  # torn final line: the process died mid-append
                raise TamperedEventLog(
                    f"line {index + 1} of {path.name} failed authentication — "
                    f"the log was modified or corrupted") from exc
        else:
            raw = line
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            if last:
                continue
            raise TamperedEventLog(
                f"line {index + 1} of {path.name} is not a valid event record") from exc
    return records
