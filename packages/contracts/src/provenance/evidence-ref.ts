import type { TranscriptId, SegmentId } from '../primitives/ids';
import type { Timestamp } from '../primitives/scalars';
import type { CharSpan } from './char-span';
import type { SourcePerspective } from './source-perspective';

/**
 * An immutable pointer to an exact span of an append-only transcript segment —
 * the anchor for `Stated` and `Corroborated` evidence. Because transcripts are
 * immutable (Transcript context invariants T1–T3), an `EvidenceRef` is a stable,
 * forever-resolvable citation.
 *
 * Discriminated from `Derivation` by `anchorType`.
 */
export interface EvidenceRef {
  readonly anchorType: 'TranscriptRef';
  readonly transcriptId: TranscriptId;
  readonly segmentId: SegmentId;
  readonly span: CharSpan;
  readonly speaker: SourcePerspective;
  readonly utteredAt: Timestamp;
}
