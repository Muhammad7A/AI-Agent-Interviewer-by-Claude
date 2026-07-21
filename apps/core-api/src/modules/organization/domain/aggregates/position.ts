import type {
  PositionId,
  OrganizationId,
  DepartmentId,
  TeamId,
  OfficialRoleId,
} from '../value-objects/ids';
import type { PositionLevel } from '../value-objects/levels';
import type { OrgLifecycleStatus } from '../value-objects/enums';
import type { EffectivePeriod } from '../value-objects/temporal';

/**
 * **Aggregate Root.** An official position — a job *slot* in the org chart, filled
 * by at most one employee. Reporting is position-based (see `ReportingLine`),
 * which keeps the official structure stable as people move and supports future
 * Role-Drift detection (official `officialRoleId` vs the role discovered in
 * interviews).
 */
export interface Position {
  readonly id: PositionId;
  readonly organizationId: OrganizationId;
  readonly departmentId: DepartmentId;
  readonly teamId?: TeamId;
  readonly title: string;
  readonly officialRoleId?: OfficialRoleId;
  readonly level: PositionLevel;
  readonly isManagerial: boolean;
  readonly status: OrgLifecycleStatus;
  readonly effectivePeriod: EffectivePeriod;
}
