import type {
  TenantId,
  EngagementId,
  KnowledgeNodeId,
  KnowledgeEdgeId,
  EvidenceId,
  GraphElementKind,
} from '@oi/contracts';
import type { ContradictionId } from '../value-objects/ids';
import type { ContradictionStatus } from '../value-objects/contradiction-status';

/**
 * **Entity** (non-root). A recorded conflict among the evidence attached to a
 * node or edge. Contradictions are *recorded, never silently resolved*
 * (invariant K2) — a consultant adjudicates through validation. It has identity
 * and a lifecycle within an engagement's graph, which is what makes it an entity
 * rather than a value object.
 *
 * `GraphElementKind` and the id types are reused from the Shared Kernel; nothing
 * is duplicated.
 */
export interface Contradiction {
  readonly id: ContradictionId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly targetKind: GraphElementKind;
  readonly targetId: KnowledgeNodeId | KnowledgeEdgeId;
  readonly conflictingEvidence: readonly EvidenceId[];
  readonly status: ContradictionStatus;
}
