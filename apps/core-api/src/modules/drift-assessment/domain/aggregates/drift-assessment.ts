import type { OrganizationId, EngagementId } from '@oi/contracts';
import type { DriftAssessmentId } from '../value-objects/ids';
import type { BaselineVersionRef, ComparisonWindow } from '../value-objects/assessment-vos';
import type { AlignmentScore, MaturityScore, ReadinessScore } from '../value-objects/scores';

/** The lifecycle of a drift assessment run. */
export type AssessmentStatus = 'Draft' | 'Running' | 'Completed' | 'Superseded';

/**
 * **Aggregate Root.** One comparison run: it compares the discovered reality of
 * an engagement against a pinned official baseline over a time window, and rolls
 * up organization-level scores. Findings, gaps, and mappings reference it by id.
 *
 * Invariants: carries a `baseline` (DRIFT2) and cannot compare incompatible
 * scopes — its `organizationId`/`engagementId` must match the baseline's
 * organization (DRIFT6).
 */
export interface DriftAssessment {
  readonly id: DriftAssessmentId;
  readonly organizationId: OrganizationId;
  readonly engagementId: EngagementId;
  readonly baseline: BaselineVersionRef;
  readonly window: ComparisonWindow;
  readonly status: AssessmentStatus;
  readonly overallAlignment?: AlignmentScore;
  readonly maturity?: MaturityScore;
  readonly readiness?: ReadinessScore;
}
