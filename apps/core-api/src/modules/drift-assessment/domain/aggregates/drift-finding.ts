import type { OrganizationId, EngagementId, EvidenceRef, ValidationRecord } from '@oi/contracts';
import type { DriftFindingId, DriftAssessmentId, MappingHypothesisId } from '../value-objects/ids';
import type { DriftCategory } from '../value-objects/drift-category';
import type { OfficialElementRef, DiscoveredElementRef } from '../value-objects/refs';
import type { DriftScore } from '../value-objects/scores';
import type { GapSeverity, GapFrequency } from '../value-objects/gap-scales';
import type { RiskAssessment } from '../value-objects/risk';

/**
 * **Aggregate Root.** A detected drift between a *matched* official/discovered
 * pair (both exist but diverge) — e.g. Process/Role/Reporting/Approval/Workflow
 * Drift, SOP Deviation, Organizational Misalignment.
 *
 * Invariants:
 *  - DRIFT1: references **both** an official artifact and a discovered artifact.
 *  - DRIFT4: carries ≥1 traceable `EvidenceRef` (resolvable via Transcript).
 *  - DRIFT5: has a human-readable `explanation` (must be explainable).
 *  - AI proposes: enters with `validation.state = 'Proposed'`; only validated
 *    findings are authoritative.
 *
 * `basedOnMappingId` records which identity mapping the pairing rests on, so a
 * finding built on a probabilistic mapping stays honest about its foundation.
 */
export interface DriftFinding {
  readonly id: DriftFindingId;
  readonly assessmentId: DriftAssessmentId;
  readonly organizationId: OrganizationId;
  readonly engagementId: EngagementId;
  readonly category: DriftCategory;
  readonly official: OfficialElementRef;
  readonly discovered: DiscoveredElementRef;
  readonly driftScore: DriftScore;
  readonly severity: GapSeverity;
  readonly frequency: GapFrequency;
  readonly risk: RiskAssessment;
  readonly basedOnMappingId?: MappingHypothesisId;
  readonly evidence: readonly EvidenceRef[];
  readonly explanation: string;
  readonly validation: ValidationRecord;
}
