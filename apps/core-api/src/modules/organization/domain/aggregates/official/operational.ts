import type { OfficialArtifact } from './official-artifact';
import type {
  OfficialProcessId,
  OfficialWorkflowId,
  OfficialCapabilityId,
  OfficialApprovalChainId,
  DepartmentId,
} from '../../value-objects/ids';
import type { Cadence } from '../../value-objects/enums';
import type { OfficialWorkflowStep } from '../../entities/official-workflow-step';
import type { Timestamp } from '@oi/contracts';

/**
 * **Aggregate Root.** A declared business process. Compared against discovered
 * processes → future Process-Drift detection.
 */
export interface OfficialProcess extends OfficialArtifact<'Process'> {
  readonly id: OfficialProcessId;
  readonly ownerDepartmentId: DepartmentId;
  readonly deliveredCapabilityIds: readonly OfficialCapabilityId[];
  readonly cadence?: Cadence;
}

/**
 * **Aggregate Root.** A declared workflow (the SOP as written). Must have an owner
 * Department (ORG4). Its steps vs discovered workflow activities → future
 * SOP-Deviation / Workflow-Drift detection.
 */
export interface OfficialWorkflow extends OfficialArtifact<'Workflow'> {
  readonly id: OfficialWorkflowId;
  readonly ownerDepartmentId: DepartmentId;
  readonly processId?: OfficialProcessId;
  readonly steps: readonly OfficialWorkflowStep[];
  readonly approvalChainId?: OfficialApprovalChainId;
  readonly publishedAt?: Timestamp;
}
