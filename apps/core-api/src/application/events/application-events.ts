import type { EngagementId, TranscriptId } from '@oi/contracts';
import type { ApplicationEvent } from '../shared/application-event';

/**
 * Application events — use-case outcomes published for integration/observability.
 * They carry the request `correlationId` (via the `ApplicationEvent` envelope) and
 * are distinct from the contexts' domain events.
 */

export type EngagementOpened = ApplicationEvent<
  'app.engagement.opened',
  { readonly engagementId: EngagementId }
>;

export type TranscriptAnalysisStarted = ApplicationEvent<
  'app.transcript-analysis.started',
  { readonly transcriptId: TranscriptId; readonly acceptedClaimCount: number }
>;

export type KnowledgeGraphUpdated = ApplicationEvent<
  'app.knowledge-graph.updated',
  { readonly engagementId: EngagementId; readonly nodesAdded: number; readonly edgesAdded: number }
>;

export type InsightsGenerated = ApplicationEvent<
  'app.insights.generated',
  { readonly engagementId: EngagementId; readonly recommendationCount: number }
>;

export type DriftAssessmentProduced = ApplicationEvent<
  'app.drift.assessment-produced',
  { readonly engagementId: EngagementId; readonly assessmentId: string; readonly findingCount: number }
>;

export type ConsultantReportProduced = ApplicationEvent<
  'app.report.produced',
  { readonly engagementId: EngagementId; readonly reportId: string }
>;

export type RecommendationValidated = ApplicationEvent<
  'app.recommendation.validated',
  { readonly engagementId: EngagementId; readonly recommendationId: string }
>;

/** Discriminated union of all platform application events. */
export type PlatformApplicationEvent =
  | EngagementOpened
  | TranscriptAnalysisStarted
  | KnowledgeGraphUpdated
  | InsightsGenerated
  | DriftAssessmentProduced
  | ConsultantReportProduced
  | RecommendationValidated;
