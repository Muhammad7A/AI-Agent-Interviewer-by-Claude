import type { Timestamp } from '@oi/contracts';
import type { OrganizationVersion } from '@oi/organization';
import type { BaselineSnapshotId } from './ids';

/** The time window of discovered data an assessment compares against the baseline. */
export interface ComparisonWindow {
  readonly from: Timestamp;
  readonly to: Timestamp;
}

/**
 * A reference to the official-structure baseline an assessment runs against —
 * the immutable `BaselineSnapshot` and the `OrganizationVersion` it captured
 * (from Organization's Published Language). Every assessment must carry one
 * (DRIFT2), which is also what keeps historical assessments reproducible (DRIFT7).
 */
export interface BaselineVersionRef {
  readonly snapshotId: BaselineSnapshotId;
  readonly organizationVersion: OrganizationVersion;
}
