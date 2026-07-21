import type { OfficialArtifact } from './official-artifact';
import type {
  OfficialPolicyId,
  OfficialApprovalChainId,
  DepartmentId,
} from '../../value-objects/ids';
import type { ApprovalLevel } from '../../value-objects/levels';
import type { OwnerRef } from '../../value-objects/refs';
import type { ApprovalStep } from '../../entities/approval-step';
import type { Timestamp } from '@oi/contracts';

/**
 * **Aggregate Root.** A declared policy/SOP. Must have **at least one** owner
 * (ORG6). Discovered practice diverging from it → future SOP-Deviation /
 * Governance-Gap detection.
 */
export interface OfficialPolicy extends OfficialArtifact<'Policy'> {
  readonly id: OfficialPolicyId;
  readonly owners: readonly OwnerRef[];
  readonly approvalLevel?: ApprovalLevel;
  readonly publishedAt?: Timestamp;
}

/**
 * **Aggregate Root.** A declared approval chain — the official sign-off path. Its
 * steps vs discovered approval behaviour → future Approval-Drift detection.
 */
export interface OfficialApprovalChain extends OfficialArtifact<'ApprovalChain'> {
  readonly id: OfficialApprovalChainId;
  readonly ownerDepartmentId?: DepartmentId;
  readonly steps: readonly ApprovalStep[];
}
