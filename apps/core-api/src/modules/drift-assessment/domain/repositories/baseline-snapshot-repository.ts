import type { OrganizationId } from '@oi/contracts';
import type { OrganizationVersion } from '@oi/organization';
import type { BaselineSnapshot } from '../aggregates/baseline-snapshot';
import type { BaselineSnapshotId } from '../value-objects/ids';

/**
 * **Repository port** for `BaselineSnapshot` aggregates — immutable, so there is
 * no update path, only capture and retrieval (DRIFT7).
 */
export interface BaselineSnapshotRepository {
  findById(id: BaselineSnapshotId): Promise<BaselineSnapshot | null>;
  capture(snapshot: BaselineSnapshot): Promise<void>;
  findByVersion(organizationId: OrganizationId, version: OrganizationVersion): Promise<BaselineSnapshot | null>;
  nextIdentity(): BaselineSnapshotId;
}
