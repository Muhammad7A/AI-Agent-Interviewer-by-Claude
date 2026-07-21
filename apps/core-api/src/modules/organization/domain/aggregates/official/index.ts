import type { OfficialRole, OfficialCapability, OfficialSystem } from './catalog';
import type { OfficialProcess, OfficialWorkflow } from './operational';
import type { OfficialPolicy, OfficialApprovalChain } from './governance';

export * from './official-artifact';
export * from './catalog';
export * from './operational';
export * from './governance';

/** The discriminated union of every official artifact (keyed by `artifactKind`). */
export type AnyOfficialArtifact =
  | OfficialProcess
  | OfficialCapability
  | OfficialSystem
  | OfficialPolicy
  | OfficialRole
  | OfficialWorkflow
  | OfficialApprovalChain;
