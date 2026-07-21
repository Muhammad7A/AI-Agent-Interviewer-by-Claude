import type { Recommendation } from '../nodes/synthesis/recommendation';
import type { RecommendationConflict } from '../entities/recommendation-conflict';

/**
 * **Domain service (port).** Detects conflicts between recommendations —
 * resource contention, mutual exclusivity, sequencing conflicts, redundancy —
 * so prioritization and bundling can account for them. Interface only.
 */
export interface RecommendationConflictPolicy {
  detectConflicts(recommendations: readonly Recommendation[]): readonly RecommendationConflict[];
}
