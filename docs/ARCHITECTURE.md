# Architecture

> **Status:** Foundational draft. This document defines the boundaries and rules
> the codebase must obey. It is intentionally ahead of the implementation — code
> is added _into_ this structure, never around it. Changes to the rules below go
> through an ADR (see `docs/adr/`).

---

## 1. What we are building

An **Organizational Intelligence platform** for an AI Transformation consulting
firm. It automates the **Discovery & Assessment** phase of a consulting
engagement.

This is **not** a chatbot product. The AI interview is only the _ingestion
layer_. The product is the pipeline that turns raw conversations into
**structured, queryable, evidence-backed organizational knowledge** that
consultants validate and act on.

Human consultants remain accountable for validation, strategy, and delivery.
Therefore the system is built around one non-negotiable property:

> **Every insight is traceable to its evidence.**
> A bottleneck or AI-opportunity the platform surfaces must point back to the
> exact transcript segment(s) that justify it. Nothing is asserted without a
> citation a consultant can inspect.

### The core pipeline

```
 Interview      Transcript        Extraction          Knowledge Base
 (capture)  →   (raw record)  →   (structured    →    (org model +
                                   facts + refs)        evidence links)
                                                            │
                                                            ▼
                                                   Detection
                                        (bottlenecks / AI opportunities)
                                                            │
                                                            ▼
                                                   Insights → Consultant
                                                   Dashboard + Reports
                                                   (human-in-the-loop)
```

Each arrow is a boundary. Data only moves forward through explicit, versioned
contracts — never by one module reaching into another's internals.

---

## 2. Deployment shape: two runtimes, one product

We are a **modular monolith on the platform side** plus a **separate AI compute
service**. We do **not** start with microservices.

| Runtime | Tech | Responsibility |
|---|---|---|
| **`core-api`** | TypeScript / NestJS | Source of truth. Owns persistence, tenancy, auth, orchestration, audit, and all consultant-facing APIs. Hosts the platform bounded contexts as internal modules. |
| **`ai-engine`** | Python / FastAPI | Stateless AI cognition. Interview turn generation, extraction, knowledge construction, and detection. Owns **no** business truth. |
| **`web`** _(later)_ | Next.js | Consultant + interviewee UIs. Talks only to `core-api`. |

**The governing split:**

> **Stateful orchestration and the system of record live in `core-api`.
> Stateless AI cognition lives in `ai-engine`.**

`ai-engine` is given the context it needs for a task and returns structured
results. It never writes to the primary database, never resolves tenancy or
auth on its own, and is safe to scale horizontally and restart at will. This
keeps tenant isolation, audit, and data governance centralized in exactly one
place — a hard requirement for a B2B platform handling client organizational
data.

### Why this split (and not microservices-per-module)

At the Discovery stage the risk is **getting boundaries wrong**, not scaling
throughput. A modular monolith lets us enforce strict bounded-context
boundaries _in code_ while paying zero distributed-systems tax. Any context can
later be extracted into its own service **because** we enforce the boundaries
now. The one boundary we _do_ split today — TS core vs. Python AI — is justified
because the two sides have genuinely different runtimes, dependency ecosystems,
and scaling profiles. See `docs/adr/0001-hybrid-ts-core-python-ai.md`.

---

## 3. Bounded contexts

Twelve product modules map onto the two runtimes as follows. Each context has an
owner runtime, a clear responsibility, and a public interface. **A context is a
boundary, not a folder** — crossing it always goes through its published
application interface or a domain event.

### Platform contexts — `core-api` (NestJS)

