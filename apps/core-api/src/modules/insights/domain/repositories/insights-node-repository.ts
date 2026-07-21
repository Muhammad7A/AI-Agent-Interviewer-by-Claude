import type { TenantId, EngagementId, KnowledgeNodeId, Layer } from '@oi/contracts';
import type { InsightsNodeType } from '../nodes/node-type';
import type { AnyInsightsNode } from '../nodes';

/**
 * **Repository port** for the Insights graph-node aggregates (PainPoint,
 * DiagnosticCluster, Opportunity, Recommendation, RecommendationBundle). They are
 * `KnowledgeNode`s authored into the *same* unified graph (ADR-0005); at the
 * domain level this is simply the port for the Insights-owned node types.
 * Tenant + engagement scoped. Implementations are infrastructure, not here.
 */
export interface InsightsNodeRepository {
  findById(
    tenantId: TenantId,
    engagementId: EngagementId,
    id: KnowledgeNodeId,
  ): Promise<AnyInsightsNode | null>;

  save(node: AnyInsightsNode): Promise<void>;

  findByType(engagementId: EngagementId, nodeType: InsightsNodeType): Promise<readonly AnyInsightsNode[]>;

  /** A lens over the Insights layers (Diagnostic / Opportunity / Synthesis). */
  findByLayer(engagementId: EngagementId, layer: Layer): Promise<readonly AnyInsightsNode[]>;

  nextIdentity(): KnowledgeNodeId;
}
