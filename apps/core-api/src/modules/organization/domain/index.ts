/**
 * Organization bounded context — domain layer (contracts only).
 *
 * Represents the **declared** official structure of an organization — the source
 * of organizational *intent*. It deliberately holds no discovered facts (those
 * belong to Knowledge); the gap between the two is a primary business value.
 * Accordingly this context does **not** use the evidence/confidence/validation
 * model — official data is declared, versioned, and effective-dated.
 *
 * Depends only on the Shared Kernel (`@oi/contracts`); it consumes no other
 * context's Published Language. Ids reuse `Brand`; `OrganizationId`/`EngagementId`
 * are reused from the kernel; events reuse `DomainEvent`; invariants reuse
 * `InvariantSpec` — no duplication. No behaviour, persistence, infrastructure,
 * application services, or presentation.
 *
 * The curated external surface is `./published-language`.
 */
export * from './value-objects';
export * from './entities';
export * from './aggregates';
export * from './repositories';
export * from './services';
export * from './events';
export * from './invariants';
export * from './read-models';
