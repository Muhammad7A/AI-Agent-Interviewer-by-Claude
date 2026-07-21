/**
 * The Knowledge context's edge-predicate catalog — literal values narrowing the
 * Shared Kernel's open `EdgeType` seam for the layers this context owns.
 */

/** Structural-layer predicates. */
export type StructuralEdgeType = 'reports-to' | 'part-of' | 'collaborates-with';

/** Capability-layer predicates. */
export type CapabilityEdgeType = 'owns' | 'delivers' | 'composed-of' | 'depends-on';

/** Operational-layer predicates. */
export type OperationalEdgeType =
  | 'realized-by'
  | 'has-step'
  | 'precedes'
  | 'performed-by'
  | 'uses'
  | 'produces'
  | 'consumes'
  | 'hands-off-via';

/** All edge predicates owned by the Knowledge context. */
export type KnowledgeEdgeType = StructuralEdgeType | CapabilityEdgeType | OperationalEdgeType;
