import type { OrganizationId, EngagementId } from '@oi/contracts';
import type { DriftAssessment } from '../aggregates/drift-assessment';
import type { DriftAssessmentId } from '../value-objects/ids';

/**
 * **Repository port** for `DriftAssessment` aggregates. `findHistory` keeps
 * historical assessments queryable (DRIFT7). Implementations are infrastructure.
 */
export interface DriftAssessmentRepository {
  findById(id: DriftAssessmentId): Promise<DriftAssessment | null>;
  save(assessment: DriftAssessment): Promise<void>;
  findByEngagement(engagementId: EngagementId): Promise<readonly DriftAssessment[]>;
  findHistory(organizationId: OrganizationId): Promise<readonly DriftAssessment[]>;
  nextIdentity(): DriftAssessmentId;
}
