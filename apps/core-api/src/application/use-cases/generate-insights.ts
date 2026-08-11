import type { EngagementId } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * Run interpretation over the knowledge graph: propose pain points, opportunities,
 * and recommendations — all entering as `Proposed` (AI proposes, domain validates).
 *
 * Composes (impl): Knowledge `KnowledgeGraphLens` (read), the Bottleneck/
 * Opportunity/RecommendationSynthesis AI ACL ports, Insights policies
 * (deduplication, ranking, prioritization), Insights repositories, `UnitOfWork`.
 */
export interface GenerateInsightsCommand extends Command {
  readonly engagementId: EngagementId;
}

export interface GenerateInsightsResult {
  readonly painPointCount: number;
  readonly opportunityCount: number;
  readonly recommendationCount: number;
}

export interface GenerateInsightsHandler
  extends CommandHandler<GenerateInsightsCommand, GenerateInsightsResult> {}
