import type { Timestamp } from '@oi/contracts';
import type { OrganizationId } from '../value-objects/ids';
import type { OrgUnitKind, OrgUnitIdentifier } from '../value-objects/codes';
import type { AnyOrgUnit } from '../aggregates/org-units';

/**
 * **Repository port** for the org-unit hierarchy (BusinessUnit / Department /
 * Team). `asOf` supports querying historical structures (ORG9); omitting it
 * returns the currently-effective units. Implementations are infrastructure.
 */
export interface OrgUnitRepository {
  findById(id: OrgUnitIdentifier): Promise<AnyOrgUnit | null>;
  save(unit: AnyOrgUnit): Promise<void>;
  findByKind(organizationId: OrganizationId, kind: OrgUnitKind, asOf?: Timestamp): Promise<readonly AnyOrgUnit[]>;
  findChildren(parent: OrgUnitIdentifier, asOf?: Timestamp): Promise<readonly AnyOrgUnit[]>;
}
