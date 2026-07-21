import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';
import type { FindingId } from '../../value-objects/ids';
import type { KnowledgeArtifactRef } from '../../value-objects/knowledge-artifact-ref';
import type { PainCategory, PainNature, DiagnosticOrigin } from '../../value-objects/classification';
import type { Severity, Frequency, BusinessImpact } from '../../value-objects/scales';

/**
 * A diagnosed operational problem, classified People/Process/Technology. A
 * `KnowledgeNode` in the Diagnostic layer, so it inherits evidence + confidence +
 * validation from the Shared Kernel base and lives in the one graph.
 *
 * Invariants: `affectedKnowledgeArtifacts` has ≥1 entry (INS1 — every pain point
 * references a Knowledge artifact); `supportingFindingIds` has ≥1 entry (INS5/INS6
 * — grounded in findings, no orphans).
 */
export interface PainPointAttributes extends NodeAttributes<'PainPoint'> {
  readonly category: PainCategory;
  readonly nature: PainNature;
  readonly origin: DiagnosticOrigin;
  readonly severity: Severity;
  readonly frequency: Frequency;
  readonly businessImpact: BusinessImpact;
  readonly supportingFindingIds: readonly FindingId[];
  readonly affectedKnowledgeArtifacts: readonly KnowledgeArtifactRef[];
}

export type PainPoint = KnowledgeNode<PainPointAttributes>;
