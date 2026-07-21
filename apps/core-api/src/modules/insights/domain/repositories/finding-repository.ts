import type { TenantId, EngagementId, ValidationState } from '@oi/contracts';
import type { Finding } from '../aggregates/finding';
import type { FindingId } from '../value-objects/ids';

/**
 * **Repository port** for `Finding` aggregates. Tenant + engagement scoped.
 * Implementations are infrastructure, not defined here.
 */
export interface FindingRepository {
  findById(tenantId: TenantId, engagementId: EngagementId, id: FindingId): Promise<Finding | null>;
  save(finding: Finding): Promise<void>;
  findByValidationState(engagementId: EngagementId, state: ValidationState): Promise<readonly Finding[]>;
  nextIdentity(): FindingId;
}
