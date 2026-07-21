import type { KnowledgeNodeId, Score } from '@oi/contracts';

/** The kind of decision entity resolution reached for a claim's subject. */
export type ResolutionOutcome = 'MatchExisting' | 'CreateNew' | 'Ambiguous';

/** A candidate existing node a claim's subject might resolve to, with a similarity score. */
export interface ResolutionCandidate {
  readonly nodeId: KnowledgeNodeId;
  readonly similarity: Score;
}

/**
 * The decision produced by `EntityResolutionPolicy` for a single claim — a value
 * object describing *intent*, with no side effects and no persistence.
 *  - `MatchExisting` populates `matchedNodeId`.
 *  - `Ambiguous` populates `candidates` for consultant/heuristic disambiguation.
 *  - `CreateNew` carries neither.
 */
export interface ResolutionDecision {
  readonly outcome: ResolutionOutcome;
  readonly matchedNodeId?: KnowledgeNodeId;
  readonly candidates?: readonly ResolutionCandidate[];
}
