import type { KnowledgeNode, KnowledgeEdge, Evidence } from '@oi/contracts';

/**
 * A materialized slice of the unified graph returned by a lens query. Because all
 * node/edge types conform to the Shared Kernel base contracts, one `SubGraph`
 * shape spans every layer (ADR-0004/0005).
 */
export interface SubGraph {
  readonly nodes: readonly KnowledgeNode[];
  readonly edges: readonly KnowledgeEdge[];
}

/** An ordered path through the graph: alternating nodes and the edges between them. */
export interface Path {
  readonly nodes: readonly KnowledgeNode[];
  readonly edges: readonly KnowledgeEdge[];
}

/**
 * A provenance tree: a piece of evidence and the evidence it derives from,
 * resolving transitively to stated transcript segments (invariant E1). This is
 * the drill-path that makes every insight auditable.
 */
export interface EvidenceTree {
  readonly evidence: Evidence;
  readonly inputs: readonly EvidenceTree[];
}
