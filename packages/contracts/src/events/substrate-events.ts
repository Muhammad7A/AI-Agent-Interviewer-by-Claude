import type { KnowledgeNodeId, KnowledgeEdgeId, EvidenceId } from '../primitives/ids';
import type { Layer } from '../graph/layer';
import type { NodeType } from '../graph/node-type';
import type { EdgeType } from '../graph/edge-type';
import type { Confidence } from '../confidence/confidence';
import type { ValidationState } from '../validation/validation-state';
import type { DomainEvent } from './domain-event';

/**
 * Substrate-level domain events — the shared vocabulary announcing changes to
 * the base node/edge/evidence/confidence/validation model. Context-specific
 * business events (e.g. `PainPointProposed`) are defined by their owning
 * contexts, not the Shared Kernel.
 */

/** Which kind of graph element an event targets. */
export type GraphElementKind = 'Node' | 'Edge';

export type KnowledgeNodeAdded = DomainEvent<
  'knowledge.node.added',
  {
    readonly nodeId: KnowledgeNodeId;
    readonly nodeType: NodeType;
    readonly layers: readonly Layer[];
  }
>;

export type KnowledgeNodeMerged = DomainEvent<
  'knowledge.node.merged',
  {
    readonly supersededId: KnowledgeNodeId;
    readonly survivingId: KnowledgeNodeId;
  }
>;

export type KnowledgeNodeRevised = DomainEvent<
  'knowledge.node.revised',
  {
    readonly nodeId: KnowledgeNodeId;
  }
>;

export type KnowledgeEdgeAdded = DomainEvent<
  'knowledge.edge.added',
  {
    readonly edgeId: KnowledgeEdgeId;
    readonly edgeType: EdgeType;
    readonly sourceId: KnowledgeNodeId;
    readonly targetId: KnowledgeNodeId;
    readonly layers: readonly Layer[];
  }
>;

export type EvidenceAttached = DomainEvent<
  'knowledge.evidence.attached',
  {
    readonly targetKind: GraphElementKind;
    readonly targetId: KnowledgeNodeId | KnowledgeEdgeId;
    readonly evidenceId: EvidenceId;
  }
>;

export type ConfidenceRecomputed = DomainEvent<
  'knowledge.confidence.recomputed',
  {
    readonly targetKind: GraphElementKind;
    readonly targetId: KnowledgeNodeId | KnowledgeEdgeId;
    readonly confidence: Confidence;
  }
>;

export type ContradictionDetected = DomainEvent<
  'knowledge.contradiction.detected',
  {
    readonly targetKind: GraphElementKind;
    readonly targetId: KnowledgeNodeId | KnowledgeEdgeId;
    readonly conflictingEvidence: readonly EvidenceId[];
  }
>;

export type ValidationTransitioned = DomainEvent<
  'knowledge.validation.transitioned',
  {
    readonly targetKind: GraphElementKind;
    readonly targetId: KnowledgeNodeId | KnowledgeEdgeId;
    readonly from: ValidationState;
    readonly to: ValidationState;
  }
>;

/** Discriminated union of all substrate events, keyed by `eventType`. */
export type SubstrateEvent =
  | KnowledgeNodeAdded
  | KnowledgeNodeMerged
  | KnowledgeNodeRevised
  | KnowledgeEdgeAdded
  | EvidenceAttached
  | ConfidenceRecomputed
  | ContradictionDetected
  | ValidationTransitioned;
