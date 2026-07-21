import type { TenantId, EngagementId, KnowledgeEdgeId, KnowledgeNodeId, Layer } from '@oi/contracts';
import type { KnowledgeEdgeType } from '../edges/edge-type';
import type { AnyKnowledgeEdge } from '../edges';

/**
 * **Repository port** for `KnowledgeEdge` aggregates. Edges are traversed from
 * their endpoint nodes (referenced by identity). Tenant + engagement scoped by
 * contract. Implementations are infrastructure, not defined here.
 */
export interface KnowledgeEdgeRepository {
  findById(
    tenantId: TenantId,
    engagementId: EngagementId,
    id: KnowledgeEdgeId,
  ): Promise<AnyKnowledgeEdge | null>;

  save(edge: AnyKnowledgeEdge): Promise<void>;

  outgoing(nodeId: KnowledgeNodeId, edgeType?: KnowledgeEdgeType): Promise<readonly AnyKnowledgeEdge[]>;

  incoming(nodeId: KnowledgeNodeId, edgeType?: KnowledgeEdgeType): Promise<readonly AnyKnowledgeEdge[]>;

  /** A lens: all edges participating in a given layer. */
  findByLayer(engagementId: EngagementId, layer: Layer): Promise<readonly AnyKnowledgeEdge[]>;

  nextIdentity(): KnowledgeEdgeId;
}
