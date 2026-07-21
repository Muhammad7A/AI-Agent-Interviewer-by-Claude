/**
 * `@oi/contracts` — the Shared Kernel.
 *
 * Evidence-first provenance primitives and the one-graph substrate contracts,
 * shared by the core bounded contexts (Knowledge, Insights) and mirrored to the
 * Python `ai-engine` as Published Language. Type contracts only — this package
 * contains no domain behaviour.
 *
 * See `docs/DOMAIN_MODEL.md` §3–§4 and ADRs 0001–0007.
 */
export * from './primitives';
export * from './provenance';
export * from './confidence';
export * from './validation';
export * from './graph';
export * from './events';
export * from './invariants';
