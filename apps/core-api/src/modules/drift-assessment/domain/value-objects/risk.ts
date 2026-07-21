import type { Score } from '@oi/contracts';
import type { RiskLevel } from '@oi/insights';

/** Re-exported from Insights' Published Language — one shared risk scale, not a duplicate. */
export type { RiskLevel };

/**
 * A risk assessment for a drift finding or gap: the banded `RiskLevel` (reused
 * from Insights) decomposed into likelihood and impact, with a rationale.
 */
export interface RiskAssessment {
  readonly level: RiskLevel;
  readonly likelihood: Score;
  readonly impact: Score;
  readonly rationale: string;
}
