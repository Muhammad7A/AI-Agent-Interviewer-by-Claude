# core-api (NestJS)

> ## ⚠ STATUS: RATIFIED DESIGN — CONTRACTS ONLY. THIS CODE HAS NEVER RUN.
>
> There is **no runtime, no persistence, no server, and no tests** here. Every file
> in `src/` is a type-level contract that `tsc` checks and nothing executes.
>
> **The working system is the Python package `apps/ai-engine/ai_engine/`.** If you
> are looking for code that does something, it is there — see
> `../../docs/CODE_WALKTHROUGH.md`.
>
> This tree is kept because the roadmap needs it in Year 1–2 (persistence, tenancy,
> enterprise readiness), not because it is load-bearing today. Its deletion path is
> documented in `../../docs/REPO_MAP.md`: nothing in `ai_engine` imports it, so it
> can be removed without touching the working product.
>
> Where a concept exists on both sides (`TranscriptSegment`, `EvidenceRef`), the two
> are held in step mechanically by
> `apps/ai-engine/tests/test_contract_conformance.py`. Every deliberate difference is
> declared there with a reason; anything undeclared fails the build.

**Intended** role, once implemented: the system of record and platform backbone —
a modular monolith hosting the platform bounded contexts as internal modules,
owning persistence, multi-tenancy, authentication/authorization, orchestration,
audit, and the consultant-facing APIs, and delegating AI cognition to `ai-engine`
over the versioned contract in `packages/contracts`.

## Rules

- Each context under `src/modules/<context>/` has four layers:
  `domain` · `application` · `infrastructure` · `presentation`.
- **Dependencies point inward.** `domain` imports nothing from other layers.
  Infrastructure implements domain ports; it is never imported by the domain.
- **No cross-module reach-in.** A module talks to another module only through
  its published application interface or via domain events — never by importing
  another module's `domain`/`infrastructure`.
- Every tenant-owned aggregate carries a `TenantId`. No query reaches the
  database except through the tenant-scoped repository guard.

See `../../docs/ARCHITECTURE.md` and `../../docs/adr/`. No business logic yet —
this is the ratified skeleton.
