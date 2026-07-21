import type { ValidationEventId } from '../primitives/ids';
import type { ActorRef } from '../primitives/actor';
import type { Timestamp } from '../primitives/scalars';
import type { ValidationState } from './validation-state';

/**
 * An audited transition in an artifact's validation lifecycle. Every change of
 * `ValidationState` is recorded as one of these — who, when, from/to, and why —
 * forming the human-in-the-loop audit trail.
 */
export interface ValidationEvent {
  readonly id: ValidationEventId;
  readonly actor: ActorRef;
  readonly before: ValidationState;
  readonly after: ValidationState;
  readonly reason?: string;
  readonly at: Timestamp;
}
