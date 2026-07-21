import type { EdgeAttributes, KnowledgeEdge } from '@oi/contracts';

/**
 * Structural-layer edge contracts. These predicates carry no payload beyond the
 * discriminant, so their attributes are plain `EdgeAttributes` specializations.
 */

export type ReportsToEdgeAttributes = EdgeAttributes<'reports-to'>;
export type PartOfEdgeAttributes = EdgeAttributes<'part-of'>;
export type CollaboratesWithEdgeAttributes = EdgeAttributes<'collaborates-with'>;

/** Role→Role or Team→Department reporting line. */
export type ReportsToEdge = KnowledgeEdge<ReportsToEdgeAttributes>;
/** Team→Department containment. */
export type PartOfEdge = KnowledgeEdge<PartOfEdgeAttributes>;
/** Department↔Department informal collaboration (captures the real, unofficial structure). */
export type CollaboratesWithEdge = KnowledgeEdge<CollaboratesWithEdgeAttributes>;
