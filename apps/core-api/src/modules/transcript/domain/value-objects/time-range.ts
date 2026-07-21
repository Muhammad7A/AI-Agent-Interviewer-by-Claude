/**
 * A time range within the recording, in milliseconds from its start. Optional
 * capture metadata — it plays **no** part in evidence resolution, which keys on
 * the segment's text `CharSpan`, not time.
 */
export interface TimeRange {
  readonly startMs: number;
  readonly endMs: number;
}
