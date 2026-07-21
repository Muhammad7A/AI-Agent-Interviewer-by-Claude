import type { DomainEvent, KnowledgeNodeId, KnowledgeEdgeId, Layer } from '@oi/contracts';
import type { ClaimId, ContradictionId } from '../value-objects/ids';

/**
 * Knowledge-context domain events. These are the events *unique* to this context
 * (the `Claim` and `Contradiction` lifecycles). The node/edge/evidence/
 * confidence/validation events are Shared Kernel substrate events (`SubstrateEvent`)
 * — emitted by this context but defined once in the kernel, not redefined here
 * (no duplication).
 */

export type ClaimExtracted = DomainEvent<
  'knowledge.claim.extracted',
  {
    readonly claimId: ClaimId;
    readonly targetLayer: Layer;
  }
>;

export type ClaimResolved = DomainEvent<
  'knowledge.claim.resolved',
  {
    readonly claimId: ClaimId;
    readonly resolvedInto: readonly (KnowledgeNodeId | KnowledgeEdgeId)[];
  }
>;

export type ClaimRejected = DomainEvent<
  'knowledge.claim.rejected',
  {
    readonly claimId: ClaimId;
    readonly reason: string;
  }
>;

export type ContradictionResolved = DomainEvent<
  'knowledge.contradiction.resolved',
  {
    readonly contradictionId: ContradictionId;
  }
>;

/** Discriminated union of the Knowledge context's own domain events. */
export type KnowledgeDomainEvent =
  | ClaimExtracted
  | ClaimResolved
  | ClaimRejected
  | ContradictionResolved;
