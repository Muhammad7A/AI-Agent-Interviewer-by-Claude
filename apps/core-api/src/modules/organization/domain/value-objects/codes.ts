import type { Brand } from '@oi/contracts';
import type { BusinessUnitId, DepartmentId, TeamId } from './ids';

/** A human-facing department code (e.g. "FIN-001"). */
export type DepartmentCode = Brand<string, 'DepartmentCode'>;

/** A generic org-unit code, used by business units and teams. */
export type OrgUnitCode = Brand<string, 'OrgUnitCode'>;

/** An HR employee number. */
export type EmployeeNumber = Brand<string, 'EmployeeNumber'>;

/** The kind of org unit — the discriminant across the BU/Department/Team hierarchy. */
export type OrgUnitKind = 'BusinessUnit' | 'Department' | 'Team';

/**
 * A polymorphic reference to any org unit (a parent pointer up the hierarchy),
 * discriminated by `kind`.
 */
export type OrgUnitIdentifier =
  | { readonly kind: 'BusinessUnit'; readonly id: BusinessUnitId }
  | { readonly kind: 'Department'; readonly id: DepartmentId }
  | { readonly kind: 'Team'; readonly id: TeamId };
