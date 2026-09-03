"""Durable storage for transcripts — so evidence outlives the process.

The architecture's central claim is that every finding resolves to an immutable
source. Before this existed, that claim held only *inside a single process*: the
transcript lived in memory, the event log recorded segment ids and a character count
but never the words, and so the moment the process exited every ``EvidenceRef`` in
every report pointed at a segment that no longer existed. Quotes could not be
re-verified, the safety gates could not be re-run, and a consultant could not answer
"show me why you believe this" the next day.

The invariant this module exists to provide, and which its tests assert directly:

    a rehydrated transcript resolves every EvidenceRef to exactly the same text
    as the original.

That requires storing segment ids, order, and text byte-for-byte — offsets are
character positions, so a single normalisation would silently shift every quote.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..transcript.model import Speaker, Transcript, TranscriptSegment
from .crypto import Cipher, NullCipher

SCHEMA = "ontora.transcript/v1"
_PLAIN_SUFFIX = ".transcript.json"
_ENCRYPTED_SUFFIX = ".transcript.enc"


class TranscriptNotFound(KeyError):
    pass


def _segment_to_dict(segment: TranscriptSegment) -> dict:
    return {
        "id": segment.id,
        "sequence": segment.sequence,
        "speaker": segment.speaker.value,
        "text": segment.text,
        "uttered_at": segment.uttered_at.isoformat(),
    }


def _segment_from_dict(data: dict, transcript_id: str) -> TranscriptSegment:
    return TranscriptSegment(
        id=data["id"],
        transcript_id=transcript_id,
        sequence=int(data["sequence"]),
        speaker=Speaker(data["speaker"]),
        text=data["text"],
        uttered_at=datetime.fromisoformat(data["uttered_at"]),
    )


def transcript_to_dict(transcript: Transcript) -> dict:
    return {
        "schema": SCHEMA,
        "id": transcript.id,
        "engagement_id": transcript.engagement_id,
        "tenant_id": transcript.tenant_id,
        "interview_id": transcript.interview_id,
        "created_at": transcript.created_at.isoformat(),
        "finalized": transcript.finalized,
        "segments": [_segment_to_dict(s) for s in transcript.segments],
    }


def transcript_from_dict(data: dict) -> Transcript:
    schema = data.get("schema")
    if schema != SCHEMA:
        raise ValueError(f"unsupported transcript schema: {schema!r}")
    transcript_id = data["id"]
    return Transcript.rehydrate(
        id=transcript_id,
        engagement_id=data["engagement_id"],
        tenant_id=data["tenant_id"],
        interview_id=data["interview_id"],
        created_at=datetime.fromisoformat(data["created_at"]),
        finalized=bool(data["finalized"]),
        segments=[_segment_from_dict(s, transcript_id) for s in data["segments"]],
    )


class TranscriptStore:
    """File-backed, write-once transcript storage.

    Write-once mirrors the domain rule: a finalized transcript is immutable, so
    overwriting a stored one is refused. Corrections would create a new version
    (not implemented in the thin slice), never a mutation of the evidence base.
    """

    def __init__(self, data_dir: Path | str, cipher: Cipher | None = None) -> None:
        self._dir = Path(data_dir) / "transcripts"
        self._cipher = cipher or NullCipher()
        from .crypto import assert_encrypted_in_production

        assert_encrypted_in_production(self._cipher, "the transcript store")

    @property
    def directory(self) -> Path:
        return self._dir

    @property
    def cipher(self) -> Cipher:
        return self._cipher

    @property
    def encrypted(self) -> bool:
        return self._cipher.protects_at_rest

    def _path(self, transcript_id: str) -> Path:
        suffix = _ENCRYPTED_SUFFIX if self.encrypted else _PLAIN_SUFFIX
        return self._dir / f"{transcript_id}{suffix}"

    def exists(self, transcript_id: str) -> bool:
        return any(
            (self._dir / f"{transcript_id}{suffix}").exists()
            for suffix in (_ENCRYPTED_SUFFIX, _PLAIN_SUFFIX)
        )

    def save(self, transcript: Transcript, *, overwrite: bool = False) -> Path:
        path = self._path(transcript.id)
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"transcript {transcript.id} is already stored; a finalized "
                f"transcript is immutable (pass overwrite=True only to repair)"
            )
        self._dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(transcript_to_dict(transcript), ensure_ascii=False, indent=2)
        path.write_bytes(self._cipher.encrypt(payload.encode("utf-8")))
        return path

    def load(self, transcript_id: str) -> Transcript:
        for suffix, needs_cipher in ((_ENCRYPTED_SUFFIX, True), (_PLAIN_SUFFIX, False)):
            path = self._dir / f"{transcript_id}{suffix}"
            if not path.exists():
                continue
            blob = path.read_bytes()
            # Read what is actually on disk rather than what this store is
            # configured for, so a plaintext file written in development still
            # loads after a key is introduced.
            raw = self._cipher.decrypt(blob) if needs_cipher else blob
            return transcript_from_dict(json.loads(raw.decode("utf-8")))
        raise TranscriptNotFound(
            f"no stored transcript {transcript_id} in {self._dir}"
        )

    def list_ids(self) -> list[str]:
        if not self._dir.exists():
            return []
        ids: set[str] = set()
        for path in self._dir.iterdir():
            for suffix in (_ENCRYPTED_SUFFIX, _PLAIN_SUFFIX):
                if path.name.endswith(suffix):
                    ids.add(path.name[: -len(suffix)])
        return sorted(ids)
