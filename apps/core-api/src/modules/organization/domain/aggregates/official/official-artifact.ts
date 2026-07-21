import type { OrganizationId } from '../../value-objects/ids';
import type { OfficialArtifactKind, OrgLifecycleStatus } from '../../value-objects/enums';
import type { OrganizationVersion, EffectivePeriod } from '../../value-objects/temporal';
import type { DeclarationRecord } from '../../value-objects/refs';

/**
 * The common governance shape of every official artifact (process, capability,
 * system, policy, role, workflow, approval chain), discriminated by
 * `artifactKind`. Each concrete artifact extends this with its own id, owner, and
 * type-specific fields.
 *
 * Every official artifact is versioned (ORG8), effective-dated (ORG9), and
 * declared (not discovered) — carrying an optional `DeclarationRecord` rather than
 * interview `Evidence`. This uniform shape is what future drift detection compares
 * against the discovered Knowledge graph.
 */
export interface OfficialArtifact<K extends OfficialArtifactKind = OfficialArtifactKind> {
  readonly artifactKind: K;
  readonly organizationId: OrganizationId;
  readonly name: string;
  readonly status: OrgLifecycleStatus;
  readonly version: OrganizationVersion;
  readonly effectivePeriod: EffectivePeriod;
  readonly declaration?: DeclarationRecord;
}
