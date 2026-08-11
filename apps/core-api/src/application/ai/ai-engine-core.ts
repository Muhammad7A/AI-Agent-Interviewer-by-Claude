import type { Timestamp } from '@oi/contracts';
import type { CancellationToken, Deadline } from '../shared/ports';

/**
 * The AI Engine ACL boundary — the *only* way the application reaches an LLM.
 * Infrastructure implements this later (calling the Python `ai-engine` / a Claude
 * adapter). Nothing here imports an SDK; nothing here returns a domain object.
 * Every output is a proposal a use case must map and validate before it becomes
 * domain state.
 */

/** Which model an adapter should use. Omitted on a request ⇒ the adapter's default (the latest Claude). */
export interface AiModelRef {
  readonly provider: string;
  readonly model: string;
  readonly version?: string;
}

/** Per-invocation tuning, including a timeout budget. */
export interface AiInvocationParams {
  readonly temperature?: number;
  readonly maxOutputTokens?: number;
  readonly deadline?: Deadline;
}

/** The AI capabilities the ACL brokers (mirrors the `ai-engine` capabilities). */
export type AiTaskType =
  | 'ClaimExtraction'
  | 'KnowledgeConstruction'
  | 'BottleneckDetection'
  | 'OpportunityDetection'
  | 'RecommendationSynthesis'
  | 'DriftDetection'
  | 'MappingResolution'
  | 'InterviewCognition';

/** A structured, cancellable request to the AI engine. */
export interface AiRequest<TInput> {
  readonly taskType: AiTaskType;
  readonly input: TInput;
  readonly model?: AiModelRef;
  readonly params?: AiInvocationParams;
  readonly correlationId: string;
  readonly cancellation?: CancellationToken;
}

/** Cost / token accounting returned with every successful call. */
export interface AiUsage {
  readonly inputTokens: number;
  readonly outputTokens: number;
  readonly costEstimateUsd?: number;
}

/**
 * The model's *raw* confidence hint (0..1) — **not** a domain `Confidence`. The
 * ACL/use case maps this into the kernel's computed, explainable `Confidence`
 * before it ever reaches domain state (evidence-first, no opaque certainty).
 */
export interface AiConfidenceHint {
  readonly score: number;
  readonly rationale?: string;
}

/** A structured, well-typed AI output plus its provenance metadata. */
export interface AiStructuredOutput<TOutput> {
  readonly output: TOutput;
  readonly confidence?: AiConfidenceHint;
  readonly model: AiModelRef;
  readonly usage: AiUsage;
  readonly producedAt: Timestamp;
}

/** The categories of AI failure the ACL surfaces. */
export type AiErrorKind =
  | 'Timeout'
  | 'RateLimited'
  | 'Cancelled'
  | 'InvalidOutput'
  | 'ContentFiltered'
  | 'ProviderUnavailable'
  | 'Unknown';

/** A structured AI error; `retryable` drives `RetryPolicy`. */
export interface AiEngineError {
  readonly kind: AiErrorKind;
  readonly message: string;
  readonly retryable: boolean;
}

/** Success or a structured error — never a thrown SDK exception across the boundary. */
export type AiResult<TOutput> =
  | { readonly ok: true; readonly value: AiStructuredOutput<TOutput> }
  | { readonly ok: false; readonly error: AiEngineError };

/** Retry configuration for a call, applied by the adapter. */
export interface RetryPolicy {
  readonly maxAttempts: number;
  readonly backoffMs: number;
  readonly retryableKinds: readonly AiErrorKind[];
}

/**
 * A schema-level validation hook the ACL runs on structured output before
 * returning it — the first gate that keeps malformed AI output out of the
 * application (the domain gate comes second, in the use case).
 */
export interface AiOutputValidator<TOutput> {
  isValid(output: TOutput): boolean;
}

/** The generic AI engine port. Task-specific ports (see `task-ports`) build on this. */
export interface AiEnginePort {
  invoke<TInput, TOutput>(request: AiRequest<TInput>, retry?: RetryPolicy): Promise<AiResult<TOutput>>;
}
