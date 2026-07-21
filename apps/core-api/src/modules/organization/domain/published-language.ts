/**
 * Organization context — **Published Language**.
 *
 * Organization is the most upstream context: it *provides* the scope keys
 * (`OrganizationId` == `TenantId`, `EngagementId`) and the declared official
 * structure, and consumes no other context's Published Language. Downstream
 * consumers (Reporting, Consultant Workspace, and a future drift-detection domain)
 * depend on the official structure, the engagement, and the read models below.
 *
 * Repository ports, policies, and domain events are internals and excluded.
 */

// Scope + identity.
export type { OrganizationId, EngagementId } from './value-objects/ids';

// Official structure — aggregate contracts (read shapes for consumers).
export type { Organization } from './aggregates/organization';
export type { LegalEntity, Location } from './aggregates/establishments';
export type { BusinessUnit, Department, Team, AnyOrgUnit } from './aggregates/org-units';
export type { Position } from './aggregates/position';
export type { Employee } from './aggregates/employee';
export type { ReportingLine } from './aggregates/reporting-line';
export type { Engagement } from './aggregates/engagement';
export * from './aggregates/official';

// Value objects consumers need to interpret the structure.
export type { OrgUnitKind, OrgUnitIdentifier, DepartmentCode } from './value-objects/codes';
export type { PositionLevel, ReportingLevel, ApprovalLevel } from './value-objects/levels';
export type {
  EmploymentType,
  OrganizationStatus,
  OrgLifecycleStatus,
  EngagementStatus,
  OfficialArtifactKind,
} from './value-objects/enums';
export type { OrganizationVersion, EffectivePeriod } from './value-objects/temporal';
export type { OwnerRef, Manager } from './value-objects/refs';

// Analytics / structural read models (the official side of future drift comparison).
export * from './read-models';
