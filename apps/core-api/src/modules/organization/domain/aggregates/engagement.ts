import type { EngagementId, OrganizationId } from '../value-objects/ids';
import type { EngagementStatus } from '../value-objects/enums';
import type { OrganizationVersion } from '../value-objects/temporal';
import type { Timestamp } from '@oi/contracts';

/**
 * **Aggregate Root.** A Discovery & Assessment project (ADR-0007: Engagement
 * lives in the Organization context). Belongs to exactly one Organization (ORG7).
 * `id` is the Shared Kernel `EngagementId` — the scope key every other context
 * carries.
 *
 * `baselineVersion` pins the official-structure version this engagement's
 * discovery is assessed against — the anchor for future official-vs-discovered
 * (drift) comparison.
 */
export interface Engagement {
  readonly id: EngagementId;
  readonly organizationId: OrganizationId;
  readonly name: string;
  readonly status: EngagementStatus;
  readonly baselineVersion?: OrganizationVersion;
  readonly startedAt?: Timestamp;
  readonly completedAt?: Timestamp;
}
