import type { DriftCategory } from './drift-category';
import type { DriftScore } from './scores';
import type { GapSeverity } from './gap-scales';
import type { OfficialElementRef } from './refs';
import type { ConfidenceOfMatch } from './confidence';

/** The outcome of classifying one compared pair, produced by `DriftClassificationPolicy`. */
export interface DriftClassification {
  readonly category: DriftCategory;
  readonly isDrift: boolean;
  readonly driftScore: DriftScore;
  readonly rationale: string;
}

/** A scored gap, produced by `GapScoringPolicy`. */
export interface GapScore {
  readonly driftScore: DriftScore;
  readonly severity: GapSeverity;
}

/**
 * A proposed reconciliation match (an official candidate + confidence + reason),
 * produced by `MappingResolutionPolicy`. A value object with no identity — the
 * `IdentityResolution` aggregate turns accepted proposals into
 * `ReconciliationCandidate` entities.
 */
export interface ReconciliationProposal {
  readonly official: OfficialElementRef;
  readonly confidence: ConfidenceOfMatch;
  readonly rationale: string;
}
