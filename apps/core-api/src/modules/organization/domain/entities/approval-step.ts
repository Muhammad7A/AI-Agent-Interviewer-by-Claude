import type { ApprovalStepId, PositionId, OfficialRoleId } from '../value-objects/ids';
import type { ApprovalLevel } from '../value-objects/levels';

/**
 * **Entity** within an `OfficialApprovalChain`. A declared approval gate.
 * Comparing the official chain against discovered approval behaviour is the
 * foundation of future Approval-Drift detection.
 */
export interface ApprovalStep {
  readonly id: ApprovalStepId;
  readonly order: number;
  readonly approverPositionId?: PositionId;
  readonly approverRoleId?: OfficialRoleId;
  readonly level: ApprovalLevel;
  readonly condition?: string;
}
