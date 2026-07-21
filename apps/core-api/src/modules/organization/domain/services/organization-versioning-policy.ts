import type { OrganizationVersion } from '../value-objects/temporal';

/**
 * **Domain service (port).** Produces the next `OrganizationVersion` when the
 * official structure changes, upholding ORG8 (official data remains versioned).
 * Interface only.
 */
export interface OrganizationVersioningPolicy {
  nextVersion(current: OrganizationVersion): OrganizationVersion;
}
