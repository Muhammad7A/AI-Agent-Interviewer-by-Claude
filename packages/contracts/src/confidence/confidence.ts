import type { Score } from '../primitives/scalars';
import type { ConfidenceBand } from './confidence-band';
import type { ConfidenceFactors } from './confidence-factors';

/**
 * A computed, explainable confidence value carried by every node and edge.
 *
 * Confidence is **orthogonal to validation status**: AI-confidence and
 * human-verification are independent axes. A fact may be high-confidence yet
 * unvalidated, or low-confidence yet consultant-validated — the model keeps both
 * dimensions separate (see `ValidationRecord`).
 */
export interface Confidence {
  /** Scalar in [0, 1], used for ranking. */
  readonly score: Score;
  /** Coarse band for display. */
  readonly band: ConfidenceBand;
  /** The factor breakdown that produced the score. */
  readonly factors: ConfidenceFactors;
  /** Human-readable "why this score". */
  readonly rationale: string;
}
