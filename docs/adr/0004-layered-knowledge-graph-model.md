# 4. One layered knowledge graph, not many graphs

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

The Organizational Intelligence Engine must produce several "graphs" —
Knowledge, Department, Process, Workflow, Pain Point, AI Opportunity — plus
recommendations. The obvious-but-wrong reading is to build these as separate
stores/models.

The core value of the platform is **cross-layer reasoning**: "this bottleneck, at
this handoff, between these departments, in this workflow, is addressable by this
AI opportunity." That is a single path across layers. It also demands a **single,
unified provenance spine** — every assertion in every layer must trace to the same
immutable transcript evidence.

## Decision

Model **one unified property graph** (`KnowledgeNode` + `KnowledgeEdge`), scoped
per **Engagement**. The six named graphs are **typed layers / lenses** over that
one substrate, not separate stores:

- Structural (Department) → Capability (Process) → Operational (Workflow) →
  Diagnostic (Pain Point) → Opportunity → Synthesis (Recommendation).
- A "Department Graph" is a query over structural node/edge types; a "Pain Point
  Graph" is another lens that also links into the workflow and structural layers.

Every node and edge carries three mandatory cross-cutting value objects:
`Evidence` (provenance), `Confidence` (computed, explainable, orthogonal to
validation), and `ValidationStatus` (human-in-the-loop). Edges are first-class
and evidence-bearing. Inferred insights resolve **transitively** to stated
transcript segments.

Full design: `docs/ORGANIZATIONAL_INTELLIGENCE_ENGINE.md`.

## Consequences

**Positive**

- Cross-layer reasoning is a graph traversal, not a cross-store integration.
- Provenance is unified: one evidence spine under every layer.
- New lenses are new node/edge *types*, not new databases.
- Confidence, evidence, and validation are enforced uniformly by one invariant.

**Negative / costs**

- One graph model must express many node/edge types — richer schema, needs
  disciplined typing.
- Requires a concrete graph-capable storage decision later (deferred, behind a
  port per ADR-0002); the domain model does not presuppose the engine.
- Graph-wide operations are eventually consistent (the graph is not one
  in-memory aggregate); the transactional aggregate is the individual node/edge.

## Related

- Layering & dependency rule: ADR-0002. Tenancy: ADR-0003.
- Runtime split (which stage runs where): ADR-0001.
