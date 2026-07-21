import type { DriftClassification } from '../value-objects/policy-results';
import type { GapFrequency } from '../value-objects/gap-scales';
import type { GapScore } from '../value-objects/policy-results';

/**
 * **Domain service (port).** Turns a drift classification and observed frequency
 * into a scored, severity-banded gap. Interface only.
 */
export interface GapScoringPolicy {
  score(classification: DriftClassification, frequency: GapFrequency): GapScore;
}
