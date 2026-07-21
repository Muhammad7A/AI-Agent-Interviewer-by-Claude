# Organization context

The **declared** official structure of an organization — the source of
organizational *intent*. Knowledge holds the **discovered** reality; the gap
between the two is a primary business value. This context therefore holds **no
discovered facts** and does **not** use the evidence/confidence/validation model
— official data is *declared*, versioned, and effective-dated. See
`docs/DOMAIN_MODEL.md` §7.6 and ADR-0007.

**This slice is the `domain/` layer only — contracts, no behaviour.** No
persistence, infrastructure, application services, presentation, REST, DTO, or
GraphQL. It depends **only** on the Shared Kernel (`@oi/contracts`) and consumes
no other context's Published Language (it is the most upstream context).

## `domain/` layout

| Folder | Contents |
|---|---|
| `aggregates/` | `Organization`, `LegalEntity`, `Location`, `BusinessUnit`/`Department`/`Team`, `Position`, `Employee`, `ReportingLine`, `Engagement`, and `official/` (`OfficialProcess`, `OfficialCapability`, `OfficialSystem`, `OfficialPolicy`, `OfficialRole`, `OfficialWorkflow`, `OfficialApprovalChain` over an `OfficialArtifact` base). |
| `entities/` | `OfficialWorkflowStep`, `ApprovalStep`. |
| `value-objects/` | Ids; `DepartmentCode`, `EmployeeNumber`, `OrgUnitIdentifier`; `PositionLevel`, `ReportingLevel`, `ApprovalLevel`; `EmploymentType`, `OrganizationStatus`, `EngagementStatus`; `OrganizationVersion`, `EffectivePeriod`; `Manager`, `OwnerRef`, `DeclarationRecord`. |
| `repositories/` | Ports for Organization, org units, Position, Employee, ReportingLine, Engagement, and official artifacts (all with `asOf` for historical queries). |
| `services/` | Policy ports: `ReportingLineAcyclicityPolicy`, `OrgHierarchyIntegrityPolicy`, `DepartmentMergePolicy`, `OrganizationVersioningPolicy`. |
| `events/` | `OrganizationCreated`, `DepartmentCreated`/`Merged`/`Archived`, `EmployeeAssigned`/`Transferred`, `ManagerAssigned`, `ReportingLineChanged`, `WorkflowPublished`, `PolicyPublished`, `EngagementStarted`/`Completed`. |
| `invariants/` | `ORGANIZATION_INVARIANTS` (ORG1–ORG9). |
| `read-models/` | `OrgChartView`, `ReportingHierarchyView`, `DepartmentDirectory`, `GovernanceOwnershipView`, `DepartmentMembership`. |
| `published-language.ts` | Curated external surface (also *provides* `OrganizationId`/`EngagementId`). |

## Designed for future drift detection

The official artifacts carry stable identifiers, owners, and effective-dating so a
later domain can compare **official vs discovered**: Process/Role/Approval/Workflow
Drift, Shadow Org/Leadership/Workflow, Governance Gap, SOP Deviation, Ownership
Ambiguity, Capability Gap. That comparison logic is **not** in this context — only
the declared side it will compare against.

## Type-check

```bash
cd packages/contracts && npm install
cd ../../apps/core-api && ../../packages/contracts/node_modules/.bin/tsc -p tsconfig.json
```
