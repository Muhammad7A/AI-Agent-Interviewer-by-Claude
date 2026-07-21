import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';
import type { AutomationLevel, Frequency } from '../../value-objects/enums';

/**
 * A single step within a workflow. `automationLevel` and a described rework rate
 * are prime inputs to bottleneck and opportunity detection downstream.
 */
export interface ActivityAttributes extends NodeAttributes<'Activity'> {
  readonly automationLevel: AutomationLevel;
  readonly effortDescription?: string;
  readonly frequency?: Frequency;
  readonly reworkDescription?: string;
}

export type ActivityNode = KnowledgeNode<ActivityAttributes>;
