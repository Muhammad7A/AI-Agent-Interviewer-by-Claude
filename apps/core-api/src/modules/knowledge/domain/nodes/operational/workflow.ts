import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';
import type { Frequency } from '../../value-objects/enums';

/** A concrete workflow that realizes a process — the level at which bottlenecks and automation opportunities physically live. */
export interface WorkflowAttributes extends NodeAttributes<'Workflow'> {
  readonly trigger?: string;
  readonly frequency?: Frequency;
  readonly endState?: string;
}

export type WorkflowNode = KnowledgeNode<WorkflowAttributes>;
