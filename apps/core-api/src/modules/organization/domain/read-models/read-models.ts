import type { Timestamp } from '@oi/contracts';
import type {
  OrganizationId,
  DepartmentId,
  PositionId,
  EmployeeId,
} from '../value-objects/ids';
import type { OrgUnitIdentifier } from '../value-objects/codes';
import type { OfficialArtifactKind } from '../value-objects/enums';
import type { OrganizationVersion } from '../value-objects/temporal';
import type { OwnerRef } from '../value-objects/refs';

/**
 * Read models — denormalized projections of the *declared* organization. They are
 * deliberately shaped to be the official side of a future official-vs-discovered
 * comparison (drift detection lives in a later context, not here).
 */

/** The official org chart at a point in time — the hierarchy of units. */
export interface OrgChartNode {
  readonly unit: OrgUnitIdentifier;
  readonly name: string;
  readonly parent?: OrgUnitIdentifier;
  readonly headPositionId?: PositionId;
}
export interface OrgChartView {
  readonly organizationId: OrganizationId;
  readonly asOf: Timestamp;
  readonly version: OrganizationVersion;
  readonly nodes: readonly OrgChartNode[];
}

/** The position reporting tree — the official chain, edge by edge. */
export interface ReportingHierarchyEdge {
  readonly subordinatePositionId: PositionId;
  readonly managerPositionId: PositionId;
}
export interface ReportingHierarchyView {
  readonly organizationId: OrganizationId;
  readonly edges: readonly ReportingHierarchyEdge[];
}

/** Departments with their head and headcount — the directory. */
export interface DepartmentDirectoryEntry {
  readonly departmentId: DepartmentId;
  readonly name: string;
  readonly headPositionId?: PositionId;
  readonly employeeCount: number;
}
export interface DepartmentDirectory {
  readonly organizationId: OrganizationId;
  readonly entries: readonly DepartmentDirectoryEntry[];
}

/**
 * Who officially owns what — the governance ownership matrix. This is the
 * declared-side foundation for future Governance-Gap and Ownership-Ambiguity
 * detection (e.g. an artifact with no owner, or discovered ownership that differs
 * from the declared owner).
 */
export interface GovernanceOwnershipEntry {
  readonly artifactKind: OfficialArtifactKind;
  readonly artifactName: string;
  readonly owners: readonly OwnerRef[];
}
export interface GovernanceOwnershipView {
  readonly organizationId: OrganizationId;
  readonly entries: readonly GovernanceOwnershipEntry[];
}

/** A member of a department at a point in time (supports historical queries, ORG9). */
export interface DepartmentMembership {
  readonly departmentId: DepartmentId;
  readonly employeeIds: readonly EmployeeId[];
  readonly asOf: Timestamp;
}
