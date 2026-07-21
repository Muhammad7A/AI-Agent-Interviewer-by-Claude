import type { IntervieweeRef, RoleLabel, DepartmentLabel } from '@oi/contracts';
import type { SpeakerId } from '../value-objects/ids';
import type { SpeakerLabel } from '../value-objects/speaker-label';

/**
 * **Entity.** A speaker within a transcript. `label` is the diarization label
 * (e.g. "Speaker 1"); once identified, `intervieweeRef` (pseudonymized, never
 * PII) with `role`/`department` resolves who it is.
 *
 * These fields project directly onto the Shared Kernel `SourcePerspective`
 * carried by `EvidenceRef.speaker` — the same primitives, so evidence attributed
 * here aligns with the evidence spine without any duplication.
 */
export interface Speaker {
  readonly id: SpeakerId;
  readonly label: SpeakerLabel;
  readonly intervieweeRef?: IntervieweeRef;
  readonly role?: RoleLabel;
  readonly department?: DepartmentLabel;
}
