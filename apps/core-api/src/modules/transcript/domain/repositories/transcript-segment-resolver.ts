import type { TranscriptId, SegmentId, EvidenceRef } from '@oi/contracts';
import type { TranscriptSegment } from '../entities/transcript-segment';

/**
 * A resolved segment together with the exact quoted substring an `EvidenceRef`
 * selects: `quote` is `segment.text` sliced by the ref's `CharSpan`.
 */
export interface ResolvedEvidence {
  readonly segment: TranscriptSegment;
  readonly quote: string;
}

/**
 * **Read-model port** that makes requirement #1 a contract: an `EvidenceRef`
 * resolves **deterministically** to an immutable segment and its quoted span.
 *
 * Resolution keys on `(transcriptId, segmentId)` — never on a version — and that
 * content never changes (T1, T2, T4), so:
 *  - the same `EvidenceRef` always yields the same segment and quote, and
 *  - transcript versioning never breaks an existing `EvidenceRef` (T5).
 *
 * Read-only; it never mutates the transcript. Interface only — no resolution
 * logic here.
 */
export interface TranscriptSegmentResolver {
  resolveSegment(transcriptId: TranscriptId, segmentId: SegmentId): Promise<TranscriptSegment | null>;

  resolveEvidence(ref: EvidenceRef): Promise<ResolvedEvidence | null>;
}
