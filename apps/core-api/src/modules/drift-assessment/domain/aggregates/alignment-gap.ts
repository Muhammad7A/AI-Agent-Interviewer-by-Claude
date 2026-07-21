import type { OrganizationId, EngagementId, EvidenceRef, ValidationRecord } from '@oi/contracts';
import type { AlignmentGapId, DriftAssessmentId } from '../value-objects/ids';
import type { DriftCategory } from '../value-objects/drift-category';
import type { OfficialElementRef, DiscoveredElementRef, ComparisonSide } from '../value-objects/refs';
import type { GapSeverity } from '../value-objects/gap-scales';
import type { RiskAssessment } from '../value-objects/risk';

/**
 * **Aggregate Root.** A *one-sided* gap: something exists on one side with no
 * counterpart on the other — Shadow Organization / Shadow Leadership (discovered,
 * no official), Capability Gap / Governance Gap (official, no discovered),
 * Ownership Ambiguity.
 *
 * `missingSide` says which side is absent: when `'Discovered'`, `official` is
 * present and `discovered` is absent; when `'Official'`, the reverse. Unlike a
 * `DriftFinding` (which pairs both sides), a gap intrinsically has only one.
 *
 * Invariants: carries ≥1 traceable `EvidenceRef` (DRIFT4) and an `explanation`
 * (DRIFT5); AI proposes, domain validates.
 */
export interface AlignmentGap {
  readonly id: AlignmentGapId;
  readonly assessmentId: DriftAssessmentId;
  readonly organizationId: OrganizationId;
  readonly engagementId: EngagementId;
  readonly category: DriftCategory;
  readonly missingSide: ComparisonSide;
  readonly official?: OfficialElementRef;
  readonly discovered?: DiscoveredElementRef;
  readonly severity: GapSeverity;
  readonly risk: RiskAssessment;
  readonly evidence: readonly EvidenceRef[];
  readonly explanation: string;
  readonly validation: ValidationRecord;
}
