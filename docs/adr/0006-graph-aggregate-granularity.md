# 6. Graph aggregate granularity and consistency

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

The unified knowledge graph (ADR-0004, ADR-0005) can grow to many thousands of
nodes and edges per engagement. We must decide the DDD aggregate boundary: is the
graph one large aggregate, or is each node/edge its own aggregate? This
determines transaction boundaries, concurrency, and the consistency model for
graph-wide operations (resolution, detection, recompute).

A single graph-sized aggregate would serialize all writes and load enormous
object trees per transaction — unworkable. It also contradicts the DDD guidance
to keep aggregates small.

## Decision

**Each `KnowledgeNode` and each `KnowledgeEdge` is its own Aggregate Root.**

- The transactional consistency boundary is the individual node or edge.
- An edge references its endpoint nodes **by identity** (`KnowledgeNodeId`), never
  by object containment — the standard rule that aggregates reference other
  aggregates by ID only.
- **Graph-wide operations are eventually consistent.** Resolution, construction,
  detection, and recompute operate across many aggregates via domain events and
  idempotent, re-runnable stages — they do not require a single serializable
  transaction over the whole graph.
- Endpoint integrity (invariant N3) and evidence-first (N1) are enforced per
  aggregate at write time; cross-aggregate consistency (e.g. a dangling edge
  after a node merge) is reconciled through events, not locks.

## Consequences

**Positive**

- Small, independently writable aggregates; high write concurrency.
- Matches the incremental, re-runnable pipeline — new interviews mutate a few
  aggregates, not the whole graph.
- Faithful to DDD aggregate-sizing guidance.

**Negative / costs**

- Graph-wide invariants are eventually consistent, not immediate; transient
  states (e.g. an edge briefly pointing at a just-superseded node) are possible
  and must be reconciled by event handlers.
- Multi-node operations need saga/process-manager style coordination later, not
  a single transaction.

## Related

- One graph & lenses: ADR-0004. Ownership: ADR-0005. Tenancy scope: ADR-0003.
- Invariants N1–N5: `docs/DOMAIN_MODEL.md` §3.5.
