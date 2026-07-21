import type {
  OrganizationId,
  BusinessUnitId,
  DepartmentId,
  TeamId,
  LegalEntityId,
  LocationId,
} from '../value-objects/ids';
import type { OrgUnitKind, DepartmentCode, OrgUnitCode } from '../value-objects/codes';
import type { OrgLifecycleStatus } from '../value-objects/enums';
import type { EffectivePeriod } from '../value-objects/temporal';
import type { Manager } from '../value-objects/refs';

/**
 * Common shape of every official org unit, discriminated by `kind`. Each unit
 * belongs to exactly one Organization (ORG2) and carries effective-dating so the
 * hierarchy is historically queryable (ORG9).
 */
export interface OrgUnit<K extends OrgUnitKind = OrgUnitKind> {
  readonly kind: K;
  readonly organizationId: OrganizationId;
  readonly name: string;
  readonly status: OrgLifecycleStatus;
  readonly effectivePeriod: EffectivePeriod;
  readonly manager?: Manager;
}

/** **Aggregate Root.** A top-level business unit (a division). */
export interface BusinessUnit extends OrgUnit<'BusinessUnit'> {
  readonly id: BusinessUnitId;
  readonly code?: OrgUnitCode;
  readonly legalEntityId?: LegalEntityId;
}

/** **Aggregate Root.** A department within a business unit (or directly under the org). */
export interface Department extends OrgUnit<'Department'> {
  readonly id: DepartmentId;
  readonly code: DepartmentCode;
  readonly businessUnitId?: BusinessUnitId;
  readonly locationId?: LocationId;
}

/** **Aggregate Root.** A team within a department. */
export interface Team extends OrgUnit<'Team'> {
  readonly id: TeamId;
  readonly code?: OrgUnitCode;
  readonly departmentId: DepartmentId;
}

/** The discriminated union of every org-unit kind. */
export type AnyOrgUnit = BusinessUnit | Department | Team;