| Context | Module(s) | Responsibility |
|---|---|---|
| **Identity & Access** | Authentication | Users, credentials, sessions, roles (consultant / admin / interviewee). |
| **Organization** | Organization Management | The tenant aggregate. Client orgs, departments, org-level settings. |
| **Invitations** | Employee Invitation | Inviting employees into an interview, invite lifecycle & tokens. |
| **Interview Orchestration** | AI Interview Engine (session side) | Interview session lifecycle. Delegates each _AI turn_ to `ai-engine`; owns session state and turn persistence. |
| **Transcript** | Transcript Storage | Immutable record of interviews. The canonical evidence store. |
| **Knowledge** | Organizational Knowledge Base | Persisted org model (entities, workflows, relationships) with evidence links. Read + write side of the knowledge graph. See `ORGANIZATIONAL_INTELLIGENCE_ENGINE.md` for the full domain model. |
| **Insights** | Bottleneck Detection, AI Opportunity Detection (results side) | Persistence and lifecycle of detected findings, incl. consultant validation state. |
| **Reporting** | Report Generator | Assembles validated insights into consultant deliverables. |
| **Consultant Workspace** | Consultant Dashboard | Read-optimized APIs/projections for the consultant UI. |
| **Administration** | Administration Panel | Platform + tenant administration, feature flags, usage. |

### AI capabilities — `ai-engine` (FastAPI)

`ai-engine` is organized by **capability**, not by product module. Each
capability is a pure function of its inputs → structured output.

| Capability | Feeds module | Responsibility |
|---|---|---|
| **Interview cognition** | AI Interview Engine | Given session context + conversation memory, produce the next interviewer turn (question / probe / wrap-up). |
| **Conversation memory** | Conversation Memory | Maintain and summarize working context within a session under a token budget. |
| **Extraction** | Transcript → Knowledge | Turn transcript segments into structured facts, entities, and workflow steps — each carrying an evidence reference. |
| **Knowledge construction** | Organizational Knowledge Base | Merge extracted facts into a coherent org model / graph. |
| **Bottleneck detection** | Bottleneck Detection | Analyze the org model to surface operational bottlenecks, with evidence. |
| **Opportunity detection** | AI Opportunity Detection | Identify workflows suited to automation / AI, with evidence and rationale. |

> **Evidence rule for `ai-engine`:** every structured item it emits — a fact, a
> bottleneck, an opportunity — carries one or more `EvidenceRef`s pointing at the
> transcript segments that justify it. Output without evidence is a contract
> violation, not a warning.

---

## 4. Layering (both runtimes)

Every context uses the same hexagonal / clean-architecture layering. The layers
and the **dependency rule** are identical across TS and Python so engineers move
between them without relearning the shape.

```
        presentation  ──▶  application  ──▶  domain  ◀──  infrastructure
        (controllers,      (use cases,       (entities,     (adapters:
         routers, DTOs)     orchestration)    VOs, ports)    DB, LLM, HTTP)
```

| Layer | Contains | Depends on |
|---|---|---|
| **domain** | Entities, value objects, aggregates, domain events, and **ports** (repository & service interfaces). Pure business rules. | **Nothing.** No framework, no I/O, no imports of other layers. |
| **application** | Use cases / application services. Orchestrates domain objects and ports. Owns transaction boundaries. | domain only. |
| **infrastructure** | Adapters that _implement_ domain ports: DB repositories, the LLM client, the `core-api`↔`ai-engine` HTTP/queue clients. | domain (implements its ports), application. |
| **presentation** | NestJS controllers / FastAPI routers, request/response DTOs, mappers. | application. |

**The dependency rule — dependencies point inward:**

- `domain` imports nothing from other layers. It is unit-testable in complete
  isolation, with no database and no LLM.
- Infrastructure depends on the domain by **implementing its ports**, never the
  reverse. Swapping Postgres, or swapping the Claude model, or adding a second
  LLM provider, must not touch a single line of `domain`.
- Cross-context communication happens **only** through a context's published
  application interface or via domain events — never by importing another
  context's `domain`/`infrastructure` directly.

This is what makes the SOLID goals real: the Dependency Inversion Principle is
enforced by the layer boundaries, not by convention.

---

## 5. Multi-tenancy

**Model:** shared database, **row-level tenant scoping**
(see `docs/adr/0003-multi-tenancy-row-level.md`).

Rules:

1. Every tenant-owned aggregate carries a `TenantId` (an org). It is modeled as a
   value object in the domain, not an incidental column.
