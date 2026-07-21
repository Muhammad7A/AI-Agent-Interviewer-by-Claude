import type { DomainEvent, KnowledgeNodeId } from '@oi/contracts';
import type { ObservationId, FindingId } from '../value-objects/ids';
import type { PainCategory } from '../value-objects/classification';
import type { AiPattern } from '../value-objects/taxonomies';

/** Insights-context domain events, all extending the Shared Kernel `DomainEvent` envelope. */

export type ObservationCreated = DomainEvent<
  'insights.observation.created',
  { readonly observationId: ObservationId }
>;

export type FindingConfirmed = DomainEvent<
  'insights.finding.confirmed',
  { readonly findingId: FindingId; readonly supportingObservationIds: readonly ObservationId[] }
>;

export type PainPointDetected = DomainEvent<
  'insights.painpoint.detected',
  { readonly painPointId: KnowledgeNodeId; readonly category: PainCategory }
>;

export type OpportunityDetected = DomainEvent<
  'insights.opportunity.detected',
  { readonly opportunityId: KnowledgeNodeId; readonly aiPattern: AiPattern }
>;

export type RecommendationProposed = DomainEvent<
  'insights.recommendation.proposed',
  { readonly recommendationId: KnowledgeNodeId }
>;

export type RecommendationRejected = DomainEvent<
  'insights.recommendation.rejected',
  { readonly recommendationId: KnowledgeNodeId; readonly reason: string }
>;

export type RecommendationAccepted = DomainEvent<
  'insights.recommendation.accepted',
  { readonly recommendationId: KnowledgeNodeId }
>;

export type DiagnosticClusterMerged = DomainEvent<
  'insights.cluster.merged',
  { readonly survivingClusterId: KnowledgeNodeId; readonly mergedClusterIds: readonly KnowledgeNodeId[] }
>;

/** Discriminated union of the Insights context's domain events. */
export type InsightsDomainEvent =
  | ObservationCreated
  | FindingConfirmed
  | PainPointDetected
  | OpportunityDetected
  | RecommendationProposed
  | RecommendationRejected
  | RecommendationAccepted
  | DiagnosticClusterMerged;
