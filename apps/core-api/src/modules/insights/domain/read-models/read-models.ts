import type { KnowledgeNodeId, DepartmentLabel } from '@oi/contracts';
import type { ResolvedEvidence } from '@oi/transcript';
import type { Severity, Frequency, BusinessImpact } from '../value-objects/scales';
import type { PainCategory } from '../value-objects/classification';
import type { OpportunityScore } from '../value-objects/opportunity-score';
import type { RecommendationPriority, PriorityTier } from '../value-objects/recommendation-priority';

/**
 * Read models — denormalized, query-optimized projections for the consultant
 * dashboard and reporting. Shapes only; no query logic. They answer the
 * senior-consultant questions this context exists to serve.
 */

/** "What are the biggest operational bottlenecks?" — pain points ranked by severity × frequency × impact. */
export interface BottleneckRankingEntry {
  readonly painPointId: KnowledgeNodeId;
  readonly rank: number;
  readonly severity: Severity;
  readonly frequency: Frequency;
  readonly businessImpact: BusinessImpact;
  readonly affectedDepartments: readonly DepartmentLabel[];
}
export interface BottleneckRanking {
  readonly entries: readonly BottleneckRankingEntry[];
}

/** "Which departments are most affected?" — pain distribution per department. */
export interface DepartmentImpactProfile {
  readonly department: DepartmentLabel;
  readonly painPointCount: number;
  readonly dominantCategory: PainCategory;
  readonly topPainPointIds: readonly KnowledgeNodeId[];
}

/** "Which AI opportunities have the highest business impact?" — ranked leaderboard. */
export interface OpportunityLeaderboardEntry {
  readonly opportunityId: KnowledgeNodeId;
  readonly rank: number;
  readonly score: OpportunityScore;
}
export interface OpportunityLeaderboard {
  readonly entries: readonly OpportunityLeaderboardEntry[];
}

/** "Which recommendations should be prioritized?" — the roadmap. */
export interface RecommendationRoadmapItem {
  readonly recommendationId: KnowledgeNodeId;
  readonly tier: PriorityTier;
  readonly priority: RecommendationPriority;
}
export interface RecommendationRoadmap {
  readonly items: readonly RecommendationRoadmapItem[];
}

/**
 * The audit view behind any insight: its resolved transcript quotes, obtained via
 * Transcript's Published Language (`ResolvedEvidence`). This makes INS4
 * (traceability to immutable EvidenceRefs) visible to a consultant — drilling
 * from a boardroom insight to the sentence an employee said.
 */
export interface EvidenceTrace {
  readonly insightId: KnowledgeNodeId;
  readonly quotes: readonly ResolvedEvidence[];
}
