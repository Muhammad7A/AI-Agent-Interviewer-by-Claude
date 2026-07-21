import type { GraphElementKind, KnowledgeNodeId, KnowledgeEdgeId } from '@oi/contracts';
import type { KnowledgeNodeType } from '@oi/knowledge';

/**
 * A reference from an Insights artifact to a **Knowledge** graph artifact it
 * interprets. Insights never owns these nodes/edges — Knowledge does — it only
 * points at them by identity (Shared Kernel ids + `GraphElementKind`), optionally
 * recording the Knowledge node type (from Knowledge's Published Language) for
 * diagnostic readability ("this pain affects a Handoff"). This is how Insights
 * "references a Knowledge artifact" for invariants INS1/INS6 without depending on
 * Knowledge internals.
 */
export interface KnowledgeArtifactRef {
  readonly kind: GraphElementKind;
  readonly id: KnowledgeNodeId | KnowledgeEdgeId;
  /** Present when `kind === 'Node'`; the Knowledge node's published type. */
  readonly nodeType?: KnowledgeNodeType;
}
