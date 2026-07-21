import type { NodeAttributes, KnowledgeNode, RoleLabel } from '@oi/contracts';
import type { HandoffChannel } from '../../value-objects/enums';

/**
 * A handoff between activities — a first-class node because wait time, re-keying
 * and lost context cluster here. Modeling it explicitly lets detectors find
 * bottlenecks structurally, not only when someone complains out loud.
 */
export interface HandoffAttributes extends NodeAttributes<'Handoff'> {
  readonly fromActor: RoleLabel;
  readonly toActor: RoleLabel;
  readonly channel: HandoffChannel;
  readonly latencyDescription?: string;
  readonly waitTimeDescription?: string;
}

export type HandoffNode = KnowledgeNode<HandoffAttributes>;
