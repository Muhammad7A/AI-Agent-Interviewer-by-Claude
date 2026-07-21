/**
 * Insights bounded context — domain layer (contracts only).
 *
 * Insights owns **interpretation**: Observation, Finding, PainPoint, Opportunity,
 * Recommendation, DiagnosticCluster, RecommendationBundle, and prioritization. It
 * never owns truth (Knowledge does) or evidence (Transcript does). Every graph
 * node extends the Shared Kernel `KnowledgeNode`; every confidence reuses the
 * kernel `Confidence`; ids reuse `Brand`; scores reuse `Score`; events reuse
 * `DomainEvent`; invariants reuse `InvariantSpec` — no duplication.
 *
 * Dependencies are limited to the Published Language of the Shared Kernel
 * (`@oi/contracts`), Knowledge (`@oi/knowledge`), and Transcript (`@oi/transcript`).
 * No behaviour, persistence, infrastructure, application services, or presentation.
 *
 * The curated external surface is `./published-language`.
 */
export * from './value-objects';
export * from './aggregates';
export * from './entities';
export * from './nodes';
export * from './repositories';
export * from './services';
export * from './events';
export * from './invariants';
export * from './read-models';
