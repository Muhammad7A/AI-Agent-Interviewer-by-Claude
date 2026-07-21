/** The kind of precondition an opportunity needs before it is feasible. */
export type PrerequisiteKind = 'Data' | 'Integration' | 'Volume' | 'Skill' | 'Governance';

/** A precondition an `Opportunity` requires (data availability, integration, volume, …). */
export interface Prerequisite {
  readonly kind: PrerequisiteKind;
  readonly description: string;
  readonly satisfied?: boolean;
}
