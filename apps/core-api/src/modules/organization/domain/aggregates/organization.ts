import type { OrganizationId } from '../value-objects/ids';
import type { OrganizationStatus } from '../value-objects/enums';
import type { OrganizationVersion } from '../value-objects/temporal';
import type { DeclarationRecord } from '../value-objects/refs';

/**
 * **Aggregate Root.** The client organization — the tenant and the root of all
 * official structure. `id` is the Shared Kernel `OrganizationId` (== `TenantId`).
 *
 * `version` carries the official-structure version (ORG8); every other structural
 * aggregate references this organization by id (ORG2). This aggregate holds only
 * organization-level facts — declared, never discovered.
 */
export interface Organization {
  readonly id: OrganizationId;
  readonly legalName: string;
  readonly displayName?: string;
  readonly status: OrganizationStatus;
  readonly version: OrganizationVersion;
  readonly declaration?: DeclarationRecord;
}
