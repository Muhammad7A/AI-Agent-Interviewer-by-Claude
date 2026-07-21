import type { TenantId, EngagementId, ActorRef, Timestamp } from '@oi/contracts';

/**
 * The envelope every **application** event shares. Distinct from the Shared
 * Kernel's domain `DomainEvent`: application events announce *use-case* outcomes
 * for integration and observability, and carry a `correlationId` tracing the
 * request across contexts. Domain events remain the source of intra-domain truth;
 * application events are the orchestration-level signal.
 */
export interface ApplicationEvent<TType extends string = string, TPayload = unknown> {
  readonly eventId: string;
  readonly eventType: TType;
  readonly tenantId: TenantId;
  readonly engagementId?: EngagementId;
  readonly occurredAt: Timestamp;
  readonly correlationId: string;
  readonly actor?: ActorRef;
  readonly payload: TPayload;
}
