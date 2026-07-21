import type { Brand } from '../primitives/brand';

/**
 * Discriminator for a node's kind (e.g. "Department", "Workflow", "PainPoint").
 *
 * The *values* are owned by the context that owns the layer (an open brand, not
 * a closed union): Knowledge owns the structural/capability/operational types,
 * Insights owns the diagnostic/opportunity/synthesis types. The Shared Kernel
 * fixes only the shape — so the graph stays physically unified while node types
 * remain context-sovereign (ADR-0005).
 */
export type NodeType = Brand<string, 'NodeType'>;
