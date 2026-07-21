import type { EngagementId } from '@oi/contracts';
import type { IdentityResolution, ResolutionStatus } from '../aggregates/identity-resolution';
import type { IdentityResolutionId } from '../value-objects/ids';

/** **Repository port** for `IdentityResolution` aggregates. */
export interface IdentityResolutionRepository {
  findById(id: IdentityResolutionId): Promise<IdentityResolution | null>;
  save(resolution: IdentityResolution): Promise<void>;
  findByEngagement(engagementId: EngagementId): Promise<readonly IdentityResolution[]>;
  findByStatus(engagementId: EngagementId, status: ResolutionStatus): Promise<readonly IdentityResolution[]>;
  nextIdentity(): IdentityResolutionId;
}
