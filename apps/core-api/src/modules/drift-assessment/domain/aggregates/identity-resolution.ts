import type { OrganizationId, EngagementId } from '@oi/contracts';
import type { IdentityResolutionId, MappingHypothesisId } from '../value-objects/ids';
import type { DiscoveredElementRef } from '../value-objects/refs';
import type { ReconciliationCandidate } from '../entities/reconciliation-candidate';

/** Whether the identity of a discovered element has been resolved to an official one. */
export type ResolutionStatus = 'Unresolved' | 'Resolved' | 'Ambiguous';

/**
 * **Aggregate Root.** The resolution state for a *single* discovered element:
 * its ranked `ReconciliationCandidate` entities and, once settled, the validated
 * mapping. `Ambiguous` is a first-class outcome — the platform never forces an
 * exact match and never pretends the mapping is truth until validated.
 *
 * When `status = 'Resolved'`, `resolvedMappingId` points at the validated
 * `MappingHypothesis`.
 */
export interface IdentityResolution {
  readonly id: IdentityResolutionId;
  readonly organizationId: OrganizationId;
  readonly engagementId: EngagementId;
  readonly discovered: DiscoveredElementRef;
  readonly candidates: readonly ReconciliationCandidate[];
  readonly status: ResolutionStatus;
  readonly resolvedMappingId?: MappingHypothesisId;
}
