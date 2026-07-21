# 1. Hybrid runtime: TypeScript core + Python AI engine

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

The platform has two workloads with genuinely different characteristics:

1. **Platform / domain / system-of-record work** — auth, organizations, tenancy,
   invitations, transcript storage, orchestration, consultant-facing APIs. This
   needs strong typing, dependency injection, clear module boundaries, and a
   large hiring pool. It is I/O- and orchestration-heavy, not compute-heavy.
2. **AI cognition** — interview turn generation, extraction, knowledge
   construction, bottleneck and opportunity detection. This lives closest to the
   Python AI/ML ecosystem and has a different scaling and dependency profile.

Options considered:

- **Single TypeScript stack.** Simplest ops, one language — but pushes AI/ML work
  against the grain of its ecosystem.
- **Single Python stack.** Closest to AI tooling — but weaker out-of-the-box
  structure/DI for a large domain-driven platform, and more discipline required
  to keep clean boundaries.
- **Hybrid: TS core + Python AI service.** Each workload in its natural
  environment, at the cost of one service boundary.

## Decision

Adopt a **hybrid** architecture:

- **`core-api`** in **TypeScript / NestJS** is the system of record and hosts all
  platform bounded contexts as internal modules (a modular monolith).
- **`ai-engine`** in **Python / FastAPI** performs stateless AI cognition and
  owns no business truth.

The governing rule: **stateful orchestration and the system of record live in
`core-api`; stateless AI cognition lives in `ai-engine`.** `ai-engine` never
writes to the primary database and never resolves tenancy or auth on its own.

The runtime boundary is a versioned contract in `packages/contracts`, generating
both TS types and Python models so the two sides cannot drift.

## Consequences

**Positive**

- Each workload uses its natural ecosystem.
- Tenant isolation, auth, and audit are centralized in exactly one runtime.
- `ai-engine` is horizontally scalable and freely restartable (stateless).
- The AI runtime can later be swapped or scaled independently.

**Negative / costs**

- One cross-runtime boundary exists from day one (network, serialization,
  contract versioning). We accept this because the two sides are genuinely
  different runtimes — unlike splitting individual domain contexts, which we
  explicitly refuse to do yet.
- Two toolchains to build, test, and deploy.

## Related

- Boundary details: `docs/ARCHITECTURE.md` §2, §6.
- We remain a modular monolith on the platform side: `0002`.
