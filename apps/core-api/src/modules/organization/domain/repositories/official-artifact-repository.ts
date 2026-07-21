import type { Timestamp } from '@oi/contracts';
import type { OrganizationId } from '../value-objects/ids';
import type { OfficialArtifactKind } from '../value-objects/enums';
import type { AnyOfficialArtifact } from '../aggregates/official';

/**
 * **Repository port** for the official artifacts (process, capability, system,
 * policy, role, workflow, approval chain). One port, keyed by `artifactKind`,
 * because they share the `OfficialArtifact` governance shape. `asOf` supports
 * historical queries (ORG9). Implementations are infrastructure.
 */
export interface OfficialArtifactRepository {
  findByKind(
    organizationId: OrganizationId,
    kind: OfficialArtifactKind,
    asOf?: Timestamp,
  ): Promise<readonly AnyOfficialArtifact[]>;
  save(artifact: AnyOfficialArtifact): Promise<void>;
}
