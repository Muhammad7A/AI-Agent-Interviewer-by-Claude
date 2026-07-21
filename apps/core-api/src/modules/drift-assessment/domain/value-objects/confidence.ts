import type { Confidence } from '@oi/contracts';

/**
 * Mapping confidences **reuse** the Shared Kernel's computed, explainable
 * `Confidence` (no duplication). Identity resolution is probabilistic, but the
 * requirement that it "remain explainable" is met by reusing the kernel's
 * factor-broken-down confidence rather than an opaque number.
 */

/** Confidence that a `MappingHypothesis` (discovered ↔ official) is correct. */
export type MappingConfidence = Confidence;

/** Confidence that a single `ReconciliationCandidate` is the right official match. */
export type ConfidenceOfMatch = Confidence;
