/**
 * The lifecycle status of a transcript.
 *  - `Draft`: being captured; segments may still be appended freely.
 *  - `Finalized`: immutable. Further content is added only via a new
 *    `TranscriptVersion` (append-only; T4).
 */
export type TranscriptStatus = 'Draft' | 'Finalized';
