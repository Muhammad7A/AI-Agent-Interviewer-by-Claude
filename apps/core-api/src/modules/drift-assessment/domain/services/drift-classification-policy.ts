import type { OfficialElementRef, DiscoveredElementRef } from '../value-objects/refs';
import type { ComparisonRule } from '../aggregates/comparison-rule';
import type { DriftClassification } from '../value-objects/policy-results';

/**
 * **Domain service (port).** Classifies a compared official/discovered pair into a
 * `DriftCategory` and a drift score, per a `ComparisonRule`. Pure decision;
 * interface only.
 */
export interface DriftClassificationPolicy {
  classify(
    official: OfficialElementRef,
    discovered: DiscoveredElementRef,
    rule: ComparisonRule,
  ): DriftClassification;
}
