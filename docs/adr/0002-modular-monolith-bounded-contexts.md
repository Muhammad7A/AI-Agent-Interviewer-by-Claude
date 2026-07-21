# 2. Modular monolith with strict bounded contexts

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

`core-api` hosts ~10 platform contexts (Identity, Organization, Invitations,
Interview Orchestration, Transcript, Knowledge, Insights, Reporting, Consultant
Workspace, Administration). We must decide how strongly to separate them.

At the Discovery stage, the dominant risk is **getting boundaries wrong**, not
scaling throughput. Microservices-per-context would impose distributed-systems
costs (network failure modes, distributed transactions, deploy orchestration)
long before there is any throughput justification — and would make it _harder_,
not easier, to correct a boundary we drew wrong.

## Decision

Build `core-api` as a **modular monolith** with **strictly enforced bounded
contexts**:

- Each context is an internal module with four layers — `domain`, `application`,
  `infrastructure`, `presentation` — following the dependency rule (dependencies
  point inward; `domain` depends on nothing).
- **Cross-context communication is only through a context's published
  application interface or via domain events.** No module imports another
  module's `domain` or `infrastructure` directly.
- Because boundaries are enforced in code, any context can later be extracted
  into its own service with a localized change — the seams already exist.

## Consequences

**Positive**

- Zero distributed-systems tax while boundaries are still being learned.
- Boundaries are cheap to adjust now and honestly enforced.
- A clean extraction path to services later, if throughput ever demands it.

**Negative / costs**

- Requires discipline (and CI/lint enforcement) to prevent illegal cross-module
  imports — a convention that must be mechanically guarded, not just documented.
- A single deployable for the platform side; a context cannot yet be scaled in
  isolation (accepted — no driver for it today).

## Related

- Layering and dependency rule: `docs/ARCHITECTURE.md` §4.
- The one boundary we _do_ split (TS vs Python): `0001`.