2. Tenant context is resolved **once**, at the edge of `core-api` (auth →
   request-scoped `TenantContext`), and propagated through the application layer.
3. A **base repository / query guard in infrastructure guarantees no query
   escapes tenant scope.** Individual use cases cannot forget to filter by
   tenant — it is structurally impossible to write an unscoped query through the
   sanctioned repository path.
4. `ai-engine` never resolves tenancy. It receives already-scoped context from
   `core-api` and returns results tagged with the same scope for `core-api` to
   persist. Cross-tenant leakage has exactly one place it could originate, and
   that place is guarded.

---

## 6. The runtime boundary contract (`core-api` ↔ `ai-engine`)

The boundary between the two runtimes is a **first-class, versioned contract**,
not ad-hoc HTTP. Contracts are the single source of truth in
`packages/contracts` and generate **both** TypeScript types and Python
(pydantic) models, so the two sides can never silently drift.

Two interaction styles:

| Style | Used for | Mechanism |
|---|---|---|
| **Synchronous** | Interview turns — latency-sensitive, user is waiting. | Request/response (REST or gRPC). `core-api` calls, `ai-engine` returns the next turn. |
| **Asynchronous** | Extraction, knowledge construction, detection — long-running, batch. | Job/event driven. `core-api` enqueues work; `ai-engine` processes and returns results for `core-api` to persist. |

`ai-engine` is effectively stateless per request: everything it needs arrives in
the contract payload (or via a read-only context fetch), and everything it
produces goes back for `core-api` to store. This is what lets us scale, restart,
and later even swap the AI runtime without touching the system of record.

---

## 7. Cross-cutting principles

- **AI providers sit behind ports.** No domain or application code names a model
  or SDK. The LLM is an adapter implementing a domain port. Default to the latest
  Claude models; switching or adding a provider is an infrastructure change only.
- **Testability is structural, not aspirational.** Domain logic is pure and
  unit-tested. Adapters are integration-tested against their real dependency.
  Because the domain has no I/O, it needs no mocks of frameworks.
- **Evidence and auditability are domain concepts.** `EvidenceRef` (a link from a
  derived fact/insight back to a transcript segment) is part of the ubiquitous
  language, present in the model — not a logging afterthought.
- **Immutability of the record.** Transcripts are append-only. Derived knowledge
  can be recomputed; the raw evidence it derives from cannot be mutated.
- **Consultant-in-the-loop is a state, not a hope.** Insights carry an explicit
  validation lifecycle (e.g. `suggested → validated → dismissed`). The platform
  proposes; the consultant disposes.

---

## 8. Repository layout

```
/
├── apps/
│   ├── core-api/          # NestJS — platform bounded contexts (system of record)
│   │   └── src/modules/<context>/{domain,application,infrastructure,presentation}
│   ├── ai-engine/         # FastAPI — AI capabilities (stateless cognition)
│   │   └── src/<capability>/{domain,application,infrastructure,presentation}
│   └── web/               # Next.js — consultant + interviewee UIs (later)
├── packages/
│   └── contracts/         # Cross-runtime contracts → TS types + pydantic models
├── docs/
│   ├── ARCHITECTURE.md    # This document
│   └── adr/               # Architecture Decision Records
└── README.md
```

Folders exist for the contexts and capabilities named above so the boundaries
are visible before any logic lands. They are intentionally empty (or
placeholder-only) at this stage — the skeleton _is_ the current deliverable.

---

## 9. What is deliberately deferred

To avoid premature complexity (and the technical debt that comes with guessing),
the following are **out of scope until a concrete driver exists**, and each will
get its own ADR when it arrives:

- Concrete database engine & ORM choice (the domain doesn't depend on it either
  way — this is an infrastructure decision).
- Message broker / queue technology for the async boundary.
- gRPC vs. REST for the sync boundary.
- Extraction of any context into a standalone service.
- Real-time streaming of interview turns to the UI.

Choosing these now would be guessing. Choosing them behind ports means the
guess, when we make it, is cheap to change.
