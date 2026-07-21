import type { InvariantCode } from './invariant-code';

/**
 * A declarative statement of a Shared Kernel invariant. This is **data, not
 * logic**: the canonical registry that the owning contexts' factories, guards
 * and tests reference by `code`. This package defines the invariants; it does
 * not enforce them (enforcement is behaviour and lives in the domain contexts).
 */
export interface InvariantSpec<TCode extends string = InvariantCode> {
  readonly code: TCode;
  readonly name: string;
  readonly statement: string;
  /** The contracts this invariant constrains. */
  readonly appliesTo: readonly string[];
}

/**
 * The Shared Kernel invariant registry — the substrate's non-negotiable rules,
 * keyed by code. Preserves the two load-bearing principles: evidence-first (N1,
 * E1) and one-graph coherence (N5), plus scope (N2), integrity (N3) and human
 * anchor protection (N4).
 */
export const SHARED_KERNEL_INVARIANTS = {
  N1: {
    code: 'N1',
    name: 'Evidence-first',
    statement: 'Every KnowledgeNode and KnowledgeEdge carries at least one Evidence.',
    appliesTo: ['KnowledgeNode', 'KnowledgeEdge'],
  },
  N2: {
    code: 'N2',
    name: 'Tenant and engagement scope',
    statement: 'Every node and edge carries a resolving TenantId and EngagementId; no artifact is unscoped.',
    appliesTo: ['KnowledgeNode', 'KnowledgeEdge'],
  },
  N3: {
    code: 'N3',
    name: 'Endpoint integrity',
    statement: "An edge's sourceId and targetId reference nodes that exist within the same engagement.",
    appliesTo: ['KnowledgeEdge'],
  },
  N4: {
    code: 'N4',
    name: 'Anchor protection',
    statement:
      'When validation.isAnchor is true, machine recompute may not revise or overwrite the artifact; only a ValidationEvent may change it.',
    appliesTo: ['KnowledgeNode', 'KnowledgeEdge', 'ValidationRecord'],
  },
  N5: {
    code: 'N5',
    name: 'Type-layer coherence',
    statement:
      "A node's layers are consistent with its nodeType, and an edge's layers are consistent with its edgeType.",
    appliesTo: ['KnowledgeNode', 'KnowledgeEdge'],
  },
  E1: {
    code: 'E1',
    name: 'Transitive resolvability',
    statement:
      'Inferred evidence is anchored by a Derivation whose inputEvidence is non-empty and resolvable within the engagement, so every inference resolves transitively to Stated transcript segments.',
    appliesTo: ['Evidence', 'Derivation'],
  },
} as const satisfies Record<InvariantCode, InvariantSpec>;
