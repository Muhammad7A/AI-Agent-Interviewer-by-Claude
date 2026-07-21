import type { OrganizationId, Timestamp } from '@oi/contracts';
import type { OrganizationVersion } from '@oi/organization';
import type { BaselineSnapshotId } from '../value-objects/ids';

/**
 * **Aggregate Root.** An immutable capture of *which* official-structure version
 * an assessment compares against. It does not copy the official model (that stays
 * in Organization) — it pins the `OrganizationVersion` so an assessment is
 * reproducible and historical assessments remain queryable (DRIFT7).
 */
export interface BaselineSnapshot {
  readonly id: BaselineSnapshotId;
  readonly organizationId: OrganizationId;
  readonly organizationVersion: OrganizationVersion;
  readonly capturedAt: Timestamp;
  readonly scopeDescription?: string;
}
