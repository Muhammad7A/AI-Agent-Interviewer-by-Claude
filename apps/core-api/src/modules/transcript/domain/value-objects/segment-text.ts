import type { Brand } from '@oi/contracts';

/**
 * The immutable verbatim text of a segment. `CharSpan`s carried by `EvidenceRef`s
 * index into this string as `[start, end)` with `0 <= start <= end <= length`.
 * Fixed at segment creation and never mutated (T1, T2, T4) — this immutability is
 * what makes evidence resolution deterministic.
 */
export type SegmentText = Brand<string, 'SegmentText'>;
