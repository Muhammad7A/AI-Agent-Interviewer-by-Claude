/**
 * Knowledge context — **Published Language**.
 *
 * The curated subset of contracts that downstream contexts (Insights, Reporting,
 * Consultant Workspace) may depend on. Internal aggregates (`Claim`), the
 * `Contradiction` entity, policies, repository ports and domain events are
 * deliberately **not** part of this surface — they are the context's internals.
 *
 * Consumers depend on: the node/edge type catalogs, the typed node/edge
 * contracts, and the read-only graph lens with its read models.
 */

// Node & edge type catalogs (the lens vocabulary consumers query by).
export type {
  KnowledgeNodeType,
  StructuralNodeType,
  CapabilityNodeType,
  OperationalNodeType,
} from './nodes/node-type';
export type {
  KnowledgeEdgeType,
  StructuralEdgeType,
  CapabilityEdgeType,
  OperationalEdgeType,
} from './edges/edge-type';

// Typed node/edge contracts + their attribute and union types.
export * from './nodes';
export * from './edges';

// The read-only surface over the unified graph.
export type { KnowledgeGraphLens } from './repositories/knowledge-graph-lens';
export type { SubGraph, Path, EvidenceTree } from './value-objects/read-models';
