import type { AlignmentGap } from '../aggregates/alignment-gap';
import type { AlignmentGapId, DriftAssessmentId } from '../value-objects/ids';
import type { DriftCategory } from '../value-objects/drift-category';

/** **Repository port** for `AlignmentGap` aggregates. */
export interface AlignmentGapRepository {
  findById(id: AlignmentGapId): Promise<AlignmentGap | null>;
  save(gap: AlignmentGap): Promise<void>;
  findByAssessment(assessmentId: DriftAssessmentId): Promise<readonly AlignmentGap[]>;
  findByCategory(assessmentId: DriftAssessmentId, category: DriftCategory): Promise<readonly AlignmentGap[]>;
  nextIdentity(): AlignmentGapId;
}
