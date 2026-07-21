import type { NodeAttributes, KnowledgeNode, KnowledgeNodeId } from '@oi/contracts';
import type { RecommendationPriority } from '../../value-objects/recommendation-priority';

/**
 * A coherent grouping of related recommendations delivered together (e.g. a
 * quarter's programme of work). A `KnowledgeNode` in the Synthesis layer.
 *
 * Invariant: `memberRecommendationIds` has ≥1 entry (no orphan bundle, INS6).
 */
export interface RecommendationBundleAttributes extends NodeAttributes<'RecommendationBundle'> {
  readonly theme: string;
  readonly memberRecommendationIds: readonly KnowledgeNodeId[];
  readonly bundlePriority: RecommendationPriority;
}

export type RecommendationBundle = KnowledgeNode<RecommendationBundleAttributes>;
