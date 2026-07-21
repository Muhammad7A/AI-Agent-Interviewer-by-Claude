import type { ReconciliationCandidateId } from '../value-objects/ids';
import type { OfficialElementRef } from '../value-objects/refs';
import type { ConfidenceOfMatch } from '../value-objects/confidence';

/** Whether a candidate has been accepted, rejected, or is still open within a resolution. */
export type CandidateStatus = 'Proposed' | 'Accepted' | 'Rejected';

/**
 * **Entity** within an `IdentityResolution`. One ranked candidate official match
 * for a discovered element, with its match confidence and rationale. Has a local
 * identity and a lifecycle (proposed → accepted/rejected), which is what makes it
 * an entity rather than a value object.
 */
export interface ReconciliationCandidate {
  readonly id: ReconciliationCandidateId;
  readonly official: OfficialElementRef;
  readonly confidence: ConfidenceOfMatch;
  readonly rationale: string;
  readonly status: CandidateStatus;
}
