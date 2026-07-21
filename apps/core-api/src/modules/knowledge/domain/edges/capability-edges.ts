import type { EdgeAttributes, KnowledgeEdge } from '@oi/contracts';

/** Capability-layer edge contracts. */

export type OwnsEdgeAttributes = EdgeAttributes<'owns'>;
export type DeliversEdgeAttributes = EdgeAttributes<'delivers'>;
export type ComposedOfEdgeAttributes = EdgeAttributes<'composed-of'>;
export type DependsOnEdgeAttributes = EdgeAttributes<'depends-on'>;

/** Department→Process ownership. */
export type OwnsEdge = KnowledgeEdge<OwnsEdgeAttributes>;
/** Process→Capability delivery. */
export type DeliversEdge = KnowledgeEdge<DeliversEdgeAttributes>;
/** Process→sub-Process composition. */
export type ComposedOfEdge = KnowledgeEdge<ComposedOfEdgeAttributes>;
/** Process→Process dependency. */
export type DependsOnEdge = KnowledgeEdge<DependsOnEdgeAttributes>;
