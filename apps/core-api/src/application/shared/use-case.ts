import type { TenantId, EngagementId, ActorRef } from '@oi/contracts';
import type { Result } from './result';
import type { CancellationToken, IdempotencyKey } from './ports';

/**
 * The ambient context every use case executes within: resolved scope, the acting
 * identity, a correlation id for tracing across contexts, and optional
 * cancellation. Passed explicitly (never ambient/global) so handlers stay pure
 * and testable.
 */
export interface ExecutionContext {
  readonly tenantId: TenantId;
  readonly engagementId?: EngagementId;
  readonly actor: ActorRef;
  readonly correlationId: string;
  readonly cancellation?: CancellationToken;
}

/** The base contract for any use case: input + context → an explicit result. */
export interface UseCase<TInput, TOutput> {
  execute(input: TInput, ctx: ExecutionContext): Promise<Result<TOutput>>;
}

/** Marker base for write-side inputs. Commands may carry an idempotency key. */
export interface Command {
  readonly idempotencyKey?: IdempotencyKey;
}

/** Marker base for read-side inputs. */
export interface Query {
  readonly _query?: never;
}

/** A handler for a command (a state-changing use case). */
export interface CommandHandler<TCommand extends Command, TResult>
  extends UseCase<TCommand, TResult> {}

/** A handler for a query (a read-only use case). */
export interface QueryHandler<TQuery extends Query, TResult>
  extends UseCase<TQuery, TResult> {}
