# 3. Multi-tenancy: shared database, row-level scoping

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

This is a B2B platform. Each client organization is a tenant, and its
organizational data (interviews, transcripts, knowledge, insights) must be
strictly isolated from every other tenant. We must choose an isolation model
early because it touches the data model, the repository layer, and the security
posture of the whole system.

Options considered:

- **Shared DB, row-level scoping** — one database; every tenant-owned row carries
  `tenant_id`, enforced at the repository layer. Simplest to operate, migrate,
  and scale early. Isolation depends on disciplined, guarded query scoping.
- **Schema-per-tenant** — stronger isolation, but heavier migration/ops burden as
  tenant count grows.
- **Database-per-tenant** — strongest physical isolation and compliance story,
  highest operational cost. Premature at Discovery stage.

## Decision

Use a **shared database with row-level tenant scoping**:

1. Every tenant-owned aggregate carries a `TenantId`, modeled as a **value
   object** in the domain (not an incidental column).
2. Tenant context is resolved **once**, at the edge of `core-api` (auth →
   request-scoped `TenantContext`), then propagated through the application
   layer.
3. A **base repository / query guard in infrastructure structurally guarantees
   no query escapes tenant scope.** It must be impossible to write an unscoped
   query through the sanctioned repository path — isolation cannot depend on a
   developer remembering to add a filter.
4. `ai-engine` never resolves tenancy; it receives already-scoped context and
   returns results tagged with the same scope for `core-api` to persist.

## Consequences

**Positive**

- Simplest to operate, migrate, and scale at Discovery stage.
- Cross-tenant leakage has exactly one possible origin (the repository layer),
  and that origin is guarded and testable.
- Migration to schema- or database-per-tenant later is possible because tenancy
  is already an explicit, first-class concept in the model.

**Negative / costs**

- Isolation is logical, not physical — a defect in the guard is a cross-tenant
  risk. This is mitigated by making the guard the _only_ sanctioned query path
  and covering it with dedicated tests.
- Clients requiring physical data isolation for compliance would need a future
  ADR revisiting this (schema- or DB-per-tenant for those tenants).

## Related

- Tenancy rules: `docs/ARCHITECTURE.md` §5.
