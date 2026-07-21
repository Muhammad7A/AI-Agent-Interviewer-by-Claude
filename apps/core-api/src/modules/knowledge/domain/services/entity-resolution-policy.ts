import type { KnowledgeNode } from '@oi/contracts';
import type { Claim } from '../aggregates/claim';
import type { ResolutionDecision } from '../value-objects/resolution';

/**
 * **Domain service (port).** Decides whether a claim's subject resolves to an
 * existing node, warrants a new node, or is ambiguous. A pure decision: no side
 * effects, no persistence. The implementation strategy is not defined here.
 */
export interface EntityResolutionPolicy {
  decide(claim: Claim, candidates: readonly KnowledgeNode[]): ResolutionDecision;
}
