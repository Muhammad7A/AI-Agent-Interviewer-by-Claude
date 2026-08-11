# Architecture Readiness Review

> **Reviewer role:** Principal Engineer accountable for taking this repository from
> architecture into production and maintaining it for five years.
> **Scope:** all 9 ADRs, 6 bounded contexts, the application layer, and the AI ACL.
> **Mandate:** identify risk, rank debt by cost, name friction contracts, gate the
> seams, and reject changes that should stay unresolved. **No implementation, no
> redesign.**

---

## 0. Verdict

**The architecture is sound, unusually disciplined, and NOT yet ready for
production code.**

What's strong: contracts-first with everything type-checking; a genuine
evidence-first spine; clean bounded contexts with Published-Language boundaries;
the "one graph, six lenses" model held across five contexts; the official-vs-
discovered separation that is the product's moat; a clean AI ACL.

What blocks production code: the model defines *what is true* but has not decided
*where truth is enforced*. Three enforcement homes are undefined — **domain
behaviour, tenant isolation, and evidence/confidence provenance** — and the
**build/test topology is half-formed**. Until those four (R1, R2, R3, R7) are
settled, the first line of production code will put domain logic in the wrong
layer and be untestable in CI.

**Estimated P0 foundation before the first production vertical slice: ~4–6 focused
engineer-weeks.** The big deferred decisions (storage engine, event broker) are
*correctly* deferred and must not be pulled forward beyond a spike.

---

## 1. Risk register (ranked by severity × likelihood)

Cost key: **S** ≈ <1 wk · **M** ≈ 1–4 wk · **L** ≈ 1–2+ months.

