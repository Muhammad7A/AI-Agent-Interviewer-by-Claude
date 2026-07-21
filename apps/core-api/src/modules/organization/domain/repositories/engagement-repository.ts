import type { EngagementId, OrganizationId } from '../value-objects/ids';
import type { Engagement } from '../aggregates/engagement';

/** **Repository port** for `Engagement` aggregates (ADR-0007). */
export interface EngagementRepository {
  findById(id: EngagementId): Promise<Engagement | null>;
  save(engagement: Engagement): Promise<void>;
  findByOrganization(organizationId: OrganizationId): Promise<readonly Engagement[]>;
  nextIdentity(): EngagementId;
}
