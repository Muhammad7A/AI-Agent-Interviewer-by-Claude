import type { InvariantSpec } from '@oi/contracts';
import type { OrganizationInvariantCode } from './invariant-code';

/**
 * The Organization context's invariant registry — declarative data, not logic —
 * reusing the Shared Kernel's generic `InvariantSpec` (no duplication). These
 * encode the principle that this context holds **declared** organizational truth,
 * kept versioned and historically queryable.
 */
export const ORGANIZATION_INVARIANTS = {
  ORG1: {
    code: 'ORG1',
    name: 'Employee in exactly one department',
    statement: 'Every Employee belongs to exactly one Department.',
    appliesTo: ['Employee'],
  },
  ORG2: {
    code: 'ORG2',
    name: 'Department in exactly one organization',
    statement: 'Every Department (and every org unit) belongs to exactly one Organization.',
    appliesTo: ['BusinessUnit', 'Department', 'Team'],
  },
  ORG3: {
    code: 'ORG3',
    name: 'Reporting graph is acyclic',
    statement: 'The set of ReportingLines forms an acyclic graph.',
    appliesTo: ['ReportingLine'],
  },
  ORG4: {
    code: 'ORG4',
    name: 'Workflow has an owner department',
    statement: 'Every OfficialWorkflow has an owner Department (ownerDepartmentId).',
    appliesTo: ['OfficialWorkflow'],
  },
  ORG5: {
    code: 'ORG5',
    name: 'Capability has an owner',
    statement: 'Every OfficialCapability has an owner.',
    appliesTo: ['OfficialCapability'],
  },
  ORG6: {
    code: 'ORG6',
    name: 'Policy has at least one owner',
    statement: 'Every OfficialPolicy has at least one owner (owners is non-empty).',
    appliesTo: ['OfficialPolicy'],
  },
  ORG7: {
    code: 'ORG7',
    name: 'Engagement in one organization',
    statement: 'Every Engagement belongs to exactly one Organization.',
    appliesTo: ['Engagement'],
  },
  ORG8: {
    code: 'ORG8',
    name: 'Official data is versioned',
    statement:
      'Official organizational data remains versioned: the Organization carries an OrganizationVersion and structural changes produce a new version.',
    appliesTo: ['Organization', 'OfficialArtifact'],
  },
  ORG9: {
    code: 'ORG9',
    name: 'History remains queryable',
    statement:
      'Historical structures remain queryable: elements are effective-dated and archived (status Archived/Merged), never deleted.',
    appliesTo: ['BusinessUnit', 'Department', 'Team', 'Position', 'Employee', 'ReportingLine', 'OfficialArtifact'],
  },
} as const satisfies Record<OrganizationInvariantCode, InvariantSpec<OrganizationInvariantCode>>;
