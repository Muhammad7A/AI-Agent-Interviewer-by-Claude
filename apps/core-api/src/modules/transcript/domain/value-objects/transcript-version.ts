import type { Timestamp, SegmentId } from '@oi/contracts';
import type { VersionNumber } from './version-number';

/**
 * An immutable snapshot of the transcript at a finalization point.
 *
 * Versioning is **additive**: each version's `segmentIds` is a superset of the
 * prior version's, and existing segment ids and content are preserved. That is
 * precisely why `EvidenceRef`s created against an earlier version keep resolving
 * (T5). A `TranscriptVersion` is a value object — once finalized it never
 * changes.
 */
export interface TranscriptVersion {
  readonly versionNumber: VersionNumber;
  readonly finalizedAt: Timestamp;
  readonly segmentIds: readonly SegmentId[];
  /** The version this one supersedes, if any (absent for the first version). */
  readonly supersedes?: VersionNumber;
}
