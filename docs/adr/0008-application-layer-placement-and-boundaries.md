# 8. Application layer placement and boundaries

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

The platform's first real use cases (StartTranscriptAnalysis, BuildKnowledgeGraph,
DetectDrift, …) are inherently **cross-context**: one workflow coordinates
Transcript, an AI adapter, Knowledge, Insights, Organization, and Drift. The
ratified skeleton (ADR-0002) put an `application/` folder *inside each* bounded
context, which fits context-local use cases but not cross-context orchestration.

We also need firm rules for what the application layer may depend on, so it stays
thin and never becomes a second home for domain logic.

## Decision

**Placement.** Cross-context orchestration lives in a dedicated top-level layer,
`apps/core-api/src/application/`, that sits *above* the bounded contexts and
composes their domain ports. Per-context `modules/<ctx>/application/` folders
remain for context-local use cases; genuinely cross-context workflows live in the
top-level layer.

**Boundaries.**

1. The application layer depends on **domain contracts only** — domain repository
   ports, domain services/policies, and Published Language — never on
   infrastructure.
2. All external AI access goes through an **AI Engine ACL port**; the application
   never imports an LLM SDK.
3. AI output is a **DTO proposal**, never a domain object. It becomes domain state
   only after the use case maps and validates it (evidence-first; AI-authored
   artifacts enter as `Proposed`).
4. Application **contract** files (commands, queries, results, handler interfaces,
   application ports, application events) depend on the Shared Kernel and
   primitives; the specific domain ports a handler composes are wired in its
   *implementation* and documented in the use-case map — not imported into the
   contracts.
5. Orchestration is thin and explicit: one command/query handler per use case, no
   fat services. Every handler is testable with fakes, no infrastructure.

## Consequences

**Positive**

- Cross-context workflows have a clear home; contexts stay decoupled from each
  other's orchestration.
- The AI boundary is the single, swappable seam for LLM integration.
- Handlers are unit-testable against port fakes.

**Negative / costs**

- A new top-level layer beyond the per-module structure — engineers must know
  where a use case belongs (context-local vs cross-context).
- The application layer couples (at implementation time) to many contexts' domain
  ports; this is inherent to orchestration and accepted.

## Related

- Layering & module structure: ADR-0002. Runtime split / ACL: ADR-0001.
- Graph eventual consistency the handlers must respect: ADR-0006.
- Full design: `docs/APPLICATION_LAYER.md`.
