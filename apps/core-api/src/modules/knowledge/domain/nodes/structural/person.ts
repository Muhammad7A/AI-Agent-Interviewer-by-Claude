import type { NodeAttributes, KnowledgeNode, IntervieweeRef, RoleLabel } from '@oi/contracts';

/**
 * A person node — a pseudonymized reference linking a perspective to its
 * evidence. It carries an `IntervieweeRef`, never PII; the platform models
 * viewpoints, not a surveillance record of individuals.
 */
export interface PersonAttributes extends NodeAttributes<'Person'> {
  readonly intervieweeRef: IntervieweeRef;
  readonly primaryRole?: RoleLabel;
}

export type PersonNode = KnowledgeNode<PersonAttributes>;
