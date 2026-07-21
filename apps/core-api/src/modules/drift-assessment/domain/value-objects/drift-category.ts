/**
 * The kinds of drift/misalignment this context detects — the comparison
 * vocabulary between declared intent and discovered reality.
 */
export type DriftCategory =
  | 'ProcessDrift'
  | 'RoleDrift'
  | 'ReportingDrift'
  | 'ApprovalDrift'
  | 'WorkflowDrift'
  | 'OwnershipAmbiguity'
  | 'ShadowOrganization'
  | 'ShadowLeadership'
  | 'GovernanceGap'
  | 'SopDeviation'
  | 'CapabilityGap'
  | 'OrganizationalMisalignment';
