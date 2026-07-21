/**
 * Insights context — **Published Language**.
 *
 * The curated surface downstream contexts (Reporting, Consultant Workspace) may
 * depend on: the diagnostic/opportunity/synthesis node contracts, the confirmed
 * `Finding`, the scoring/classification value objects, and the analytics read
 * models. The interpretation internals — `Observation`, policies, repository
 * ports, domain events, entities — are deliberately excluded.
 */

// Node type catalog + typed graph-node contracts and their attributes/unions.
export type {
  InsightsNodeType,
  DiagnosticNodeType,
  OpportunityNodeType,
  SynthesisNodeType,
} from './nodes/node-type';
export * from './nodes';

// The confirmed interpretation unit that recommendations rest on.
export type { Finding } from './aggregates/finding';

// Scoring / classification value objects consumers need to render insights.
export type {
  Severity,
  Frequency,
  BusinessImpact,
  Urgency,
  RiskLevel,
  BusinessValue,
  ImplementationComplexity,
} from './value-objects/scales';
export type { PainCategory, PainNature, DiagnosticOrigin } from './value-objects/classification';
export type { AiPattern, SignalType } from './value-objects/taxonomies';
export type { OpportunityScore } from './value-objects/opportunity-score';
export type { RecommendationPriority, PriorityTier } from './value-objects/recommendation-priority';
export type { DiagnosticConfidence, RootCauseConfidence } from './value-objects/confidence';
export type { KnowledgeArtifactRef } from './value-objects/knowledge-artifact-ref';

// Analytics read models — the consultant-facing answers.
export * from './read-models';
