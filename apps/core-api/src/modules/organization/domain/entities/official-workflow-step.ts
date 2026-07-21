import type { WorkflowStepId, PositionId, OfficialRoleId, OfficialSystemId } from '../value-objects/ids';
import type { ApprovalLevel } from '../value-objects/levels';

/**
 * **Entity** within an `OfficialWorkflow`. A declared step in the official
 * procedure — the SOP as written. Comparing these against discovered workflow
 * activities is the foundation of future SOP-Deviation / Workflow-Drift detection.
 */
export interface OfficialWorkflowStep {
  readonly id: WorkflowStepId;
  readonly order: number;
  readonly name: string;
  readonly responsiblePositionId?: PositionId;
  readonly responsibleRoleId?: OfficialRoleId;
  readonly systemId?: OfficialSystemId;
  readonly approvalLevel?: ApprovalLevel;
}
