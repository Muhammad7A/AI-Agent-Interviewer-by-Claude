import type { Brand, Timestamp, TenantId, EngagementId, ActorRef, DomainEvent } from '@oi/contracts';
import type { ApplicationEvent } from './application-event';

/* ------------------------------------------------------------------ *
 * Cross-cutting application ports. All are interfaces (contracts) that
 * infrastructure implements later; the application depends on these, never on
 * infrastructure directly.
 * ------------------------------------------------------------------ */

/** Cooperative cancellation for long-running (esp. AI) work. */
export interface CancellationToken {
  readonly isCancelled: boolean;
  throwIfCancelled(): void;
}

/** A wall-clock deadline / timeout budget. */
export interface Deadline {
  readonly timeoutMs: number;
}

/** Injectable time source — so handlers are deterministic under test. */
export interface Clock {
  now(): Timestamp;
}

/** A marker for the ambient transaction a `UnitOfWork` opens; repositories enlist in it via infrastructure. */
export interface TransactionScope {
  readonly transactionId: string;
}

/**
 * Transaction boundary abstraction. A handler wraps the writes that must commit
 * together in `run`. Note: per ADR-0006 the knowledge graph is eventually
 * consistent — a `UnitOfWork` bounds a *single aggregate* (or a small, same-store
 * set), not a graph-wide operation.
 */
export interface UnitOfWork {
  run<T>(work: (tx: TransactionScope) => Promise<T>): Promise<T>;
}

/** Publishes collected **domain** events (Shared Kernel `DomainEvent`) after a successful commit (outbox-friendly). */
export interface DomainEventPublisher {
  publish(events: readonly DomainEvent[]): Promise<void>;
}

/** Publishes **application** events (use-case outcomes). */
export interface ApplicationEventPublisher {
  publish(events: readonly ApplicationEvent[]): Promise<void>;
}

/** An idempotency key carried by a command so retries do not double-apply. */
export type IdempotencyKey = Brand<string, 'IdempotencyKey'>;

/** Records which command keys have been applied, so a handler can no-op on replay. */
export interface IdempotencyStore {
  has(key: IdempotencyKey): Promise<boolean>;
  remember(key: IdempotencyKey): Promise<void>;
}

/** The actions the authorization boundary guards. */
export type AppAction =
  | 'OpenEngagement'
  | 'StartTranscriptAnalysis'
  | 'ExtractClaims'
  | 'BuildKnowledgeGraph'
  | 'GenerateInsights'
  | 'DetectDrift'
  | 'ProduceReport'
  | 'ValidateRecommendation';

/** An authorization question: may this actor perform this action in this scope? */
export interface AuthorizationRequest {
  readonly actor: ActorRef;
  readonly action: AppAction;
  readonly tenantId: TenantId;
  readonly engagementId?: EngagementId;
}

/** The authorization decision. */
export type AuthorizationDecision =
  | { readonly allowed: true }
  | { readonly allowed: false; readonly reason: string };

/** The authorization boundary the application checks before mutating anything. */
export interface AuthorizationPort {
  authorize(request: AuthorizationRequest): Promise<AuthorizationDecision>;
}
