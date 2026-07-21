import type { Opportunity } from '../nodes/opportunity/opportunity';
import type { OpportunityScore } from '../value-objects/opportunity-score';
import type { RankedOpportunity } from '../value-objects/policy-results';

/**
 * **Domain service (port).** Scores and ranks opportunities by business value
 * against implementation complexity and risk. `score` explains a single
 * opportunity; `rank` orders a set. Interface only.
 */
export interface OpportunityRankingPolicy {
  score(opportunity: Opportunity): OpportunityScore;
  rank(opportunities: readonly Opportunity[]): readonly RankedOpportunity[];
}
