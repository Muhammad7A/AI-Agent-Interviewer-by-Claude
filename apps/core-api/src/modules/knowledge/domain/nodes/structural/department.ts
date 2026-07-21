import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';

/**
 * A department as *described* by the people in it — which routinely diverges from
 * the official org chart held by the Organization context. That divergence is
 * itself a signal for the Insights context.
 */
export interface DepartmentAttributes extends NodeAttributes<'Department'> {
  readonly businessFunction: string;
  readonly statedMandate?: string;
  readonly sizeDescription?: string;
}

/** A structural-layer node specialization of the Shared Kernel base. */
export type DepartmentNode = KnowledgeNode<DepartmentAttributes>;
