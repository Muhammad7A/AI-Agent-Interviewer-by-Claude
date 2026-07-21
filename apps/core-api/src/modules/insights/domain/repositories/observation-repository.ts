import type { TenantId, EngagementId, ValidationState } from '@oi/contracts';
import type { Observation } from '../aggregates/observation';
import type { ObservationId } from '../value-objects/ids';

/**
 * **Repository port** for `Observation` aggregates. Tenant + engagement scoped.
 * `findByValidationState` supports draining `Proposed` observations for review.
 * Implementations are infrastructure, not defined here.
 */
export interface ObservationRepository {
  findById(tenantId: TenantId, engagementId: EngagementId, id: ObservationId): Promise<Observation | null>;
  save(observation: Observation): Promise<void>;
  findByValidationState(engagementId: EngagementId, state: ValidationState): Promise<readonly Observation[]>;
  nextIdentity(): ObservationId;
}
