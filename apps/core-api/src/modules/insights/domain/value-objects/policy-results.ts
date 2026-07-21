import type { KnowledgeNodeId } from '@oi/contracts';
import type { OpportunityScore } from './opportunity-score';
import type { RecommendationPriority } from './recommendation-priority';

/** The decision produced by `PainDeduplicationPolicy` for a group of duplicates. */
export interface PainMergeDecision {
  readonly survivingId: KnowledgeNodeId;
  readonly duplicateIds: readonly KnowledgeNodeId[];
}

/** An opportunity with its computed rank, produced by `OpportunityRankingPolicy`. */
export interface RankedOpportunity {
  readonly opportunityId: KnowledgeNodeId;
  readonly rank: number;
  readonly score: OpportunityScore;
}

/** A recommendation with its computed priority, produced by `RecommendationPrioritizationPolicy`. */
export interface PrioritizedRecommendation {
  readonly recommendationId: KnowledgeNodeId;
  readonly rank: number;
  readonly priority: RecommendationPriority;
}
