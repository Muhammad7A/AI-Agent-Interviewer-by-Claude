import type { EdgeAttributes, KnowledgeEdge } from '@oi/contracts';

/**
 * Operational-layer edge contracts. Most carry only the discriminant; two carry
 * payload that is directly useful to downstream detection.
 */

export type RealizedByEdgeAttributes = EdgeAttributes<'realized-by'>;

/** Workflow→Activity membership, with the step's position in the flow. */
export interface HasStepEdgeAttributes extends EdgeAttributes<'has-step'> {
  readonly order?: number;
}

/** Activity→Activity ordering. `isRework` marks a loop-back rather than forward flow — a bottleneck signal. */
export interface PrecedesEdgeAttributes extends EdgeAttributes<'precedes'> {
  readonly isRework?: boolean;
}

export type PerformedByEdgeAttributes = EdgeAttributes<'performed-by'>;
export type UsesEdgeAttributes = EdgeAttributes<'uses'>;
export type ProducesEdgeAttributes = EdgeAttributes<'produces'>;
export type ConsumesEdgeAttributes = EdgeAttributes<'consumes'>;
export type HandsOffViaEdgeAttributes = EdgeAttributes<'hands-off-via'>;

/** Process→Workflow realization. */
export type RealizedByEdge = KnowledgeEdge<RealizedByEdgeAttributes>;
/** Workflow→Activity step membership. */
export type HasStepEdge = KnowledgeEdge<HasStepEdgeAttributes>;
/** Activity→Activity ordering (possibly rework). */
export type PrecedesEdge = KnowledgeEdge<PrecedesEdgeAttributes>;
/** Activity→Role assignment. */
export type PerformedByEdge = KnowledgeEdge<PerformedByEdgeAttributes>;
/** Activity→System usage. */
export type UsesEdge = KnowledgeEdge<UsesEdgeAttributes>;
/** Activity→Artifact output. */
export type ProducesEdge = KnowledgeEdge<ProducesEdgeAttributes>;
/** Activity→Artifact input. */
export type ConsumesEdge = KnowledgeEdge<ConsumesEdgeAttributes>;
/** Activity→Handoff→Activity transfer. */
export type HandsOffViaEdge = KnowledgeEdge<HandsOffViaEdgeAttributes>;
