export * from './claim';

/**
 * Note: the Knowledge context's other Aggregate Roots — `KnowledgeNode` and
 * `KnowledgeEdge` — are the Shared Kernel base contracts, specialized per type
 * under `../nodes` and `../edges` (ADR-0006: each node/edge is its own root).
 * They are not redefined here (no duplication); `Claim` is the aggregate unique
 * to this context.
 */
