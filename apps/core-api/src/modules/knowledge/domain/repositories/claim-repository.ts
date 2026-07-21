import type { TenantId, EngagementId } from '@oi/contracts';
import type { Claim } from '../aggregates/claim';
import type { ClaimId } from '../value-objects/ids';
import type { ClaimStatus } from '../value-objects/claim-status';

/**
 * **Repository port** for `Claim` aggregates. Tenant + engagement scoped.
 * `findByStatus` supports the resolution stage (e.g. draining `Unresolved`
 * claims). Implementations are infrastructure, not defined here.
 */
export interface ClaimRepository {
  findById(tenantId: TenantId, engagementId: EngagementId, id: ClaimId): Promise<Claim | null>;

  save(claim: Claim): Promise<void>;

  findByStatus(engagementId: EngagementId, status: ClaimStatus): Promise<readonly Claim[]>;

  nextIdentity(): ClaimId;
}
