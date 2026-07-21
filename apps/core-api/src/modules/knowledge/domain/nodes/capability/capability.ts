import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';

/** A business capability a process delivers. */
export interface CapabilityAttributes extends NodeAttributes<'Capability'> {
  readonly description: string;
}

export type CapabilityNode = KnowledgeNode<CapabilityAttributes>;
