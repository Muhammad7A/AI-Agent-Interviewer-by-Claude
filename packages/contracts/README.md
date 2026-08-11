# @oi/contracts — the Shared Kernel

> ## ⚠ STATUS: RATIFIED DESIGN — CONTRACTS ONLY. NO RUNTIME.
>
> `tsc` type-checks this package; nothing executes it. The working system is the
> Python package `apps/ai-engine/ai_engine/`.
>
> This package was described as "mirrored to the Python ai-engine". It was mirrored
> **by hand, in comments**, and it drifted: the Python `EvidenceRef` had lost
> `transcriptId`, so a reference could not resolve itself and — once findings from
> several interviews were aggregated — could resolve against the wrong person's
> transcript and yield someone else's words as evidence.
>
> The mirror is now mechanical. `apps/ai-engine/tests/test_contract_conformance.py`
> parses these interfaces and fails the build on any undeclared divergence, in either
> direction. The thin slice may implement *less* than the ratified design; every such
> omission is recorded there with a reason.

The **ratified source of truth** for the platform's evidence-first provenance model
and the **one-graph substrate**, intended to be shared by the core bounded contexts
(Knowledge, Insights) and by the Python `ai-engine` as Published Language.

**Type contracts only.** This package contains **no domain behaviour** — no
persistence, no infrastructure, no application/domain services, no presentation,
no business logic. It defines: domain primitives, value objects, the base
`KnowledgeNode`/`KnowledgeEdge` contracts, the evidence / confidence /
validation / provenance models, substrate domain events, and the invariant
registry (declarative data). It type-checks as a standalone package.

## What's inside (`src/`)

| Folder | Contracts |
|---|---|
| `primitives/` | Branded ids & scalars (`TenantId`, `EngagementId`, `KnowledgeNodeId`, `Score`, `Timestamp`, …), `ActorRef`. |
| `provenance/` | `Evidence`, `EvidenceRef`, `Derivation`, `SourcePerspective`, `CharSpan`, `EvidenceKind` — the evidence spine. |
| `confidence/` | `Confidence`, `ConfidenceFactors`, `ConfidenceBand` — computed, explainable, orthogonal to validation. |
| `validation/` | `ValidationState`, `ValidationRecord`, `ValidationEvent` — the human-in-the-loop plane. |
| `graph/` | `KnowledgeNode`, `KnowledgeEdge` (base contracts), `Layer` (the six lenses), `NodeType`/`EdgeType`, attribute markers. |
| `events/` | `DomainEvent` envelope + substrate events (node/edge/evidence/confidence/validation). |
| `invariants/` | `InvariantCode` + the `SHARED_KERNEL_INVARIANTS` registry (N1–N5, E1). |

## Design rules this package encodes

- **Evidence-first (N1, E1):** every node/edge carries ≥1 `Evidence`; inferred
  evidence resolves transitively to stated transcript segments.
- **One graph, six lenses (ADR-0004/0005):** all node/edge types conform to the
  base contracts here; a "lens" is a `Layer` query. `NodeType`/`EdgeType` values
  are context-owned (open brands); the shape is shared.
- **Node/edge as Aggregate Roots (ADR-0006):** edges reference endpoints by
  identity only; these interfaces are *state* contracts — behaviour lives in the
  owning contexts.

## Verify

```bash
npm install       # dev-only: TypeScript, pinned
npm run typecheck # tsc --noEmit — contracts must type-check
npm run build     # emits dist/ (.d.ts + declaration maps)
```

See `docs/DOMAIN_MODEL.md` and `docs/adr/` for the full rationale.
