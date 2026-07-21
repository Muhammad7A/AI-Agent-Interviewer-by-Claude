import type { Brand } from '@oi/contracts';

/**
 * Transcript-context identities.
 *
 * `TranscriptId` and `SegmentId` are **owned by the Shared Kernel** and reused
 * here (not redefined) — every `EvidenceRef` targets exactly these, so they are
 * the immutable identifiers the whole evidence spine depends on. `SpeakerId` and
 * `RecordingId` are new to this context and reuse the kernel's `Brand` primitive.
 */

/** Re-exported Shared Kernel identifiers — the immutable evidence anchors. */
export type { TranscriptId, SegmentId } from '@oi/contracts';

/** Identity of a `Speaker` entity within a transcript. */
export type SpeakerId = Brand<string, 'SpeakerId'>;

/** Identity of a `Recording` entity. */
export type RecordingId = Brand<string, 'RecordingId'>;
