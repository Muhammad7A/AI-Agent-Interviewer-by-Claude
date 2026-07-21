# Insights context

Core bounded context. Insights owns **interpretation** — it turns organizational
knowledge into business intelligence. It never owns truth (Knowledge does) or
evidence (Transcript does). See `docs/DOMAIN_MODEL.md` §6.2.

**This slice is the `domain/` layer only — contracts, no behaviour.** No
persistence, infrastructure, application services, presentation, REST/GraphQL, or
DTOs. It depends **only** on the Published Language of the Shared Kernel
(`@oi/contracts`), Knowledge (`@oi/knowledge`), and Transcript (`@oi/transcript`).

## The interpretation pipeline

```
Knowledge graph + evidence
  → Observation   (raw AI-proposed signal; the Insights analogue of Knowledge's Claim)
  → Finding       (validated interpretation aggregating observations)
  → PainPoint     (a diagnosed problem; People/Process/Technology) ─┐
       DiagnosticCluster (groups pain points by root cause/theme)   │  Diagnostic layer
  → Opportunity   (addresses ≥1 PainPoint; an AI pattern)              Opportunity layer
  → Recommendation(targets ≥1 Opportunity) ─ RecommendationBundle      Synthesis layer
```

`PainPoint`, `DiagnosticCluster`, `Opportunity`, `Recommendation`,
`RecommendationBundle` are `KnowledgeNode` specializations — they live in the one
graph and inherit evidence + confidence + validation from the Shared Kernel base.
`Observation` and `Finding` are non-graph interpretation aggregates.

## `domain/` layout

| Folder | Contents |
|---|---|
| `aggregates/` | `Observation`, `Finding` (non-graph interpretation roots). |
| `nodes/` | Diagnostic (`PainPoint`, `DiagnosticCluster`), Opportunity (`Opportunity`), Synthesis (`Recommendation`, `RecommendationBundle`) — graph-node aggregate roots + the node-type catalog. |
| `entities/` | `RootCauseHypothesis`, `RecommendationConflict`. |
| `value-objects/` | Ids; `Severity`, `Frequency`, `BusinessImpact`, `Urgency`, `RiskLevel`, `BusinessValue`, `ImplementationComplexity`; `PainCategory`/`PainNature`; `AiPattern`/`SignalType`; `OpportunityScore`, `RecommendationPriority`, `PrioritizationWeights`; `DiagnosticConfidence`/`RootCauseConfidence` (aliases of kernel `Confidence`); `KnowledgeArtifactRef`; `Prerequisite`; policy results. |
| `repositories/` | Ports: `ObservationRepository`, `FindingRepository`, `InsightsNodeRepository`. |
| `services/` | Policy ports (interfaces only): `PainDeduplicationPolicy`, `RootCauseAnalysisPolicy`, `OpportunityRankingPolicy`, `RecommendationPrioritizationPolicy`, `RecommendationConflictPolicy`. |
| `events/` | `ObservationCreated`, `FindingConfirmed`, `PainPointDetected`, `OpportunityDetected`, `RecommendationProposed`/`Rejected`/`Accepted`, `DiagnosticClusterMerged`. |
| `invariants/` | `INSIGHTS_INVARIANTS` (INS1–INS7). |
| `read-models/` | `BottleneckRanking`, `DepartmentImpactProfile`, `OpportunityLeaderboard`, `RecommendationRoadmap`, `EvidenceTrace`. |
| `published-language.ts` | Curated external surface. |

## Invariants (INS1–INS7)

Pain→Knowledge (INS1), Opportunity→Pain (INS2), Recommendation→Opportunity
(INS3), traceability to immutable EvidenceRefs (INS4), recommendations require
findings (INS5), no orphan diagnostic objects (INS6), and **AI proposes / domain
validates** (INS7). Linkages are typed id-reference attributes so each invariant
is enforceable within its aggregate.

## Type-check

```bash
cd packages/contracts && npm install
cd ../../apps/core-api && ../../packages/contracts/node_modules/.bin/tsc -p tsconfig.json
```
