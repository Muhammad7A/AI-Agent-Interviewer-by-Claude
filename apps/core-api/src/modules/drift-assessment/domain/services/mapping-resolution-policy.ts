import type { DiscoveredElementRef, OfficialElementRef } from '../value-objects/refs';
import type { ReconciliationProposal } from '../value-objects/policy-results';

/**
 * **Domain service (port).** Proposes ranked reconciliation candidates for a
 * discovered element against a set of official candidates — the identity-
 * resolution matcher. It proposes value objects with confidence + rationale; it
 * does **not** assert identity (that requires validation). Interface only.
 */
export interface MappingResolutionPolicy {
  resolve(
    discovered: DiscoveredElementRef,
    officialCandidates: readonly OfficialElementRef[],
  ): readonly ReconciliationProposal[];
}
