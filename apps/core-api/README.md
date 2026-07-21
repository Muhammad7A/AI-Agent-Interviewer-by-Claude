# core-api (NestJS)

The **system of record** and platform backbone. A modular monolith hosting the
platform bounded contexts as internal modules.

Owns: persistence, multi-tenancy, authentication/authorization, orchestration,
audit, and all consultant-facing APIs. Delegates AI cognition to `ai-engine`
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
