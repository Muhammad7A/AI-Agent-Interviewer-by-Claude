import type { OfficialArtifact } from './official-artifact';
import type {
  OfficialRoleId,
  OfficialCapabilityId,
  OfficialSystemId,
  DepartmentId,
} from '../../value-objects/ids';
import type { PositionLevel } from '../../value-objects/levels';
import type { OwnerRef } from '../../value-objects/refs';

/**
 * **Aggregate Root.** A declared role definition (the job-description catalog).
 * Compared against roles discovered in interviews → future Role-Drift detection.
 */
export interface OfficialRole extends OfficialArtifact<'Role'> {
  readonly id: OfficialRoleId;
  readonly title: string;
  readonly level?: PositionLevel;
  readonly ownerDepartmentId?: DepartmentId;
  readonly description?: string;
}

/**
 * **Aggregate Root.** A declared business capability. Must have an owner (ORG5).
 * Absence of a discovered counterpart → future Capability-Gap detection.
 */
export interface OfficialCapability extends OfficialArtifact<'Capability'> {
  readonly id: OfficialCapabilityId;
  readonly owner: OwnerRef;
  readonly description?: string;
}

/**
 * **Aggregate Root.** A declared/sanctioned system. Discovered systems with no
 * official counterpart → future Shadow-IT detection.
 */
export interface OfficialSystem extends OfficialArtifact<'System'> {
  readonly id: OfficialSystemId;
  readonly vendor?: string;
  readonly ownerDepartmentId?: DepartmentId;
}
