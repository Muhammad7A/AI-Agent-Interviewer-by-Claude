import type { DriftFinding } from '../aggregates/drift-finding';
import type { DriftFindingId, DriftAssessmentId } from '../value-objects/ids';
import type { DriftCategory } from '../value-objects/drift-category';

/** **Repository port** for `DriftFinding` aggregates. */
export interface DriftFindingRepository {
  findById(id: DriftFindingId): Promise<DriftFinding | null>;
  save(finding: DriftFinding): Promise<void>;
  findByAssessment(assessmentId: DriftAssessmentId): Promise<readonly DriftFinding[]>;
  findByCategory(assessmentId: DriftAssessmentId, category: DriftCategory): Promise<readonly DriftFinding[]>;
  nextIdentity(): DriftFindingId;
}
