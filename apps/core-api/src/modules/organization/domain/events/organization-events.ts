import type { DomainEvent } from '@oi/contracts';
import type {
  OrganizationId,
  DepartmentId,
  EmployeeId,
  PositionId,
  ReportingLineId,
  OfficialWorkflowId,
  OfficialPolicyId,
  EngagementId,
} from '../value-objects/ids';
import type { OrganizationVersion } from '../value-objects/temporal';

/**
 * Organization-context domain events, all extending the Shared Kernel
 * `DomainEvent` envelope. Structural changes bump the `OrganizationVersion` (ORG8),
 * so relevant events carry the resulting version.
 */

export type OrganizationCreated = DomainEvent<
  'organization.created',
  { readonly organizationId: OrganizationId }
>;

export type DepartmentCreated = DomainEvent<
  'organization.department.created',
  { readonly departmentId: DepartmentId; readonly version: OrganizationVersion }
>;

export type DepartmentMerged = DomainEvent<
  'organization.department.merged',
  {
    readonly survivingDepartmentId: DepartmentId;
    readonly archivedDepartmentId: DepartmentId;
    readonly version: OrganizationVersion;
  }
>;

export type DepartmentArchived = DomainEvent<
  'organization.department.archived',
  { readonly departmentId: DepartmentId; readonly version: OrganizationVersion }
>;

export type EmployeeAssigned = DomainEvent<
  'organization.employee.assigned',
  { readonly employeeId: EmployeeId; readonly departmentId: DepartmentId; readonly positionId?: PositionId }
>;

export type EmployeeTransferred = DomainEvent<
  'organization.employee.transferred',
  {
    readonly employeeId: EmployeeId;
    readonly fromDepartmentId: DepartmentId;
    readonly toDepartmentId: DepartmentId;
  }
>;

export type ManagerAssigned = DomainEvent<
  'organization.manager.assigned',
  { readonly positionId: PositionId; readonly managerPositionId: PositionId }
>;

export type ReportingLineChanged = DomainEvent<
  'organization.reporting-line.changed',
  { readonly reportingLineId: ReportingLineId }
>;

export type WorkflowPublished = DomainEvent<
  'organization.workflow.published',
  { readonly workflowId: OfficialWorkflowId; readonly version: OrganizationVersion }
>;

export type PolicyPublished = DomainEvent<
  'organization.policy.published',
  { readonly policyId: OfficialPolicyId; readonly version: OrganizationVersion }
>;

export type EngagementStarted = DomainEvent<
  'organization.engagement.started',
  { readonly engagementId: EngagementId; readonly baselineVersion?: OrganizationVersion }
>;

export type EngagementCompleted = DomainEvent<
  'organization.engagement.completed',
  { readonly engagementId: EngagementId }
>;

/** Discriminated union of the Organization context's domain events. */
export type OrganizationDomainEvent =
  | OrganizationCreated
  | DepartmentCreated
  | DepartmentMerged
  | DepartmentArchived
  | EmployeeAssigned
  | EmployeeTransferred
  | ManagerAssigned
  | ReportingLineChanged
  | WorkflowPublished
  | PolicyPublished
  | EngagementStarted
  | EngagementCompleted;
