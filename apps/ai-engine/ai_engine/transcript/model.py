"""Immutable transcript and segments.

Mirrors the ``transcript`` bounded-context contract in ``apps/core-api`` so that
evidence resolution is deterministic:

  * A :class:`TranscriptSegment` is immutable — its ``id`` and ``text`` are fixed
    at creation and never change. This is what makes an :class:`EvidenceRef`
    resolvable forever.
  * Segments are append-only, and appending is forbidden once the transcript is
    finalized. Corrections would create a *new version*, never mutate a segment
    (not needed for this slice, but the immutability guarantee is enforced).
  * An :class:`EvidenceRef` is a (segment id, char span) that resolves to an exact
    substring — the primitive every downstream claim will hang its provenance on.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


class Speaker(str, Enum):
    INTERVIEWER = "interviewer"
    SUBJECT = "subject"


class TranscriptFinalizedError(RuntimeError):
    """Raised on any attempt to append to a finalized transcript."""


@dataclass(frozen=True)
class TranscriptSegment:
    """An immutable unit of a transcript and the finest evidence anchor."""

    id: str
    transcript_id: str
    sequence: int
    speaker: Speaker
    text: str
    uttered_at: datetime

    def span_text(self, start: int, end: int) -> str:
        if start < 0 or end > len(self.text) or start > end:
            raise ValueError(
                f"CharSpan [{start}:{end}] out of bounds for segment {self.id} "
                f"(len {len(self.text)})"
            )
        return self.text[start:end]


@dataclass(frozen=True)
class EvidenceRef:
    """A resolvable pointer into an immutable segment. Provenance's atom.

    Carries ``transcript_id`` because a reference that does not name its own
    transcript is not self-resolving: once findings from many interviews are
    aggregated, resolving such a ref against the wrong person's transcript would
    silently yield *someone else's words* as evidence. The ratified contract in
    ``packages/contracts`` always specified this; the Python model had drifted from
    it, and the drift was compensated for by carrying the transcript id alongside.
    """

    segment_id: str
    start: int
    end: int
    transcript_id: str = ""

    def resolve(self, transcript: "Transcript") -> str:
        if self.transcript_id and transcript.id != self.transcript_id:
            raise ValueError(
                f"EvidenceRef belongs to transcript {self.transcript_id}, "
                f"cannot resolve against {transcript.id}"
            )
        return transcript.segment(self.segment_id).span_text(self.start, self.end)


@dataclass
class Transcript:
    """Append-only until finalized; then read-only forever."""

    id: str = field(default_factory=lambda: _new_id("txn"))
    engagement_id: str = "eng-unknown"
    tenant_id: str = "tenant-unknown"
    interview_id: str = "int-unknown"
    created_at: datetime = field(default_factory=_now)
    finalized: bool = False
    _segments: list[TranscriptSegment] = field(default_factory=list)

    @property
    def segments(self) -> tuple[TranscriptSegment, ...]:
        return tuple(self._segments)

    def append(self, speaker: Speaker, text: str, uttered_at: datetime | None = None) -> TranscriptSegment:
        if self.finalized:
            raise TranscriptFinalizedError(
                f"Transcript {self.id} is finalized; segments are immutable."
            )
        segment = TranscriptSegment(
            id=_new_id("seg"),
            transcript_id=self.id,
            sequence=len(self._segments),
            speaker=speaker,
            text=text.strip(),
            uttered_at=uttered_at or _now(),
        )
        self._segments.append(segment)
        return segment

    def finalize(self) -> None:
        self.finalized = True

    def segment(self, segment_id: str) -> TranscriptSegment:
        for seg in self._segments:
            if seg.id == segment_id:
                return seg
        raise KeyError(f"No segment {segment_id} in transcript {self.id}")

    def render(self) -> str:
        """Human-readable full transcript (for logs and the report generator)."""
        lines = []
        for seg in self._segments:
            who = "Q" if seg.speaker is Speaker.INTERVIEWER else "A"
            lines.append(f"[{seg.sequence:02d} {who} {seg.id}] {seg.text}")
        return "\n".join(lines)
