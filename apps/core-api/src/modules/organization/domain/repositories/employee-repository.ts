import type { Timestamp } from '@oi/contracts';
import type { EmployeeId, OrganizationId, DepartmentId } from '../value-objects/ids';
import type { EmployeeNumber } from '../value-objects/codes';
import type { Employee } from '../aggregates/employee';

/** **Repository port** for `Employee` aggregates. `asOf` supports historical queries (ORG9). */
export interface EmployeeRepository {
  findById(organizationId: OrganizationId, id: EmployeeId): Promise<Employee | null>;
  findByEmployeeNumber(organizationId: OrganizationId, number: EmployeeNumber): Promise<Employee | null>;
  save(employee: Employee): Promise<void>;
  findByDepartment(departmentId: DepartmentId, asOf?: Timestamp): Promise<readonly Employee[]>;
  nextIdentity(): EmployeeId;
}
