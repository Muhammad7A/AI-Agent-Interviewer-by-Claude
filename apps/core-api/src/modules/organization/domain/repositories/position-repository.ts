import type { Timestamp } from '@oi/contracts';
import type { PositionId, OrganizationId, DepartmentId } from '../value-objects/ids';
import type { Position } from '../aggregates/position';

/** **Repository port** for `Position` aggregates. `asOf` supports historical queries (ORG9). */
export interface PositionRepository {
  findById(organizationId: OrganizationId, id: PositionId): Promise<Position | null>;
  save(position: Position): Promise<void>;
  findByDepartment(departmentId: DepartmentId, asOf?: Timestamp): Promise<readonly Position[]>;
  nextIdentity(): PositionId;
}
