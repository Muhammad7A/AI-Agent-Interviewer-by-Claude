# 7. Engagement lives in the Organization bounded context

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

The knowledge graph is scoped per `Engagement` (a Discovery & Assessment
project). `EngagementId` is a scope key carried by nearly every artifact in the
system. We must decide which bounded context owns the `Engagement` aggregate: the
Organization context, or a dedicated Engagement context.

An `Engagement` is intrinsically tied to the client `Organization` (tenant): it
belongs to exactly one org, shares its lifecycle governance, and sits alongside
the org's official structure and directory. Its lifecycle (Draft → Active →
Ingesting → Frozen → Closed) is administrative, not part of the core reasoning
domain.

## Decision

**`Engagement` is an Aggregate Root inside the Organization bounded context**,
alongside `Organization`, `OrgUnit`, and `Employee`. Other contexts reference it
by `EngagementId` only (Published Language), never by object reference.

`EngagementId` and `TenantId` are the Organization context's Published Language
to the rest of the platform — the scope keys every other context conforms to.

## Consequences

**Positive**

- No thin, artificial context for what is an administrative aggregate.
- Engagement sits next to the official org structure it contextualizes,
  reinforcing the "official vs. discovered" contrast that feeds Insights.
- One clear owner of engagement lifecycle and scope issuance.

**Negative / costs**

- The Organization context carries an extra aggregate and lifecycle. Acceptable —
  it is generic/administrative work, not core-domain complexity.
- If engagements later grow rich, cross-org behaviour (e.g. multi-engagement
  benchmarking), this may warrant a future split — a new ADR would supersede this.

## Related

- Graph scope: `docs/ORGANIZATIONAL_INTELLIGENCE_ENGINE.md` §1.
- Organization context model: `docs/DOMAIN_MODEL.md` §7.6.
