import type { SegmentId } from '@oi/contracts';
import type { VersionNumber } from './version-number';

/**
 * An **additive** correction: a later version supersedes a segment with a
 * replacement segment, without ever mutating or removing the original. The
 * superseded segment (and every `EvidenceRef` to it) keeps resolving to its
 * original immutable text; consumers may follow the mapping forward if they want
 * the corrected wording. This is how corrections coexist with immutability (T4,
 * T5).
 */
export interface SegmentCorrection {
  readonly supersededSegmentId: SegmentId;
  readonly replacementSegmentId: SegmentId;
  readonly introducedInVersion: VersionNumber;
}
