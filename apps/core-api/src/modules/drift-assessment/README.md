# Drift / Assessment context

The platform's **comparative-intelligence** layer. It compares **declared** official
truth (Organization) against **discovered** reality (Knowledge / Transcript /
Insights) and owns only the *comparison*. It does not own either model — it
references both. This is where the platform's primary business value (the gap
between intent and reality) becomes concrete artifacts.

**This slice is the `domain/` layer only — contracts, no behaviour.** No
persistence, infrastructure, application services, presentation, or REST. It reads
**only** the Published Language of the Shared Kernel (`@oi/contracts`), Knowledge
(`@oi/knowledge`), Transcript (`@oi/transcript`), Insights (`@oi/insights`), and
Organization (`@oi/organization`) — and duplicates none of them.

## What it detects

Process / Role / Reporting / Approval / Workflow Drift, Ownership Ambiguity,
Shadow Organization, Shadow Leadership, Governance Gap, SOP Deviation, Capability
Gap, Organizational Misalignment — as `DriftFinding`s (matched pairs that diverge)
and `AlignmentGap`s (one side missing its counterpart).

## The identity-resolution seam

Official ids (`Employee`/`Position`/`Department`) and discovered refs
(`IntervieweeRef` / `RoleLabel` / `DepartmentLabel`) are bridged by
`MappingHypothesis` + `IdentityResolution` + `ReconciliationCandidate`:
**probabilistic, explainable, and a hypothesis until validated.** The platform
never forces an exact match (`Ambiguous` is a first-class outcome) and never
presents a mapping as truth before a consultant validates it.

## `domain/` layout

| Folder | Contents |
|---|---|
| `aggregates/` | `DriftAssessment`, `DriftFinding`, `AlignmentGap`, `MappingHypothesis`, `IdentityResolution`, `ComparisonRule`, `BaselineSnapshot`. |
| `entities/` | `ReconciliationCandidate`. |
| `value-objects/` | Ids; `OfficialElementRef`/`DiscoveredElementRef`; `DriftCategory`; `DriftScore`/`AlignmentScore`/`MaturityScore`/`ReadinessScore`; `GapSeverity`/`GapFrequency`; `MappingConfidence`/`ConfidenceOfMatch` (kernel `Confidence` aliases); `RiskAssessment` (+ reused `RiskLevel`); `ComparisonWindow`; `BaselineVersionRef`; policy results. |
| `repositories/` | Ports for every aggregate root (assessments/findings/gaps/mappings/resolutions/rules/baselines). |
| `services/` | Policy ports: `DriftClassificationPolicy`, `MappingResolutionPolicy`, `GapScoringPolicy`, `BaselineSelectionPolicy`, `AlignmentRiskPolicy`, `ReconciliationPrioritizationPolicy`. |
| `events/` | `DriftAssessmentStarted`, `MappingHypothesisProposed`/`Validated`/`Rejected`, `DriftDetected`, `DriftSeverityUpdated`, `AlignmentImproved`, `BaselineRecalculated`, `RiskEscalated`, `AssessmentCompleted`. |
| `invariants/` | `DRIFT_INVARIANTS` (DRIFT1–DRIFT8). |
| `read-models/` | Department misalignment, process-drift, ownership-ambiguity, contradicted-workflow, high-risk-gap rankings; uncertain-mapping list; assessment scorecard; evidence trace. |
| `published-language.ts` | Curated external surface. |

## A note on the reference seam

Organization publishes its aggregate *types* but not its branded id value objects,
so `value-objects/refs.ts` recovers official ids via **indexed access**
(`Department['id']`, `AnyOfficialArtifact['id']`) — referencing, never
duplicating, and without modifying Organization. See the "architectural seams"
note in the session summary; the clean fix (Organization publishing its id VOs) is
a future refinement, not applied here.

## Type-check

```bash
cd packages/contracts && npm install
cd ../../apps/core-api && ../../packages/contracts/node_modules/.bin/tsc -p tsconfig.json
```
