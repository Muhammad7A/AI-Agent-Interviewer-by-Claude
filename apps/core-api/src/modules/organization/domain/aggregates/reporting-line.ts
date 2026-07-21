import type { ReportingLineId, OrganizationId, PositionId } from '../value-objects/ids';
import type { ReportingLevel } from '../value-objects/levels';
import type { ReportingType, OrgLifecycleStatus } from '../value-objects/enums';
import type { EffectivePeriod } from '../value-objects/temporal';

/**
 * **Aggregate Root.** One edge of the official reporting hierarchy: a subordinate
 * position reports to a manager position. The full set of reporting lines must
 * form an **acyclic** graph (ORG3) — enforced by `ReportingLineAcyclicityPolicy`.
 *
 * Position-based (not employee-based) so the chain is stable across staffing
 * changes; `type` distinguishes solid (direct) from dotted (matrix) reporting.
 */
export interface ReportingLine {
  readonly id: ReportingLineId;
  readonly organizationId: OrganizationId;
  readonly subordinatePositionId: PositionId;
  readonly managerPositionId: PositionId;
  readonly reportingLevel: ReportingLevel;
  readonly type: ReportingType;
  readonly status: OrgLifecycleStatus;
  readonly effectivePeriod: EffectivePeriod;
}
