import type { KnowledgeEdgeId, KnowledgeNodeId, TenantId, EngagementId } from '../primitives/ids';
import type { Evidence } from '../provenance/evidence';
import type { Confidence } from '../confidence/confidence';
import type { ValidationRecord } from '../validation/validation-record';
import type { Layer } from './layer';
import type { EdgeType } from './edge-type';
import type { EdgeAttributes } from './edge-attributes';

/**
 * The base structural contract for every relationship in the unified graph.
 *
 * Edges are **first-class and evidence-bearing** — a relationship is a claim
 * about the world just as a node is, so it carries its own evidence, confidence
 * and validation. Endpoints are referenced **by identity only**
 * (`KnowledgeNodeId`): an edge never contains its nodes — the standard aggregate
 * rule (ADR-0006).
 *
 * Invariants encoded by this contract:
 *  - N1 / G1 evidence-first: `evidence` is non-empty.
 *  - N2 / G3 scope: `tenantId` and `engagementId` are always present.
 *  - N3 endpoint integrity: `sourceId` and `targetId` resolve to nodes in the
 *    same engagement.
 */
export interface KnowledgeEdge<TAttributes extends EdgeAttributes = EdgeAttributes> {
  readonly id: KnowledgeEdgeId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly edgeType: EdgeType;
  readonly layers: readonly Layer[];
  readonly sourceId: KnowledgeNodeId;
  readonly targetId: KnowledgeNodeId;
  readonly attributes: TAttributes;
  readonly evidence: readonly Evidence[];
  readonly confidence: Confidence;
  readonly validation: ValidationRecord;
}
