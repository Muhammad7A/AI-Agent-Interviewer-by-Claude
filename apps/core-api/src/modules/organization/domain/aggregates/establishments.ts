import type { LegalEntityId, LocationId, OrganizationId } from '../value-objects/ids';
import type { EffectivePeriod } from '../value-objects/temporal';
import type { OrgLifecycleStatus } from '../value-objects/enums';

/**
 * **Aggregate Root.** A registered legal entity of the organization (a company
 * within a group). Employees and org units may be attached to a legal entity.
 */
export interface LegalEntity {
  readonly id: LegalEntityId;
  readonly organizationId: OrganizationId;
  readonly registeredName: string;
  readonly jurisdiction?: string;
  readonly registrationNumber?: string;
  readonly status: OrgLifecycleStatus;
  readonly effectivePeriod: EffectivePeriod;
}

/**
 * **Aggregate Root.** A physical or logical location (office, site, "remote").
 * Referenced by departments and employees.
 */
export interface Location {
  readonly id: LocationId;
  readonly organizationId: OrganizationId;
  readonly name: string;
  readonly country?: string;
  readonly city?: string;
  readonly status: OrgLifecycleStatus;
  readonly effectivePeriod: EffectivePeriod;
}
