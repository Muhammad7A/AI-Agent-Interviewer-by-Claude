import type { EngagementId, ValidationState } from '@oi/contracts';
import type { MappingHypothesis } from '../aggregates/mapping-hypothesis';
import type { MappingHypothesisId } from '../value-objects/ids';

/**
 * **Repository port** for `MappingHypothesis` aggregates. `findByValidationState`
 * supports reviewing still-`Proposed` mappings. Implementations are infrastructure.
 */
export interface MappingHypothesisRepository {
  findById(id: MappingHypothesisId): Promise<MappingHypothesis | null>;
  save(hypothesis: MappingHypothesis): Promise<void>;
  findByEngagement(engagementId: EngagementId): Promise<readonly MappingHypothesis[]>;
  findByValidationState(engagementId: EngagementId, state: ValidationState): Promise<readonly MappingHypothesis[]>;
  nextIdentity(): MappingHypothesisId;
}
