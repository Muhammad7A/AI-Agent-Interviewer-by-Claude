import type { GapSeverity, GapFrequency } from '../value-objects/gap-scales';
import type { RiskAssessment } from '../value-objects/risk';

/**
 * **Domain service (port).** Assesses the business risk of a gap/finding from its
 * severity and frequency, producing an explainable `RiskAssessment` (the input to
 * `RiskEscalated`). Interface only.
 */
export interface AlignmentRiskPolicy {
  assess(severity: GapSeverity, frequency: GapFrequency): RiskAssessment;
}
