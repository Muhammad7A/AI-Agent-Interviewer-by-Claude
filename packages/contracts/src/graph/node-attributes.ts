import type { NodeType } from './node-type';

/**
 * Base for type-specific node attribute payloads, carrying the type discriminant.
 *
 * Each owning context defines concrete payloads that extend this with a *literal*
 * `nodeType` (e.g. `interface WorkflowAttributes extends NodeAttributes<'Workflow'>`),
 * which makes a context's attribute set a self-discriminating union — a single
 * source of truth for a node's kind. The Shared Kernel fixes only the discriminant
 * seam; the payload fields belong to the owning context.
 */
export interface NodeAttributes<TType extends NodeType = NodeType> {
  readonly nodeType: TType;
}
