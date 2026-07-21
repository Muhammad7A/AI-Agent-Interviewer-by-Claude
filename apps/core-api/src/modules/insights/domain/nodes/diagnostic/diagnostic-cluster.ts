import type { NodeAttributes, KnowledgeNode, KnowledgeNodeId } from '@oi/contracts';
import type { RootCauseId } from '../../value-objects/ids';
import type { PainCategory } from '../../value-objects/classification';
import type { RootCauseConfidence } from '../../value-objects/confidence';

/**
 * A grouping of related pain points that share a theme or root cause — the unit
 * consultants reason about ("these six frictions are one problem"). A
 * `KnowledgeNode` in the Diagnostic layer.
 *
 * Invariant: `memberPainPointIds` has ≥1 entry (no orphan cluster, INS6).
 */
export interface DiagnosticClusterAttributes extends NodeAttributes<'DiagnosticCluster'> {
  readonly theme: string;
  readonly memberPainPointIds: readonly KnowledgeNodeId[];
  readonly dominantCategory?: PainCategory;
  readonly rootCauseId?: RootCauseId;
  readonly rootCauseConfidence?: RootCauseConfidence;
}

export type DiagnosticCluster = KnowledgeNode<DiagnosticClusterAttributes>;
