import type {
  EmployeeId,
  OrganizationId,
  DepartmentId,
  PositionId,
  LocationId,
  LegalEntityId,
} from '../value-objects/ids';
import type { EmployeeNumber } from '../value-objects/codes';
import type { EmploymentType, OrgLifecycleStatus } from '../value-objects/enums';
import type { EffectivePeriod } from '../value-objects/temporal';

/**
 * **Aggregate Root.** An officially-recorded employee. Belongs to **exactly one**
 * Department (ORG1). Holds at most one Position. This is declared HR truth — a
 * person as the organization records them, distinct from the pseudonymized,
 * discovered `Person`/`IntervieweeRef` in the Knowledge/Transcript contexts.
 */
export interface Employee {
  readonly id: EmployeeId;
  readonly organizationId: OrganizationId;
  readonly employeeNumber: EmployeeNumber;
  readonly departmentId: DepartmentId;
  readonly positionId?: PositionId;
  readonly employmentType: EmploymentType;
  readonly locationId?: LocationId;
  readonly legalEntityId?: LegalEntityId;
  readonly status: OrgLifecycleStatus;
  readonly effectivePeriod: EffectivePeriod;
}
