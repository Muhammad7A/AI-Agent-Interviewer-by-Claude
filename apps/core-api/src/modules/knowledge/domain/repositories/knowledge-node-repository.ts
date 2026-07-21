import type { TenantId, EngagementId, KnowledgeNodeId, Layer } from '@oi/contracts';
import type { KnowledgeNodeType } from '../nodes/node-type';
import type { AnyKnowledgeNode } from '../nodes';

/**
 * **Repository port** for `KnowledgeNode` aggregates. A contract only —
 * implementations live in the infrastructure layer, which is out of scope here.
 * Every operation is tenant + engagement scoped by contract (ADR-0003); the
 * sanctioned query path cannot escape tenant scope.
 */
export interface KnowledgeNodeRepository {
  findById(
    tenantId: TenantId,
    engagementId: EngagementId,
    id: KnowledgeNodeId,
  ): Promise<AnyKnowledgeNode | null>;

  save(node: AnyKnowledgeNode): Promise<void>;

  findByType(
    engagementId: EngagementId,
    nodeType: KnowledgeNodeType,
  ): Promise<readonly AnyKnowledgeNode[]>;

  /** A lens: all nodes participating in a given layer (ADR-0004). */
  findByLayer(engagementId: EngagementId, layer: Layer): Promise<readonly AnyKnowledgeNode[]>;

  nextIdentity(): KnowledgeNodeId;
}
