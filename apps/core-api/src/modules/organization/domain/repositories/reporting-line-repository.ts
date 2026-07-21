import type { Timestamp } from '@oi/contracts';
import type { ReportingLineId, OrganizationId, PositionId } from '../value-objects/ids';
import type { ReportingLine } from '../aggregates/reporting-line';

/**
 * **Repository port** for `ReportingLine` aggregates. `findAllActive` returns the
 * lines an acyclicity check runs over. `asOf` supports historical queries (ORG9).
 */
export interface ReportingLineRepository {
  findById(organizationId: OrganizationId, id: ReportingLineId): Promise<ReportingLine | null>;
  save(line: ReportingLine): Promise<void>;
  findAllActive(organizationId: OrganizationId, asOf?: Timestamp): Promise<readonly ReportingLine[]>;
  findByManagerPosition(managerPositionId: PositionId): Promise<readonly ReportingLine[]>;
  nextIdentity(): ReportingLineId;
}
