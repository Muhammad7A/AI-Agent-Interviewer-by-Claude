import type { TenantId, EngagementId, Evidence, ValidationRecord } from '@oi/contracts';
import type { ObservationId } from '../value-objects/ids';
import type { SignalType } from '../value-objects/taxonomies';
import type { DiagnosticConfidence } from '../value-objects/confidence';
import type { KnowledgeArtifactRef } from '../value-objects/knowledge-artifact-ref';

/**
 * **Aggregate Root.** The atomic unit of interpretation — a single signal noticed
 * over the Knowledge graph (the Insights analogue of Knowledge's `Claim`). It is
 * *proposed* (typically by ai-engine) and enters as `validation.state = 'Proposed'`;
 * it is never authoritative until validated. It is **not** a graph node.
 *
 * State contract only; behaviour lives in the application layer.
 *
 * Invariants: references ≥1 Knowledge artifact (`about`) and carries ≥1
 * `Evidence` resolving to immutable EvidenceRefs (INS4, INS6). Insights owns the
 * interpretation; Knowledge owns the referenced truth; Transcript owns the
 * evidence.
 */
export interface Observation {
  readonly id: ObservationId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly signalType: SignalType;
  readonly statement: string;
  readonly about: readonly KnowledgeArtifactRef[];
  readonly evidence: readonly Evidence[];
  readonly confidence: DiagnosticConfidence;
  readonly validation: ValidationRecord;
}
