import type { Brand } from '@oi/contracts';

/**
 * Organization-context identities. `OrganizationId` (== `TenantId`) and
 * `EngagementId` are **owned by the Shared Kernel** and reused (not redefined) —
 * Organization is the context that gives them meaning and publishes them as the
 * platform's scope keys. The rest are new official-structure identities reusing
 * the kernel's `Brand`.
 */
export type { OrganizationId, TenantId, EngagementId } from '@oi/contracts';

export type LegalEntityId = Brand<string, 'LegalEntityId'>;
export type LocationId = Brand<string, 'LocationId'>;
export type BusinessUnitId = Brand<string, 'BusinessUnitId'>;
export type DepartmentId = Brand<string, 'DepartmentId'>;
export type TeamId = Brand<string, 'TeamId'>;
export type PositionId = Brand<string, 'PositionId'>;
export type EmployeeId = Brand<string, 'EmployeeId'>;
export type ReportingLineId = Brand<string, 'ReportingLineId'>;

export type OfficialProcessId = Brand<string, 'OfficialProcessId'>;
export type OfficialCapabilityId = Brand<string, 'OfficialCapabilityId'>;
export type OfficialSystemId = Brand<string, 'OfficialSystemId'>;
export type OfficialPolicyId = Brand<string, 'OfficialPolicyId'>;
export type OfficialRoleId = Brand<string, 'OfficialRoleId'>;
export type OfficialWorkflowId = Brand<string, 'OfficialWorkflowId'>;
export type OfficialApprovalChainId = Brand<string, 'OfficialApprovalChainId'>;

/** Local identities of child entities. */
export type WorkflowStepId = Brand<string, 'WorkflowStepId'>;
export type ApprovalStepId = Brand<string, 'ApprovalStepId'>;
