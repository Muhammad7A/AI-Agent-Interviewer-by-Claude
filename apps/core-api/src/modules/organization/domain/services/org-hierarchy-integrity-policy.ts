import type { AnyOrgUnit } from '../aggregates/org-units';
import type { OrgUnitIdentifier } from '../value-objects/codes';

/**
 * **Domain service (port).** Validates placement of an org unit in the hierarchy:
 * the parent must belong to the same Organization (ORG2) and the resulting
 * hierarchy must remain acyclic. Interface only.
 */
export interface OrgHierarchyIntegrityPolicy {
  isValidPlacement(unit: AnyOrgUnit, parent: OrgUnitIdentifier | null, existing: readonly AnyOrgUnit[]): boolean;
}
