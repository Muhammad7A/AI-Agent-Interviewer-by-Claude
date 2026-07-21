/**
 * The explicit result of a use case. Handlers return `Result<T>` rather than
 * throwing for expected failures, so callers (and tests) handle outcomes without
 * exception control-flow. Contracts only — no constructors here.
 */
export type Result<T> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: AppError };

/** The categories of expected application failure. */
export type AppErrorKind =
  | 'Validation'
  | 'NotFound'
  | 'Unauthorized'
  | 'Conflict'
  | 'ScopeMismatch'
  | 'Idempotent'
  | 'AiUnavailable'
  | 'Cancelled'
  | 'Unexpected';

/** A structured application error carried by a failed `Result`. */
export interface AppError {
  readonly kind: AppErrorKind;
  readonly message: string;
  readonly details?: Readonly<Record<string, unknown>>;
}
