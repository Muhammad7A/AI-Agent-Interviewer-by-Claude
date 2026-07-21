import type { TenantId, EngagementId, KnowledgeNodeId } from '@oi/contracts';
import type { ConflictId } from '../value-objects/ids';

/** The nature of a conflict between recommendations. */
export type ConflictKind =
  | 'ResourceContention'
  | 'MutuallyExclusive'
  | 'SequencingConflict'
  | 'Redundant';

/** Whether a detected conflict has been adjudicated. */
export type ConflictStatus = 'Open' | 'Resolved';

/**
 * **Entity.** A detected conflict among recommendations, produced by
 * `RecommendationConflictPolicy`. Has identity and a lifecycle (open → resolved).
 *
 * Invariant: involves ≥2 recommendations.
 */
export interface RecommendationConflict {
  readonly id: ConflictId;
  readonly tenantId: TenantId;
  readonly engagementId: EngagementId;
  readonly kind: ConflictKind;
  readonly recommendationIds: readonly KnowledgeNodeId[];
  readonly status: ConflictStatus;
}
