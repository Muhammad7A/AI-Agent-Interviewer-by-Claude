import type { Confidence } from '@oi/contracts';

/**
 * Diagnostic confidences **reuse** the Shared Kernel's computed, explainable
 * `Confidence` (no duplication) — they are semantic aliases that name *what* the
 * confidence is about, while keeping one confidence model and its factor
 * breakdown across the whole platform.
 */

/** Confidence in a diagnostic interpretation (an observation, finding, or pain point). */
export type DiagnosticConfidence = Confidence;

/** Confidence in a root-cause hypothesis. */
export type RootCauseConfidence = Confidence;
