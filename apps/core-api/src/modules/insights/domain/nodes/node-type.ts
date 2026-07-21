/**
 * The Insights context's node-type catalog — literal values narrowing the Shared
 * Kernel's open `NodeType` seam for the layers this context owns (ADR-0005).
 * Knowledge owns the structural/capability/operational names.
 */

/** Diagnostic layer — where it hurts. */
export type DiagnosticNodeType = 'PainPoint' | 'DiagnosticCluster';

/** Opportunity layer — where AI/automation can help. */
export type OpportunityNodeType = 'Opportunity';

/** Synthesis layer — prioritized interventions. */
export type SynthesisNodeType = 'Recommendation' | 'RecommendationBundle';

/** All node types owned by the Insights context. */
export type InsightsNodeType = DiagnosticNodeType | OpportunityNodeType | SynthesisNodeType;
