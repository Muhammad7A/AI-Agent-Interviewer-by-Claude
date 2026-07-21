import type { InvariantSpec } from '@oi/contracts';
import type { TranscriptInvariantCode } from './invariant-code';

/**
 * The Transcript context's invariant registry — declarative data, not logic —
 * reusing the Shared Kernel's generic `InvariantSpec` (no duplication). Together
 * these guarantee that `EvidenceRef` resolution is deterministic and stable for
 * the lifetime of the platform.
 */
export const TRANSCRIPT_INVARIANTS = {
  T1: {
    code: 'T1',
    name: 'Finalized immutability',
    statement:
      'A finalized transcript version is immutable: the ids, text, spans, order and speaker of its segments never change.',
    appliesTo: ['Transcript', 'TranscriptVersion', 'TranscriptSegment'],
  },
  T2: {
    code: 'T2',
    name: 'Stable segment identity and content',
    statement:
      'A segment id and its text are fixed at creation and stable forever; every EvidenceRef depends on this.',
    appliesTo: ['TranscriptSegment'],
  },
  T3: {
    code: 'T3',
    name: 'Ordered contiguous segments',
    statement: 'Segments carry stable, ordered, contiguous sequence numbers within a transcript.',
    appliesTo: ['TranscriptSegment', 'Transcript'],
  },
  T4: {
    code: 'T4',
    name: 'Append-only after finalization',
    statement:
      'After finalization no existing segment is mutated or removed; new content is added only as new segments in a new version.',
    appliesTo: ['Transcript', 'TranscriptSegment'],
  },
  T5: {
    code: 'T5',
    name: 'Additive monotonic versioning',
    statement:
      "Each version's segment set is a superset of the prior version's and version numbers strictly increase; corrections are additive replacements recorded in `corrections`, never in-place edits.",
    appliesTo: ['TranscriptVersion', 'SegmentCorrection'],
  },
  T6: {
    code: 'T6',
    name: 'Deterministic span resolution',
    statement:
      'For any EvidenceRef, its CharSpan [start, end) satisfies 0 <= start <= end <= length(segment.text) and resolves to exactly one substring of the immutable segment.',
    appliesTo: ['TranscriptSegment', 'EvidenceRef', 'CharSpan'],
  },
  T7: {
    code: 'T7',
    name: 'Tenant and engagement scope',
    statement: 'Every transcript is scoped to a TenantId and EngagementId; no transcript is unscoped.',
    appliesTo: ['Transcript'],
  },
  T8: {
    code: 'T8',
    name: 'Speaker reference integrity',
    statement: "A segment's speakerId references a Speaker defined within the same transcript.",
    appliesTo: ['TranscriptSegment', 'Speaker'],
  },
} as const satisfies Record<TranscriptInvariantCode, InvariantSpec<TranscriptInvariantCode>>;