| ID | Sev | Risk | Evidence | Cost | Gate |
|----|-----|------|----------|------|------|
| **R1** | 🔴 Critical | **No domain behaviour / enforcement home.** Every aggregate is a `readonly` state interface; invariants (N/K/T/INS/ORG/DRIFT) exist only as declarative `*_INVARIANTS` data. Nothing *enforces* them. Docstrings say behaviour lives "in the owning context" *and* "in the application layer" — an unresolved contradiction that will push domain logic up into handlers. | every `aggregates/*.ts`; `INVARIANTS` registries | L | **P0** |
| **R2** | 🔴 Critical | **Tenant isolation is aspirational.** ADR-0003 promises a "base repository / query guard" that structurally prevents cross-tenant reads. No such contract exists; repo ports merely *accept* `tenantId`. Nothing stops an implementation from ignoring it. Security-critical. | ADR-0003; all `repositories/*` | M | **P0** |
| **R3** | 🔴 Critical | **Evidence-first is unenforceable as shipped.** `ConfidencePolicy` was specified (DOMAIN_MODEL §3.3) but never shipped in the kernel. Nothing maps `AiConfidenceHint`→ 6-factor `Confidence`, and nothing builds or validates `Derivation` chains down to `EvidenceRef`s (E1/N1/IN4/DRIFT4). The platform's trust proposition has no home. | `@oi/contracts` (no `ConfidencePolicy`); `AiConfidenceHint` | M–L | **P0** |
| **R7** | 🔴 Critical | **Build topology incomplete.** `packages/contracts` is a real package, but `apps/core-api` is only a `tsconfig` with path aliases — no `package.json`, no dependency on `@oi/contracts`, no test runner, no lint, no CI. Core-api cannot be built or tested as a unit. TDD of the application layer is impossible today. | `apps/core-api/` (no package.json) | M | **P0** |
| **R4** | 🟠 High | **Persistence architecture undecided but heavily constrained.** "One graph, six lenses" + `KnowledgeGraphLens.pathsBetween`/`provenanceChain` + per-node/edge eventual consistency (ADR-0006) strongly imply graph-capable storage; Organization/Transcript are relational. A wrong pick forces repository rework. The *port* deferral is correct; the *decision* is now due before Knowledge repos. | ADR-0004/0006; `KnowledgeGraphLens` | L | **P1** |
| **R5** | 🟠 High | **Cross-runtime contract source of truth missing.** ADR-0001 promised `packages/contracts` generates *both* TS types and Python pydantic models. Only TS exists; the AI DTOs live in the TS app layer. When the Python `ai-engine` is built, contract drift is guaranteed. | ADR-0001; `application/ai/*` | M | **P1** |
| **R6** | 🟠 High | **No saga / process-manager for multi-step, multi-context flows.** `UnitOfWork` bounds one aggregate; but StartTranscriptAnalysis→BuildKnowledgeGraph→GenerateInsights/DetectDrift is a multi-store choreography with no defined partial-failure recovery, retry, or compensation. | `application/` event flow; `UnitOfWork` | M–L | **P1–P2** |
| **R8** | 🟡 Medium | **Idempotency can't be transparent.** `IdempotencyStore.has/remember(key)` stores no result, so a replayed `OpenEngagement` cannot return the original `engagementId` — only no-op or error. | `shared/ports.ts` | S | **P1** |
| **R9** | 🟡 Medium | **Evidence representation is inconsistent.** Knowledge/Insights nodes carry `Evidence[]`; Drift findings/mappings and… carry `EvidenceRef[]`; Observation/Finding carry `Evidence[]`. The spine is not uniformly typed, which will fracture the provenance drill-path. | `drift/aggregates/*` vs `insights/*` | S–M | **P1** |
| **R10** | 🟡 Medium | **Authorization is coarse and IAM is absent.** `AuthorizationPort` is action-level; it cannot express "may this consultant validate *this* recommendation in *this* engagement." The Identity & Access context was never designed. | `shared/ports.ts`; skeleton `identity-access/` | M–L | **P2** |
| **R11** | 🟡 Medium | **The read side is shapes-only.** Every context ships read-model *types* but there is no projection/materialization/staleness strategy, no query handlers, and Consultant Workspace + Reporting are unbuilt/unowned. | `read-models/*`; `Query` marker | M | **P2** |
| **R12** | 🟡 Medium | **Cross-aggregate referential integrity unenforced.** Insights `KnowledgeArtifactRef` → Knowledge nodes, Drift refs → both, all by id; nothing guarantees the target exists / is same-tenant / isn't dismissed. Inherent to ADR-0006 but needs reconciliation. | `KnowledgeArtifactRef`, `OfficialElementRef` | M | **P2** |
| **R13** | 🟡 Medium | **Published Languages don't export id VOs.** Drift recovers ids via indexed access (`Department['id']`); the app layer falls back to opaque `string` ids at its boundary. Branded-id safety is lost exactly where it crosses contexts. | `drift/value-objects/refs.ts` | S | **P1** |
| **R14** | 🟢 Low | **`NodeType`/`EdgeType` are open strings with no registry.** N5 (type↔layer coherence) has no enforcement and nothing prevents cross-context type-name collisions or typos. | `@oi/contracts` graph seam | S–M | **P2** |
| **R15** | 🟢 Low | **No event schema versioning/migration.** `DomainEvent.eventType` is a bare string; persisted events (outbox/choreography) will need evolution. | `events/*` | M | **P3** |
| **R16** | 🟢 Low | **Error model differs across layers.** Repos return `T \| null`; app returns `Result<T>`; domain enforcement (once it exists) will throw. No convention. | ports vs `Result` | S | **P1** |
| **R17** | 🟢 Low | **Reference-VO proliferation.** Three overlapping "ref to an artifact" VOs (`KnowledgeArtifactRef`, `OfficialElementRef`, `DiscoveredElementRef`). Manageable, watch for divergence. | across contexts | S | Watch |

---

## 2. The one risk that dominates: R1 (no enforcement home)

This deserves its own paragraph because it silently determines the fate of the
other risks. Today the aggregates are pure data. There are exactly three places
enforcement *could* land:

