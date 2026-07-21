/**
 * A half-open character range `[start, end)` within a transcript segment.
 *
 * Invariant (span): `0 <= start <= end`. Enforced by the Transcript context's
 * factories — the contract fixes only the shape.
 */
export interface CharSpan {
  readonly start: number;
  readonly end: number;
}
