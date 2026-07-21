import type { TranscriptId, SegmentId, Timestamp } from '@oi/contracts';
import type { SpeakerId } from '../value-objects/ids';
import type { SegmentText } from '../value-objects/segment-text';
import type { TimeRange } from '../value-objects/time-range';
import type { VersionNumber } from '../value-objects/version-number';

/**
 * **Entity.** An immutable unit of a transcript and the **finest evidence
 * anchor**. Its `id` (a Shared Kernel `SegmentId`) and `text` are fixed at
 * creation and never change (T1, T2, T4) — this immutability is what makes
 * `EvidenceRef` resolution deterministic. An `EvidenceRef`'s `CharSpan` indexes
 * into `text`; `utteredAt` matches `EvidenceRef.utteredAt`.
 *
 * State contract only. Behaviour (none — segments are immutable) is not modeled.
 */
export interface TranscriptSegment {
  readonly id: SegmentId;
  readonly transcriptId: TranscriptId;
  /** Stable position of this segment within the transcript (T3). */
  readonly sequence: number;
  readonly speakerId: SpeakerId;
  readonly text: SegmentText;
  readonly utteredAt: Timestamp;
  readonly timeRange?: TimeRange;
  /** The version in which this segment first appeared. */
  readonly introducedInVersion: VersionNumber;
}
