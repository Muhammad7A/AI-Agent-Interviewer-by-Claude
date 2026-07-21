/**
 * Interpretation taxonomies.
 */

/** The pattern an `Observation` recognized over the knowledge graph. */
export type SignalType =
  | 'ManualStep'
  | 'HighLatencyHandoff'
  | 'ReworkLoop'
  | 'SwivelChair'
  | 'Fragmentation'
  | 'Duplication'
  | 'KnowledgeSilo'
  | 'Bottleneck'
  | 'Other';

/** The AI/automation pattern an `Opportunity` applies. */
export type AiPattern =
  | 'DocumentExtraction'
  | 'Classification'
  | 'Drafting'
  | 'RoutingTriage'
  | 'Forecasting'
  | 'RetrievalQa'
  | 'RulesRpa'
  | 'AnomalyDetection'
  | 'Other';
