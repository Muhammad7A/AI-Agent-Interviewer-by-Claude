# 5. DDD context map and unified-graph ownership

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

We are laying down the tactical DDD skeleton (`docs/DOMAIN_MODEL.md`). Two
strategic questions had to be settled first, because they shape every aggregate:

1. **How are the bounded contexts related** (subdomain classification + context
   map patterns)?
2. **Who owns the unified knowledge graph?** ADR-0004 mandates "one graph, six
   lenses." But Insights owns pain points and Knowledge owns the graph — if both
   store nodes, the single graph fractures. This had to be reconciled without
   weakening either the one-graph principle or context sovereignty.

## Decision

**Subdomains:** Core = Knowledge, Insights. Supporting = Transcript, Interview
Orchestration, Invitations, Reporting, Consultant Workspace. Generic = Identity &
Access, Organization, Administration. `ai-engine` is a separate context reached
only via Published Language + an Anti-Corruption Layer.

**Graph ownership — physically one graph, logically owned per layer:**

- A **Shared Kernel** owns the *base* `KnowledgeNode`/`KnowledgeEdge` contracts,
  the `Layer` taxonomy, the substrate repository ports, the `KnowledgeGraphLens`
  read model, and the evidence/confidence/validation value objects. This is the
  single physical graph and the uniform evidence-first invariant.
- Each **core context owns the node/edge _types_** (catalog + sealed attributes +
  invariants + lifecycle) for its layer(s): Knowledge owns Structural/Capability/
  Operational; Insights owns Diagnostic/Opportunity/Synthesis.
- Insights authors its nodes into the *same* store through the shared substrate
  ports. It does **not** run a second graph.

A "lens" is therefore a `findByLayer` query over one store; cross-layer reasoning
is a graph traversal; provenance is unified under one evidence spine.

**Cross-runtime boundary:** `ai-engine` capabilities appear to `core-api` as
domain-service ports implemented by ACL adapters. Proposals are DTOs; they become
domain objects only after the evidence-first invariant is validated at the
boundary.

## Consequences

**Positive**

- "One graph, six lenses" (ADR-0004) survives context decomposition — physically
  unified, cross-layer-queryable, one provenance spine.
- Each context keeps sovereignty over its types' invariants and lifecycle.
- Evidence-first is enforced uniformly (shared kernel + factories + ACL).

**Negative / costs**

- A shared kernel couples the core contexts; changes to the substrate require
  their agreement. Accepted deliberately — the alternative (duplicated graph
  models) fractures the graph.
- One physical graph store is a shared dependency of Knowledge and Insights;
  their independent scaling is constrained (no driver to split today).

## Related

- One-graph principle: ADR-0004. Layering: ADR-0002. Tenancy: ADR-0003. Runtime
  split & ACL boundary: ADR-0001. Full skeleton: `docs/DOMAIN_MODEL.md`.
