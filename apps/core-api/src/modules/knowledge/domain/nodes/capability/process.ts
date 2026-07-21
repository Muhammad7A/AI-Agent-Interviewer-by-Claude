import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';
import type { Cadence, Criticality } from '../../value-objects/enums';

/**
 * A business process — the bridge between *who* (departments) and *how*
 * (workflows). It answers what a department actually does, before descending to
 * step-level detail.
 */
export interface ProcessAttributes extends NodeAttributes<'Process'> {
  readonly purpose: string;
  readonly trigger?: string;
  readonly cadence?: Cadence;
  readonly criticality?: Criticality;
}

export type ProcessNode = KnowledgeNode<ProcessAttributes>;
