/**
 * Transcript context — **Published Language** (Open-Host Service surface).
 *
 * Transcript is upstream of the whole evidence spine. What it publishes is the
 * *immutable segment* and the means to resolve an `EvidenceRef` to it — nothing
 * about how transcripts are captured or stored. Consumers (ai-engine extraction,
 * Knowledge, Insights, Reporting) depend only on this surface.
 *
 * The aggregate root, the repository, and the domain events are internals and
 * are deliberately excluded.
 */

// The immutable evidence anchors (read shapes).
export type { TranscriptSegment } from './entities/transcript-segment';
export type { Speaker } from './entities/speaker';
export type { TranscriptVersion } from './value-objects/transcript-version';
export type { SegmentCorrection } from './value-objects/segment-correction';

// Supporting value objects.
export type { SegmentText } from './value-objects/segment-text';
export type { TimeRange } from './value-objects/time-range';
export type { VersionNumber } from './value-objects/version-number';
export type { TranscriptStatus } from './value-objects/transcript-status';
export type { RecordingMedium } from './value-objects/recording-medium';

// Identifiers + span — reused from the Shared Kernel, re-exported so consumers
// have one import surface for evidence addressing.
export type { CharSpan } from './value-objects/char-span';
export type { TranscriptId, SegmentId } from './value-objects/ids';

// Deterministic EvidenceRef resolution (requirement #1).
export type { TranscriptSegmentResolver, ResolvedEvidence } from './repositories/transcript-segment-resolver';
