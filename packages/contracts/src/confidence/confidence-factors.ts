import type { Score } from '../primitives/scalars';

/**
 * The explainable decomposition behind a `Confidence` score. Confidence is
 * *computed* from these factors — never emitted opaquely by a model — so a
 * consultant can always see *why* something scored the way it did.
 */
export interface ConfidenceFactors {
  /** The extractor's confidence in the underlying claim. */
  readonly extraction: Score;
  /** Support from independent, agreeing sources. */
  readonly corroboration: Score;
  /** Authority of the source (e.g. describing one's own workflow). */
  readonly sourceAuthority: Score;
  /** Penalty from conflicting evidence. */
  readonly contradiction: Score;
  /** Decay with the depth of the inference chain. */
  readonly inferenceDepth: Score;
  /** Anchoring from consultant confirmation. */
  readonly humanValidation: Score;
}
