import type { Score } from '@oi/contracts';

/** The strategic tier a recommendation falls into. */
export type PriorityTier = 'QuickWin' | 'Strategic' | 'Foundational' | 'Deferred';

/**
 * A computed, explainable priority for a `Recommendation`. Reuses the Shared
 * Kernel `Score` for the ranking scalar.
 */
export interface RecommendationPriority {
  readonly tier: PriorityTier;
  readonly value: Score;
  readonly rationale: string;
}

/**
 * Tunable weights for prioritization — the Strategy inputs a firm sets per
 * engagement. Reuses `Score` for each weight.
 */
export interface PrioritizationWeights {
  readonly businessValueWeight: Score;
  readonly urgencyWeight: Score;
  readonly complexityWeight: Score;
  readonly riskWeight: Score;
}
