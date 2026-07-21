import type { EventId, TenantId, EngagementId } from '../primitives/ids';
import type { ActorRef } from '../primitives/actor';
import type { Timestamp } from '../primitives/scalars';

/**
 * The envelope every domain event shares.
 *
 * Events are how graph-wide operations stay eventually consistent (ADR-0006) and
 * how the reasoning pipeline is choreographed across contexts. Every event is
 * scoped to a tenant and engagement. `actor` is present for human-originated
 * events and absent for machine-originated ones.
 *
 * @typeParam TType    - the event's discriminant string (e.g. `"knowledge.node.added"`).
 * @typeParam TPayload - the event-specific payload shape.
 */
export interface DomainEvent<TType extends string = string, TPayload = unknown> {
  readonly eventId: EventId;
  readonly eventType: TType;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly occurredAt: Timestamp;
  readonly actor?: ActorRef;
  readonly payload: TPayload;
}
