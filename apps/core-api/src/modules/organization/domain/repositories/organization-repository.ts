import type { OrganizationId } from '../value-objects/ids';
import type { Organization } from '../aggregates/organization';

/**
 * **Repository port** for the `Organization` aggregate root. Implementations are
 * infrastructure, not defined here.
 */
export interface OrganizationRepository {
  findById(id: OrganizationId): Promise<Organization | null>;
  save(organization: Organization): Promise<void>;
  nextIdentity(): OrganizationId;
}
