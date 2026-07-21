import type { NodeAttributes, KnowledgeNode, RoleLabel } from '@oi/contracts';
import type { Seniority } from '../../value-objects/enums';

/** A role/position as described (distinct from the individuals who hold it). */
export interface RoleAttributes extends NodeAttributes<'Role'> {
  readonly title: RoleLabel;
  readonly seniority?: Seniority;
  readonly headcountDescription?: string;
}

export type RoleNode = KnowledgeNode<RoleAttributes>;
