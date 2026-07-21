import type { KnowledgeNode } from '@oi/contracts';
import type { PainPointAttributes, DiagnosticClusterAttributes, PainPoint, DiagnosticCluster } from './diagnostic';
import type { OpportunityAttributes, Opportunity } from './opportunity';
import type {
  RecommendationAttributes,
  RecommendationBundleAttributes,
  Recommendation,
  RecommendationBundle,
} from './synthesis';

export * from './node-type';
export * from './diagnostic';
export * from './opportunity';
export * from './synthesis';

/** Attribute unions per layer (discriminated by `nodeType`). */
export type DiagnosticNodeAttributes = PainPointAttributes | DiagnosticClusterAttributes;
export type OpportunityNodeAttributes = OpportunityAttributes;
export type SynthesisNodeAttributes = RecommendationAttributes | RecommendationBundleAttributes;

/** Every node-attribute payload the Insights context owns. */
export type InsightsNodeAttributes =
  | DiagnosticNodeAttributes
  | OpportunityNodeAttributes
  | SynthesisNodeAttributes;

/** The discriminated union of every typed Insights node. */
export type InsightsNodeUnion =
  | PainPoint
  | DiagnosticCluster
  | Opportunity
  | Recommendation
  | RecommendationBundle;

/** An Insights node whose attributes are any of this context's payloads. */
export type AnyInsightsNode = KnowledgeNode<InsightsNodeAttributes>;
