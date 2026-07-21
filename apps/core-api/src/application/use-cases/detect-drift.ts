import type { EngagementId, OrganizationId, Timestamp } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * **Priority use case #3.** Compare official structure against discovered reality
 * and produce a drift assessment.
 *
 * Orchestration (implementation — comparison rules live in Drift policies):
 *  1. `AuthorizationPort` (DetectDrift); verify engagement/organization scopes are
 *     compatible (DRIFT6) → else `AppError('ScopeMismatch')`.
 *  2. Baseline: `BaselineSelectionPolicy` → capture/reuse a `BaselineSnapshot`
 *     pinning the `OrganizationVersion` (DRIFT2, reproducible history DRIFT7).
 *  3. Load official structure (Organization repos) + discovered graph (Knowledge
 *     `KnowledgeGraphLens`).
 *  4. Identity resolution: `MappingResolutionPort` (AI ACL) → suggestions →
 *     `MappingHypothesis` candidates (`Proposed`, hypothesis-until-validated).
 *     Persist (Drift `MappingHypothesisRepository`). **Never assert a mapping as truth.**
 *  5. For each enabled `ComparisonRule`: `DriftClassificationPolicy` →
 *     `DriftFinding` (paired) / `AlignmentGap` (one-sided), each `Proposed` and
 *     scored (`GapScoringPolicy`, `AlignmentRiskPolicy`), carrying traceable
 *     `EvidenceRef`s (DRIFT4).
 *  6. Persist assessment + findings + gaps (Drift repos); publish DriftDetected /
 *     AssessmentCompleted + application event (DriftAssessmentProduced).
 */
export interface DetectDriftCommand extends Command {
  readonly engagementId: EngagementId;
  readonly organizationId: OrganizationId;
  readonly comparisonFromInclusive: Timestamp;
  readonly comparisonToInclusive: Timestamp;
  /** Omit to auto-select the baseline effective during the comparison window. */
  readonly baselineOrganizationVersion?: number;
}

export interface DetectDriftResult {
  readonly assessmentId: string;
  readonly findingCount: number;
  readonly gapCount: number;
  readonly proposedMappingCount: number;
  readonly unresolvedMappingCount: number;
}

export interface DetectDriftHandler
  extends CommandHandler<DetectDriftCommand, DetectDriftResult> {}
