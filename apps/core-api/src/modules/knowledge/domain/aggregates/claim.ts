import type {
  TenantId,
  EngagementId,
  KnowledgeNodeId,
  KnowledgeEdgeId,
  Evidence,
  Score,
  Layer,
} from '@oi/contracts';
import type { ClaimId } from '../value-objects/ids';
import type { ClaimTriple } from '../value-objects/claim-triple';
import type { ClaimStatus } from '../value-objects/claim-status';

/**
 * **Aggregate Root.** The atomic unit that bridges unstructured transcript text
 * and the structured graph: a single subject–predicate–object assertion drawn
 * from one segment, carrying its own evidence and extraction confidence.
 *
 * Keeping extraction (fuzzy, text-level) separate from graph construction
 * (resolved, structured) is what lets extraction re-run with a better model
 * without destabilizing the validated graph above it.
 *
 * This interface is the aggregate's **state contract** — behaviour lives in the
 * application layer (out of scope here).
 *
 * Invariants (see the Knowledge invariant registry):
 *  - C1: `evidence.kind === 'Stated'` — claims come directly from a segment.
 *  - C2: a `Resolved` claim has non-empty `resolvedInto`; `Unresolved`/`Rejected`
 *    have none.
 *  - K3: every id in `resolvedInto` belongs to the same engagement.
 */
export interface Claim {
  readonly id: ClaimId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly triple: ClaimTriple;
  readonly targetLayer: Layer;
  readonly evidence: Evidence;
  readonly extractionConfidence: Score;
  readonly status: ClaimStatus;
  readonly resolvedInto: readonly (KnowledgeNodeId | KnowledgeEdgeId)[];
}
