import type { TenantId, EngagementId, KnowledgeNodeId, ValidationRecord } from '@oi/contracts';
import type { RootCauseId, FindingId } from '../value-objects/ids';
import type { RootCauseConfidence } from '../value-objects/confidence';

/**
 * **Entity.** A candidate underlying cause explaining a set of pain points,
 * produced by `RootCauseAnalysisPolicy`. It has identity and a validation
 * lifecycle (proposed → validated), which makes it an entity; a
 * `DiagnosticCluster` references it by `RootCauseId`.
 *
 * Invariant: explains ≥1 pain point and rests on ≥1 finding (no orphan, INS6).
 */
export interface RootCauseHypothesis {
  readonly id: RootCauseId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly statement: string;
  readonly explainedPainPointIds: readonly KnowledgeNodeId[];
  readonly supportingFindingIds: readonly FindingId[];
  readonly confidence: RootCauseConfidence;
  readonly validation: ValidationRecord;
}
