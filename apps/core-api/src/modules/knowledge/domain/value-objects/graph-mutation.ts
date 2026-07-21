import type { KnowledgeNodeId, KnowledgeEdgeId } from '@oi/contracts';

/**
 * A node supersession produced by resolution/merge. Preserves identity: the
 * surviving node absorbs the superseded node's evidence (invariant K1).
 */
export interface NodeMerge {
  readonly supersededId: KnowledgeNodeId;
  readonly survivingId: KnowledgeNodeId;
}

/**
 * The plan produced by `GraphConstructionService` for a batch of resolved claims:
 * the intended node/edge additions and merges. A value object — a *description*
 * of intended mutations, not their execution (execution is an application concern
 * outside this contracts-only package).
 */
export interface GraphMutation {
  readonly addedNodeIds: readonly KnowledgeNodeId[];
  readonly addedEdgeIds: readonly KnowledgeEdgeId[];
  readonly merges: readonly NodeMerge[];
}
