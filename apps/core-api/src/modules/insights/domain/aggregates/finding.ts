import type { TenantId, EngagementId, Evidence, ValidationRecord } from '@oi/contracts';
import type { FindingId, ObservationId } from '../value-objects/ids';
import type { DiagnosticConfidence } from '../value-objects/confidence';
import type { KnowledgeArtifactRef } from '../value-objects/knowledge-artifact-ref';

/**
 * **Aggregate Root.** A confirmed interpretation aggregating one or more
 * `Observation`s — the validated diagnostic building block. Pain points and,
 * transitively, recommendations rest on findings (INS5): "recommendations cannot
 * exist without supporting findings."
 *
 * A Finding becomes authoritative only through validation (AI proposes, domain
 * validates). Not a graph node. State contract only.
 *
 * Invariants: references ≥1 `Observation` and ≥1 Knowledge artifact; carries ≥1
 * `Evidence` (INS4, INS6).
 */
export interface Finding {
  readonly id: FindingId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly statement: string;
  readonly supportingObservationIds: readonly ObservationId[];
  readonly about: readonly KnowledgeArtifactRef[];
  readonly evidence: readonly Evidence[];
  readonly confidence: DiagnosticConfidence;
  readonly validation: ValidationRecord;
}
