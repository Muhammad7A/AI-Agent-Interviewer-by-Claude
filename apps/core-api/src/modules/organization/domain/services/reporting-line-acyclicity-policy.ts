import type { ReportingLine } from '../aggregates/reporting-line';

/**
 * **Domain service (port).** Guards invariant ORG3: the official reporting graph
 * must stay acyclic. `wouldIntroduceCycle` tests a candidate line against the
 * existing set; `isAcyclic` validates a whole set. Pure predicates, interface only.
 */
export interface ReportingLineAcyclicityPolicy {
  wouldIntroduceCycle(candidate: ReportingLine, existing: readonly ReportingLine[]): boolean;
  isAcyclic(lines: readonly ReportingLine[]): boolean;
}
