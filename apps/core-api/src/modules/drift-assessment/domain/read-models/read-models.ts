import type { DepartmentLabel } from '@oi/contracts';
import type { ResolvedEvidence } from '@oi/transcript';
import type {
  DriftFindingId,
  AlignmentGapId,
  MappingHypothesisId,
  DriftAssessmentId,
} from '../value-objects/ids';
import type { OfficialElementRef, DiscoveredElementRef } from '../value-objects/refs';
import type { DriftScore, AlignmentScore, MaturityScore, ReadinessScore } from '../value-objects/scores';
import type { GapSeverity } from '../value-objects/gap-scales';
import type { RiskAssessment } from '../value-objects/risk';
import type { ConfidenceBand } from '@oi/contracts';

/**
 * Read models — denormalized projections answering consultant-facing questions.
 * Shapes only; no query logic.
 */

/** "Which departments are most misaligned?" */
export interface DepartmentMisalignmentEntry {
  readonly department: OfficialElementRef;
  readonly departmentLabel?: DepartmentLabel;
  readonly alignmentScore: AlignmentScore;
  readonly findingCount: number;
  readonly rank: number;
}
export interface DepartmentMisalignmentRanking {
  readonly assessmentId: DriftAssessmentId;
  readonly entries: readonly DepartmentMisalignmentEntry[];
}

/** "Where is the largest process drift?" */
export interface ProcessDriftEntry {
  readonly findingId: DriftFindingId;
  readonly official: OfficialElementRef;
  readonly discovered: DiscoveredElementRef;
  readonly driftScore: DriftScore;
  readonly rank: number;
}
export interface ProcessDriftRanking {
  readonly assessmentId: DriftAssessmentId;
  readonly entries: readonly ProcessDriftEntry[];
}

/** "Which roles have the highest ownership ambiguity?" */
export interface OwnershipAmbiguityEntry {
  readonly official: OfficialElementRef;
  readonly ambiguityScore: DriftScore;
  readonly conflictingOwnerCount: number;
  readonly rank: number;
}
export interface RoleOwnershipAmbiguityRanking {
  readonly assessmentId: DriftAssessmentId;
  readonly entries: readonly OwnershipAmbiguityEntry[];
}

/** "Which official workflows are most contradicted by reality?" */
export interface ContradictedWorkflowEntry {
  readonly official: OfficialElementRef;
  readonly contradictingFindingIds: readonly DriftFindingId[];
  readonly driftScore: DriftScore;
  readonly rank: number;
}
export interface ContradictedWorkflowRanking {
  readonly assessmentId: DriftAssessmentId;
  readonly entries: readonly ContradictedWorkflowEntry[];
}

/** "Which gaps are high-risk and high-impact?" */
export interface HighRiskGapEntry {
  readonly gapId: AlignmentGapId;
  readonly severity: GapSeverity;
  readonly risk: RiskAssessment;
  readonly rank: number;
}
export interface HighRiskGapRanking {
  readonly assessmentId: DriftAssessmentId;
  readonly entries: readonly HighRiskGapEntry[];
}

/** "Which mappings are still uncertain?" */
export interface UncertainMappingEntry {
  readonly mappingId: MappingHypothesisId;
  readonly discovered: DiscoveredElementRef;
  readonly official: OfficialElementRef;
  readonly confidenceBand: ConfidenceBand;
}
export interface UncertainMappingList {
  readonly assessmentId: DriftAssessmentId;
  readonly entries: readonly UncertainMappingEntry[];
}

/** The assessment scorecard — the top-line alignment/maturity/readiness view. */
export interface AssessmentScorecard {
  readonly assessmentId: DriftAssessmentId;
  readonly overallAlignment: AlignmentScore;
  readonly maturity: MaturityScore;
  readonly readiness: ReadinessScore;
  readonly findingCount: number;
  readonly gapCount: number;
}

/**
 * The evidence drill-path behind a drift finding: resolved transcript quotes, via
 * Transcript's Published Language (`ResolvedEvidence`). Makes DRIFT4/DRIFT5
 * (traceable + explainable) visible to consultants.
 */
export interface DriftEvidenceTrace {
  readonly findingId: DriftFindingId;
  readonly quotes: readonly ResolvedEvidence[];
}
