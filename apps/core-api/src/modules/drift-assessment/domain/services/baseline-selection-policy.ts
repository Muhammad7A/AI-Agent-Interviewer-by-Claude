import type { BaselineVersionRef, ComparisonWindow } from '../value-objects/assessment-vos';

/**
 * **Domain service (port).** Selects which official baseline an assessment should
 * compare against, given the available baselines and the comparison window — so
 * discovered data is compared against the official structure that was effective at
 * the time. Interface only.
 */
export interface BaselineSelectionPolicy {
  selectBaseline(available: readonly BaselineVersionRef[], window: ComparisonWindow): BaselineVersionRef;
}
