import type { Department } from '../aggregates/org-units';
import type { DepartmentId, PositionId, EmployeeId } from '../value-objects/ids';

/**
 * The plan produced when merging one department into another — a value object
 * describing intent (which positions/employees move, which department survives),
 * not its execution.
 */
export interface DepartmentMergePlan {
  readonly survivingDepartmentId: DepartmentId;
  readonly archivedDepartmentId: DepartmentId;
  readonly reassignedPositionIds: readonly PositionId[];
  readonly reassignedEmployeeIds: readonly EmployeeId[];
}

/**
 * **Domain service (port).** Plans a department merge (the `DepartmentMerged`
 * event), preserving the archived department for history (ORG9). Interface only.
 */
export interface DepartmentMergePolicy {
  planMerge(source: Department, target: Department): DepartmentMergePlan;
}
