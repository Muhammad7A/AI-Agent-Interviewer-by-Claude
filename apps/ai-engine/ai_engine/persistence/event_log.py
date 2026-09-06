"""Append-only, event-sourced sink for the *testimony* layer only.

This is the seed corn the roadmap tells us to capture from day one. It writes
one JSONL line per event. It deliberately records **only** raw testimony
(who said what, when, which segment) — never interpretation, validation, or
outcome. Fusing those layers is a constitutional violation (C7), so the schema
here has no field that could hold them.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
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


class TruncatedEventLog(TamperedEventLog):
    """Records are missing from the end of the log.

    Per-line authenticated encryption authenticates each record's *content* and
    nothing else, so it cannot see a record that is no longer there: deleting the
    last few lines of an append-only log left a file that read as perfectly clean.
    For a system whose product is auditability, removal is the cheapest and most
    useful attack, and it was the one the log could not detect.

    Two mechanisms close it, and both must be defeated together. Each record
    carries its sequence number and the digest of the line before it, so the file
    is a chain rather than a bag of independent records; and a sidecar head file
    records how long that chain should be. Truncating the log now contradicts the
    head; rewriting the head to match requires recomputing a chain whose links are
    inside authenticated ciphertext.
    """


#: Field names for the chain. Kept short — they are written on every record.
_SEQ = "seq"
_PREV = "prev"
_HEAD_SUFFIX = ".head"


def _digest(line: str) -> str:
    """The chain link: a digest over the line exactly as it sits on disk."""
    return sha256(line.encode("utf-8")).hexdigest()


def head_path(log_path: Path) -> Path:
    """The sidecar recording how long the chain should be."""
    return Path(log_path).with_name(Path(log_path).name + _HEAD_SUFFIX)


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
        #: (next sequence number, previous line digest); read from disk on demand.
        self._tip: tuple[int, str] | None = None

    @property
    def encrypted(self) -> bool:
        return self._cipher.protects_at_rest

    @property
    def path(self) -> Path:
        return self._path

    @property
    def layer(self) -> str:
        return self._layer

    def _chain_tip(self) -> tuple[int, str]:
        """The (next sequence number, previous digest) to write, from the file itself.

        Read from disk rather than held only in memory so that appending to a log
        this process did not create — a resumed interview — continues the same
        chain instead of restarting it.
        """
        if self._tip is None:
            lines = _nonempty_lines(self._path)
            self._tip = (len(lines), _digest(lines[-1]) if lines else "")
        return self._tip

    def emit(self, event: str, **payload: Any) -> None:
        seq, prev = self._chain_tip()
        record = {
            "layer": self._layer,
            "event": event,
            "interview_id": self._interview_id,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            # The chain: this record's position, and the digest of the line before
            # it. Content authentication cannot detect a record that was removed;
            # a chain plus a recorded length can.
            _SEQ: seq,
            _PREV: prev,
            **payload,
        }
        line = json.dumps(record, ensure_ascii=False)
        if self._cipher.protects_at_rest:
            # One ciphertext per record, base64 already, so the file stays line
            # oriented and appendable without touching what came before.
            line = self._cipher.encrypt(line.encode("utf-8")).decode("ascii")
            with self._path.open("a", encoding="ascii") as fh:
                fh.write(line + "\n")
        else:
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        self._tip = (seq + 1, _digest(line))
        self._write_head(seq + 1, _digest(line))

    def _write_head(self, length: int, digest: str) -> None:
        """Record how long the chain is, atomically.

        Written after the append, so a crash between the two leaves a head that is
        one behind the log — read as a torn final line, which is the tolerated
        direction. A head *ahead* of the log is the untolerated one: records are
        missing.
        """
        head = head_path(self._path)
        tmp = head.with_name(f".{head.name}.tmp")
        tmp.write_text(json.dumps({"length": length, "digest": digest}),
                       encoding="utf-8")
        os.replace(tmp, head)

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
    _verify_chain(path, lines, records)
    return records


def _verify_chain(path: Path, lines: list[str], records: list[dict]) -> None:
    """Check the sequence/digest chain and the recorded length.

    Skipped entirely for records written before the chain existed: a log whose
    records carry no ``seq`` is read exactly as it was before, so development logs
    and stored fixtures keep working. A log that *does* carry the chain is held to
    it — an unchained record appearing among chained ones is itself the finding.
    """
    chained = [r for r in records if _SEQ in r]
    if not chained:
        return
    if len(chained) != len(records):
        raise TamperedEventLog(
            f"{path.name} mixes chained and unchained records — "
            f"{len(records) - len(chained)} record(s) carry no sequence number")

    previous = ""
    for index, record in enumerate(records):
        if record.get(_SEQ) != index:
            raise TamperedEventLog(
                f"{path.name} record {index} claims sequence {record.get(_SEQ)!r} — "
                f"records were reordered or removed from the middle")
        if record.get(_PREV, "") != previous:
            raise TamperedEventLog(
                f"{path.name} record {index} does not link to the record before it — "
                f"the log was modified")
        previous = _digest(lines[index])

    head = head_path(path)
    if not head.exists():
        return
    try:
        state = json.loads(head.read_text(encoding="utf-8"))
        expected = int(state["length"])
    except (OSError, ValueError, KeyError) as exc:
        raise TamperedEventLog(
            f"{head.name} could not be read; the log's expected length is unknown"
        ) from exc
    # One short is the tolerated direction: a crash between appending the record
    # and updating the head. More than one, or a head shorter than the log, means
    # records were removed or added behind the head's back.
    if len(records) < expected - 1:
        raise TruncatedEventLog(
            f"{path.name} holds {len(records)} record(s) but the chain head "
            f"records {expected} — {expected - len(records)} were removed")
    if len(records) > expected:
        raise TamperedEventLog(
            f"{path.name} holds {len(records)} record(s) but the chain head "
            f"records only {expected} — records were appended without the head")


def _nonempty_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
