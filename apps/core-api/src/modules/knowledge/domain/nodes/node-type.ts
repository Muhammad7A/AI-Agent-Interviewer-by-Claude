/**
 * The Knowledge context's node-type catalog — the concrete literal values that
 * narrow the Shared Kernel's open `NodeType` seam for the layers this context
 * owns (ADR-0005). Insights owns the diagnostic/opportunity/synthesis names.
 */

/** Structural layer — the org as actually described. */
export type StructuralNodeType = 'Department' | 'Team' | 'Role' | 'Person';

/** Capability layer — what the organization does. */
export type CapabilityNodeType = 'Process' | 'Capability';

/** Operational layer — how work actually happens. */
export type OperationalNodeType = 'Workflow' | 'Activity' | 'Handoff' | 'System' | 'Artifact';

/** All node types owned by the Knowledge context. */
export type KnowledgeNodeType = StructuralNodeType | CapabilityNodeType | OperationalNodeType;
