import type { Timestamp } from '@oi/contracts';
import type { RecordingId } from '../value-objects/ids';
import type { RecordingMedium } from '../value-objects/recording-medium';

/**
 * **Entity.** Metadata about the capture a transcript was produced from. Pure
 * metadata: no media bytes, no parsing, no transcription/extraction (all out of
 * scope for this context).
 */
export interface Recording {
  readonly id: RecordingId;
  readonly medium: RecordingMedium;
  readonly capturedAt: Timestamp;
  readonly durationMs?: number;
  readonly sourceLabel?: string;
}
