/**
 * Knowledge bounded context — domain layer (contracts only).
 *
 * The full internal surface: value objects, node/edge type contracts,
 * aggregates, entities, repository ports, domain-service policies, domain
 * events, and invariants. The curated external surface is
 * `./published-language`.
 *
 * Every contract here extends the Shared Kernel (`@oi/contracts`) without
 * duplication. No behaviour, persistence, infrastructure, application services,
 * or presentation appears in this layer.
 */
export * from './value-objects';
export * from './nodes';
export * from './edges';
export * from './aggregates';
export * from './entities';
export * from './repositories';
export * from './services';
export * from './events';
export * from './invariants';