- **Infrastructure** (validate on save) — worst; scatters domain rules into adapters.
- **Application handlers** — bad; directly violates ADR-0008 rule "no business
  rules in the application layer," and it's where the code will drift *by default*
  if we don't decide.
- **Domain** — correct, but requires a chosen shape: a **functional core** (pure
  `create`/`transition` functions returning new state + events, guarded by
  specifications) or **rich aggregates** (convert interfaces to classes with
  behaviour) or **factory + specification services**.

Recommendation: a **functional core** (pure domain functions + specification
objects that consult the `*_INVARIANTS` registries) — it preserves the immutable
state contracts already shipped, keeps aggregates serialization-friendly for the
eventual graph store, and is the most testable. **This needs an ADR before any
domain code.** Until it exists, "AI proposes, domain validates," anchor
protection, and evidence-first have nowhere to run.

---

## 3. Friction contracts (will cause pain during implementation)

Ranked by how early they bite:

1. **`AiConfidenceHint` → `Confidence`** — no mapper; every AI flow needs one (R3).
2. **`ExtractedClaimDto` span re-anchoring** — the bytes sent to the AI must be
   *identical* to the immutable `SegmentText`, and returned `charStart/charEnd`
   must be validated against it, or T6 "deterministic resolution" silently breaks.
   The contract does not pin this; it's a correctness landmine.
3. **`KnowledgeGraphLens.lens(layer)` returns a whole `SubGraph`** — unbounded read;
   no pagination/streaming/cursor. On a real engagement this is a memory and
   latency cliff. Needs a bounded/streamed variant before use.
4. **`IdempotencyStore`** — can't return prior results (R8).
5. **`Evidence[]` vs `EvidenceRef[]`** inconsistency (R9).
6. **`UnitOfWork` vs eventual consistency** — semantics ambiguous for the
   multi-aggregate writes DetectDrift/BuildKnowledgeGraph actually perform (R6).
7. **Repo `T | null` vs app `Result<T>`** — error-mapping boilerplate at every
   call site until a convention exists (R16).
8. **`Query` marker (`_query?: never`) + zero query handlers** — the entire read
   path is unimplemented scaffolding (R11).
9. **Indexed-access id recovery** in Drift — fragile; breaks if Organization
   renames an aggregate (R13).

---

## 4. Seams that MUST close before production code

The gate. Do **not** start production domain implementation until these are decided
(ADR-level), even if not fully built:

| Must-close | Risk | Deliverable |
|---|---|---|
| Domain enforcement strategy | R1 | ADR: functional core (recommended) |
| Tenant isolation mechanism | R2 | ADR + a real tenant-scoped repository base / Postgres RLS decision |
| Evidence & confidence enforcement location | R3 | ADR: `ConfidencePolicy` + `DerivationFactory`/validator in the kernel |
| Build & test topology | R7 | root workspace, `core-api` package, test runner, CI (typecheck + test + lint) |
| Graph persistence direction | R4 | a **spike + ADR** (not an implementation) before Knowledge repos |
| Cross-runtime contract SoT | R5 | ADR: schema codegen (JSON Schema/protobuf) before `ai-engine` |

Everything else can ride along with the first vertical slice.

---

## 5. Intentionally unresolved — REJECT changing now

Senior judgment is as much about what *not* to do. These are correctly open; pulling
them forward is over-engineering:

- **Final storage engine pick (beyond a spike).** Keep it behind the repository
  ports (ADR-0002). Decide the *shape* (graph-capable vs relational+extension), not
  the vendor, and only when Knowledge repos are next.
- **Microservices.** The modular monolith is right for this stage (ADR-0002).
  Reject any split; the contexts already have clean extraction seams if ever needed.
- **Event broker / async transport.** Keep `DomainEventPublisher` abstract; in-process
  is fine until throughput proves otherwise. Do not adopt Kafka/queues now.
