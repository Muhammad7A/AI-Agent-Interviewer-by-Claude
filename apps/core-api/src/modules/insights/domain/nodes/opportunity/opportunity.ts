import type { NodeAttributes, KnowledgeNode, KnowledgeNodeId } from '@oi/contracts';
import type { KnowledgeArtifactRef } from '../../value-objects/knowledge-artifact-ref';
import type { AiPattern } from '../../value-objects/taxonomies';
import type { BusinessValue, ImplementationComplexity, RiskLevel } from '../../value-objects/scales';
import type { Prerequisite } from '../../value-objects/prerequisite';
import type { OpportunityScore } from '../../value-objects/opportunity-score';

/**
 * An AI/automation opportunity. A `KnowledgeNode` in the Opportunity layer. It is
 * only credible when it names both the pain it resolves and the work it applies
 * to.
 *
 * Invariants: `addressedPainPointIds` has ≥1 entry (INS2 — every opportunity
 * resolves one or more pain points); `appliesTo` has ≥1 Knowledge artifact (the
 * workflow/activity it targets).
 */
export interface OpportunityAttributes extends NodeAttributes<'Opportunity'> {
  readonly aiPattern: AiPattern;
  readonly addressedPainPointIds: readonly KnowledgeNodeId[];
  readonly appliesTo: readonly KnowledgeArtifactRef[];
  readonly businessValue: BusinessValue;
  readonly implementationComplexity: ImplementationComplexity;
  readonly riskLevel: RiskLevel;
  readonly prerequisites: readonly Prerequisite[];
  readonly score: OpportunityScore;
}

export type Opportunity = KnowledgeNode<OpportunityAttributes>;
