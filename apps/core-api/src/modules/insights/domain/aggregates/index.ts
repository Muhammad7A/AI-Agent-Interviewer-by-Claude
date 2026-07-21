export * from './observation';
export * from './finding';

/**
 * Note: the Insights context's other Aggregate Roots — `PainPoint`,
 * `DiagnosticCluster`, `Opportunity`, `Recommendation`, `RecommendationBundle` —
 * are `KnowledgeNode` specializations (each its own root per ADR-0006) and live
 * under `../nodes`. `Observation` and `Finding` are the non-graph interpretation
 * aggregates unique to this context.
 */