- **Unifying the three versioning mechanisms** (`TranscriptVersion`,
  `OrganizationVersion`, `KnowledgeNode.version`). Each is domain-appropriate; a
  shared temporal abstraction is premature. Watch-item only.
- **Merging `ActorRef` and `OwnerRef`.** They model different things (IAM identity vs
  org ownership). Keep both.
- **Splitting `@oi/contracts` into kernel + graph-kernel.** Real observation, but
  cosmetic; defer until the kernel actually grows a second non-graph consumer set.
- **Building Reporting / IAM contexts in full.** Defer — but their *stubs*
  (`ProduceConsultantReport`, `AuthorizationPort`) must stay honest about being
  stubs, not quietly become the permanent home.
- **gRPC vs REST for the AI boundary.** Defer; the ACL port hides it.

---

## 6. Prioritized Production Readiness Checklist

### P0 — before writing any production domain code (the gate)
1. **ADR-0009: domain enforcement strategy** — functional core; specifications read
   the `*_INVARIANTS` registries. **[R1, L]**
2. **ADR-0010 + mechanism: multi-tenant isolation** — tenant-scoped repository base
   and/or Postgres RLS; the single sanctioned query path. **[R2, M]**
3. **ADR-0011: evidence & confidence enforcement** — ship `ConfidencePolicy` and a
   `DerivationFactory`/validator in the kernel; define the `AiConfidenceHint`→`Confidence`
   mapping and the E1 chain validator. **[R3, M–L]**
4. **Build topology** — root `package.json` workspaces; `apps/core-api/package.json`
   (deps: `@oi/contracts`, TypeScript, a test runner — Vitest); ESLint; CI running
   `typecheck + lint + test` on every push. **[R7, M]**

### P1 — with the first vertical slice (StartTranscriptAnalysis, end-to-end, fakes + tests)
5. Persistence **spike + ADR** for the knowledge graph store. **[R4, L]**
6. Cross-runtime contract codegen decision, before any `ai-engine` code. **[R5, M]**
7. Publish id VOs from every `published-language.ts`. **[R13, S]**
8. Standardize the evidence type to `Evidence[]` everywhere. **[R9, S]**
9. Idempotency-with-result. **[R8, S]**
10. Error-handling convention (domain throws typed errors → app maps to `Result`). **[R16, S]**
11. Specify + test `ExtractedClaimDto` span re-anchoring against immutable segment text. **[friction #2, S]**
12. ESLint `no-restricted-imports` enforcing PL boundaries (ADR-0002). **[seam, S]**
13. Promote validation transitions from the app layer into a domain service. **[R1-adjacent, S–M]**
14. Bound/stream `KnowledgeGraphLens` reads. **[friction #3, S–M]**

### P2 — before scaling contexts / building the read side
15. Saga / process-manager pattern for multi-step flows + outbox. **[R6, M–L]**
16. Read-model projection strategy; assign Consultant Workspace + Reporting owners. **[R11, M]**
17. Cross-aggregate referential-integrity reconciliation (events, not FKs). **[R12, M]**
18. Resource-level authorization + the Identity & Access context. **[R10, M–L]**
19. `NodeType`/`EdgeType` registry + N5 coherence check. **[R14, S–M]**

### P3 — before production scale
20. Event schema versioning/migration. **[R15, M]**
21. Promote shared scales (`RiskLevel`, `Severity`) to the kernel under the rule of three. **[seam, S]**
22. Event broker **only** if throughput demands it (keep the port). **[deferred]**

---

## 7. One-line recommendation

**Freeze new context/feature design. Spend the next ~4–6 weeks on the P0 gate
(enforcement home, tenant guard, evidence/confidence policy, build+CI), then prove
it with one vertical slice — StartTranscriptAnalysis end-to-end with fakes and
tests — before writing a second use case or a single infrastructure adapter.**
