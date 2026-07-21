import type { KnowledgeNodeId, TenantId, EngagementId } from '../primitives/ids';
import type { Label, Version } from '../primitives/scalars';
import type { Evidence } from '../provenance/evidence';
import type { Confidence } from '../confidence/confidence';
import type { ValidationRecord } from '../validation/validation-record';
import type { Layer } from './layer';
import type { NodeAttributes } from './node-attributes';

/**
 * The base structural contract every node in the unified graph conforms to,
 * regardless of which context owns its type. Conformance to this one shape is
 * precisely what makes the graph *physically single* and cross-layer queryable
 * (ADR-0004, ADR-0005).
 *
 * The node's kind is carried by `attributes.nodeType` (a self-discriminating
 * payload) — a single source of truth for its type. Each `KnowledgeNode` is its
 * own Aggregate Root (ADR-0006); this interface is its **state contract** —
 * behaviour is defined by the owning context, not here (contracts only).
 *
 * Invariants encoded by this contract (see the invariant registry):
 *  - N1 / G1 evidence-first: `evidence` is non-empty.
 *  - N2 / G3 scope: `tenantId` and `engagementId` are always present.
 *  - N5 type-layer coherence: `layers` are consistent with `attributes.nodeType`.
 *  - N4 / G5 anchor protection governs mutation when `validation.isAnchor`.
 */
export interface KnowledgeNode<TAttributes extends NodeAttributes = NodeAttributes> {
  readonly id: KnowledgeNodeId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly layers: readonly Layer[];
  readonly label: Label;
  readonly attributes: TAttributes;
  readonly evidence: readonly Evidence[];
  readonly confidence: Confidence;
  readonly validation: ValidationRecord;
  readonly version: Version;
}
