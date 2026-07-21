import type { Recommendation } from '../nodes/synthesis/recommendation';
import type { PrioritizationWeights } from '../value-objects/recommendation-priority';
import type { PrioritizedRecommendation } from '../value-objects/policy-results';

/**
 * **Domain service (port).** Prioritizes recommendations using tunable
 * `PrioritizationWeights` (the Strategy a firm sets per engagement) — impact vs.
 * complexity vs. urgency vs. risk. Interface only.
 */
export interface RecommendationPrioritizationPolicy {
  prioritize(
    recommendations: readonly Recommendation[],
    weights: PrioritizationWeights,
  ): readonly PrioritizedRecommendation[];
}
