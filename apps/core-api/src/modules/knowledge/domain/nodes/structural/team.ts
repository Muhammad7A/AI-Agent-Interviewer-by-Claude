import type { NodeAttributes, KnowledgeNode, DepartmentLabel } from '@oi/contracts';

/** A team within a department, as described. */
export interface TeamAttributes extends NodeAttributes<'Team'> {
  readonly purpose?: string;
  readonly parentDepartment?: DepartmentLabel;
}

export type TeamNode = KnowledgeNode<TeamAttributes>;
