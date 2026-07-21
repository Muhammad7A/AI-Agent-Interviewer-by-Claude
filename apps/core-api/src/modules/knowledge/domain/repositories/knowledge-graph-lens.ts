import type { EngagementId, KnowledgeNodeId, KnowledgeEdgeId, Layer, GraphElementKind } from '@oi/contracts';
import type { SubGraph, Path, EvidenceTree } from '../value-objects/read-models';

/**
 * **Read-model port** — the "six lenses" over the one graph plus provenance
 * traversal. A lens is a query by `Layer` (ADR-0004). Read-only: it never
 * mutates the graph. This is the Knowledge context's Open-Host read surface for
 * downstream contexts (Insights, Reporting, Consultant Workspace).
 */
export interface KnowledgeGraphLens {
  /** One of the six lenses: the subgraph of nodes/edges participating in a layer. */
  lens(engagementId: EngagementId, layer: Layer): Promise<SubGraph>;

  /** The neighbourhood around a node out to a given traversal depth. */
  subgraph(root: KnowledgeNodeId, depth: number): Promise<SubGraph>;

  /** Cross-layer paths between two nodes (e.g. pain → handoff → department). */
  pathsBetween(from: KnowledgeNodeId, to: KnowledgeNodeId): Promise<readonly Path[]>;

  /** The provenance drill-path for a node/edge, resolving to stated segments (E1). */
  provenanceChain(
    targetKind: GraphElementKind,
    targetId: KnowledgeNodeId | KnowledgeEdgeId,
  ): Promise<EvidenceTree>;
}
