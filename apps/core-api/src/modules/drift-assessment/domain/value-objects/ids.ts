import type { Brand } from '@oi/contracts';

/**
 * Drift/Assessment-context identities, reusing the Shared Kernel's `Brand`. This
 * context owns the *comparison* between official and discovered models, so its
 * ids name comparison artifacts — never the compared elements themselves (those
 * are referenced via `OfficialElementRef` / `DiscoveredElementRef`).
 */
export type DriftAssessmentId = Brand<string, 'DriftAssessmentId'>;
export type DriftFindingId = Brand<string, 'DriftFindingId'>;
export type AlignmentGapId = Brand<string, 'AlignmentGapId'>;
export type MappingHypothesisId = Brand<string, 'MappingHypothesisId'>;
export type IdentityResolutionId = Brand<string, 'IdentityResolutionId'>;
export type ComparisonRuleId = Brand<string, 'ComparisonRuleId'>;
export type BaselineSnapshotId = Brand<string, 'BaselineSnapshotId'>;
export type ReconciliationCandidateId = Brand<string, 'ReconciliationCandidateId'>;
