import type { Brand } from '@oi/contracts';

/**
 * Insights-context identities for the non-graph aggregates and entities. They
 * reuse the Shared Kernel's `Brand` primitive (no duplication). The graph-node
 * aggregates (PainPoint, Opportunity, Recommendation, DiagnosticCluster,
 * RecommendationBundle) are `KnowledgeNode`s and are identified by the Shared
 * Kernel's `KnowledgeNodeId`.
 */

/** Identity of an `Observation` aggregate. */
export type ObservationId = Brand<string, 'ObservationId'>;

/** Identity of a `Finding` aggregate. */
export type FindingId = Brand<string, 'FindingId'>;

/** Identity of a `RootCauseHypothesis` entity. */
export type RootCauseId = Brand<string, 'RootCauseId'>;

/** Identity of a `RecommendationConflict` entity. */
export type ConflictId = Brand<string, 'ConflictId'>;
