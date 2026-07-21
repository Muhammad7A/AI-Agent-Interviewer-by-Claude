import type { Brand } from '@oi/contracts';

/** The seniority band of an official position. */
export type PositionLevel =
  | 'IndividualContributor'
  | 'TeamLead'
  | 'Manager'
  | 'SeniorManager'
  | 'Director'
  | 'VicePresident'
  | 'CLevel';

/** Depth in the official reporting hierarchy (0 = top). Branded to avoid mixing with other numbers. */
export type ReportingLevel = Brand<number, 'ReportingLevel'>;

/** The authority tier a policy or approval step sits at. */
export type ApprovalLevel = 'Operational' | 'Managerial' | 'Executive' | 'Board';
