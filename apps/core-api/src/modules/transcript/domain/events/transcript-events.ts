import type { DomainEvent, TranscriptId, SegmentId } from '@oi/contracts';
import type { SpeakerId } from '../value-objects/ids';
import type { VersionNumber } from '../value-objects/version-number';

/** Transcript-context domain events, all extending the Shared Kernel `DomainEvent` envelope. */

export type TranscriptOpened = DomainEvent<
  'transcript.opened',
  { readonly transcriptId: TranscriptId }
>;

export type SegmentAppended = DomainEvent<
  'transcript.segment.appended',
  { readonly transcriptId: TranscriptId; readonly segmentId: SegmentId }
>;

export type SpeakerIdentified = DomainEvent<
  'transcript.speaker.identified',
  { readonly transcriptId: TranscriptId; readonly speakerId: SpeakerId }
>;

export type TranscriptFinalized = DomainEvent<
  'transcript.finalized',
  { readonly transcriptId: TranscriptId; readonly versionNumber: VersionNumber }
>;

/** A new immutable version appended after finalization (append-only; T4/T5). */
export type TranscriptVersionAppended = DomainEvent<
  'transcript.version.appended',
  {
    readonly transcriptId: TranscriptId;
    readonly versionNumber: VersionNumber;
    readonly addedSegmentIds: readonly SegmentId[];
  }
>;

/** Discriminated union of the Transcript context's domain events. */
export type TranscriptDomainEvent =
  | TranscriptOpened
  | SegmentAppended
  | SpeakerIdentified
  | TranscriptFinalized
  | TranscriptVersionAppended;
