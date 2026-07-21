# Knowledge context

Core bounded context. Owns the **substrate + descriptive layers** of the unified
graph (Structural / Capability / Operational) and the `Claim` bridge from
transcript text to structured knowledge. See `docs/DOMAIN_MODEL.md` §6.1.

**This slice is the `domain/` layer only — contracts, no behaviour.** No
persistence, infrastructure, application services, or presentation. Every
contract extends the Shared Kernel (`@oi/contracts`) without duplication.

## `domain/` layout

| Folder | Contents |
|---|---|
| `aggregates/` | `Claim` (aggregate root). `KnowledgeNode`/`KnowledgeEdge` roots are the Shared Kernel base, specialized under `nodes/` & `edges/`. |
| `entities/` | `Contradiction` (recorded evidence conflict; K2). |
| `value-objects/` | Ids (`ClaimId`, `ContradictionId`), enums, `ClaimTriple`/`ClaimStatus`, `ResolutionDecision`, `GraphMutation`, read models (`SubGraph`/`Path`/`EvidenceTree`). |
| `nodes/` | Structural (Department, Team, Role, Person), Capability (Process, Capability), Operational (Workflow, Activity, Handoff, System, Artifact) attribute + node contracts, and the node-type catalog. |
| `edges/` | Structural / capability / operational edge contracts + the edge-type catalog. |
| `repositories/` | Ports: `KnowledgeNodeRepository`, `KnowledgeEdgeRepository`, `ClaimRepository`, `KnowledgeGraphLens` (read model). |
| `services/` | Policy ports (interfaces only): `EntityResolutionPolicy`, `EvidenceMergeService`, `GraphConstructionService`, `AnchorProtectionPolicy`. |
| `events/` | `Claim`/`Contradiction` lifecycle events (substrate node/edge events stay in the kernel). |
| `invariants/` | `KnowledgeInvariantCode` + `KNOWLEDGE_INVARIANTS` (K1–K3, C1–C2), extending N1–N5/E1. |
| `published-language.ts` | The curated external surface for downstream contexts. |

## Type-check

The domain type-checks against the Shared Kernel source (resolved via a `paths`
mapping in `apps/core-api/tsconfig.json`):

```bash
cd packages/contracts && npm install   # provides TypeScript
cd ../../apps/core-api && ../../packages/contracts/node_modules/.bin/tsc -p tsconfig.json
```

`application/`, `infrastructure/`, and `presentation/` remain empty until
implementation is approved.
