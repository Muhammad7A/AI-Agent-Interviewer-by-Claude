import type { TranscriptId, TenantId, EngagementId } from '@oi/contracts';
import type { TranscriptSegment } from '../entities/transcript-segment';
import type { Speaker } from '../entities/speaker';
import type { Recording } from '../entities/recording';
import type { TranscriptStatus } from '../value-objects/transcript-status';
import type { TranscriptVersion } from '../value-objects/transcript-version';
import type { SegmentCorrection } from '../value-objects/segment-correction';
import type { VersionNumber } from '../value-objects/version-number';

/**
 * **Aggregate Root.** The append-only record of an interview and the canonical
 * evidence store. Scoped to tenant + engagement.
 *
 * Lifecycle: `Draft` (segments captured) → `Finalized` (immutable). After
 * finalization the transcript is **append-only**: further content is added only
 * by creating a new `TranscriptVersion` that carries every existing segment
 * unchanged and appends new ones (T4, T5). Corrections are additive
 * (`corrections`), never in-place edits. Because segment ids and content are
 * preserved forever (T1, T2), existing `EvidenceRef`s always keep resolving.
 *
 * State contract only — behaviour (open, appendSegment, finalize, appendVersion,
 * correct) lives in the application layer, which is out of scope here.
 */
export interface Transcript {
  readonly id: TranscriptId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly recording: Recording;
  readonly status: TranscriptStatus;
  readonly currentVersion: VersionNumber;
  readonly speakers: readonly Speaker[];
  readonly segments: readonly TranscriptSegment[];
  readonly versions: readonly TranscriptVersion[];
  readonly corrections: readonly SegmentCorrection[];
}
