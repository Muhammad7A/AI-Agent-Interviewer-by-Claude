import type { NodeType } from './node-type';

/**
 * Base marker for type-specific node attributes. Each owning context defines a
 * concrete shape extending this (e.g. a `WorkflowAttributes` in the Knowledge
 * context) and discriminates on `nodeType`. The Shared Kernel fixes only the
 * discriminant, keeping the substrate agnostic to any one layer's payload.
 */
export interface NodeAttributes {
  readonly nodeType: NodeType;
}
