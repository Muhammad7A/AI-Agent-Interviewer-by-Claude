import type { ActorRef, Timestamp } from '@oi/contracts';
import type { PositionId, EmployeeId, DepartmentId } from './ids';

/**
 * The manager of an org unit or the top of a reporting line, expressed by
 * *position* first (official org charts are position-based, which supports future
 * Role-Drift detection), optionally resolved to the employee holding it.
 */
export interface Manager {
  readonly positionId: PositionId;
  readonly employeeId?: EmployeeId;
}

/** Who officially owns an official artifact, discriminated by `kind`. */
export type OwnerRef =
  | { readonly kind: 'Department'; readonly departmentId: DepartmentId }
  | { readonly kind: 'Position'; readonly positionId: PositionId }
  | { readonly kind: 'Employee'; readonly employeeId: EmployeeId };

/**
 * Provenance of a *declaration* (distinct from interview evidence — official data
 * is declared, not discovered). Records who/what asserted the record and when.
 * Reuses the Shared Kernel `ActorRef`.
 */
export interface DeclarationRecord {
  readonly declaredBy?: ActorRef;
  readonly sourceSystem?: string;
  readonly declaredAt: Timestamp;
}
