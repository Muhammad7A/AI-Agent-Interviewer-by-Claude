/**
 * Drift/Assessment context — **Published Language**.
 *
 * The comparative-intelligence surface downstream contexts (Reporting, Consultant
 * Workspace) depend on: assessments, findings, gaps, mappings, the scores, and
 * the analytics read models. Repository ports, policies, comparison rules, and
 * domain events are internals and excluded.
 */

// The comparison artifacts (read shapes).
export type { DriftAssessment, AssessmentStatus } from './aggregates/drift-assessment';
export type { DriftFinding } from './aggregates/drift-finding';
export type { AlignmentGap } from './aggregates/alignment-gap';
export type { MappingHypothesis } from './aggregates/mapping-hypothesis';
export type { IdentityResolution, ResolutionStatus } from './aggregates/identity-resolution';
export type { BaselineSnapshot } from './aggregates/baseline-snapshot';

// The comparison vocabulary + references.
export type { DriftCategory } from './value-objects/drift-category';
export type { OfficialElementRef, DiscoveredElementRef, ComparisonSide } from './value-objects/refs';
export type {
  DriftScore,
  AlignmentScore,
  MaturityScore,
  ReadinessScore,
  MaturityLevel,
  ReadinessLevel,
} from './value-objects/scores';
export type { GapSeverity, GapFrequency } from './value-objects/gap-scales';
export type { MappingConfidence, ConfidenceOfMatch } from './value-objects/confidence';
export type { RiskAssessment, RiskLevel } from './value-objects/risk';
export type { ComparisonWindow, BaselineVersionRef } from './value-objects/assessment-vos';

// Analytics read models — the consultant-facing answers.
export * from './read-models';
