import type { NodeAttributes, KnowledgeNode, KnowledgeNodeId } from '@oi/contracts';
import type { RecommendationPriority } from '../../value-objects/recommendation-priority';
import type { Urgency, RiskLevel } from '../../value-objects/scales';

/**
 * A prioritized, consultant-ready intervention. A `KnowledgeNode` in the
 * Synthesis layer. It carries a full provenance chain (via the opportunities it
 * targets → pain points → findings → evidence) down to transcript segments.
 *
 * Invariant: `targetOpportunityIds` has ≥1 entry (INS3 — every recommendation
 * targets at least one opportunity; and via that chain, INS5 — it cannot exist
 * without supporting findings).
 */
export interface RecommendationAttributes extends NodeAttributes<'Recommendation'> {
  readonly title: string;
  readonly narrative: string;
  readonly targetOpportunityIds: readonly KnowledgeNodeId[];
  readonly priority: RecommendationPriority;
  readonly urgency: Urgency;
  readonly riskLevel: RiskLevel;
  readonly dependsOnRecommendationIds: readonly KnowledgeNodeId[];
}

export type Recommendation = KnowledgeNode<RecommendationAttributes>;
