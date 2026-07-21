/**
 * Discriminator for a node's kind (e.g. "Department", "Workflow", "PainPoint").
 *
 * An **open string** whose concrete values are owned by the context that owns the
 * layer — Knowledge owns the structural/capability/operational names, Insights
 * owns the diagnostic/opportunity/synthesis names. The Shared Kernel fixes the
 * seam (the discriminant's role), not the value set, so the graph stays
 * physically unified while node types remain context-sovereign (ADR-0005). Each
 * context narrows this to a literal union (e.g. `'Department' | 'Team' | ...`).
 */
export type NodeType = string;
