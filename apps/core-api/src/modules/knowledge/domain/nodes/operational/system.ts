import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';
import type { IntegrationQuality } from '../../value-objects/enums';

/** A tool/application used in an activity. `swivelChair` flags manual re-entry between disconnected systems — a classic automation target. */
export interface SystemAttributes extends NodeAttributes<'System'> {
  readonly vendor?: string;
  readonly integrationQuality: IntegrationQuality;
  readonly swivelChair: boolean;
}

export type SystemNode = KnowledgeNode<SystemAttributes>;
