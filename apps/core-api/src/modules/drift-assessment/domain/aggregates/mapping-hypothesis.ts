import type { OrganizationId, EngagementId, EvidenceRef, ValidationRecord } from '@oi/contracts';
import type { MappingHypothesisId } from '../value-objects/ids';
import type { OfficialElementRef, DiscoveredElementRef } from '../value-objects/refs';
import type { MappingConfidence } from '../value-objects/confidence';

/**
 * **Aggregate Root.** The core of the identity-resolution seam: a *probabilistic*
 * hypothesis that a discovered element corresponds to an official one — an
 * interviewee ↔ an employee, a role label ↔ a position, a department label ↔ a
 * department.
 *
 * It is a **hypothesis until validated**, never asserted as truth: it enters with
 * `validation.state = 'Proposed'` and becomes authoritative only when a consultant
 * validates it (AI proposes, domain validates).
 *
 * Invariants:
 *  - DRIFT3: carries a `confidence` (`MappingConfidence`).
 *  - Must remain explainable: `rationale` + traceable `evidence` (DRIFT5).
 */
export interface MappingHypothesis {
  readonly id: MappingHypothesisId;
  readonly organizationId: OrganizationId;
  readonly engagementId: EngagementId;
  readonly discovered: DiscoveredElementRef;
  readonly official: OfficialElementRef;
  readonly confidence: MappingConfidence;
  readonly rationale: string;
  readonly evidence: readonly EvidenceRef[];
  readonly validation: ValidationRecord;
}
