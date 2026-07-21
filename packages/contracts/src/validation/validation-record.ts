import type { ValidationEventId } from '../primitives/ids';
import type { ValidationState } from './validation-state';

/**
 * The current validation standing of an artifact.
 *
 * `isAnchor` marks consultant-confirmed truth (`Validated` / `ConsultantAdded`)
 * that machine recompute must never overwrite (invariant N4 / G5). Human
 * judgment, once given, is protected.
 */
export interface ValidationRecord {
  readonly state: ValidationState;
  readonly isAnchor: boolean;
  /** The most recent transition, if any. */
  readonly lastEventId?: ValidationEventId;
}
