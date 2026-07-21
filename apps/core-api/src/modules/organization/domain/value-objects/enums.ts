/**
 * Closed enumerations for the official organizational model. String-literal
 * unions — no runtime footprint.
 */

/** How an employee is engaged. */
export type EmploymentType = 'FullTime' | 'PartTime' | 'Contractor' | 'Temporary' | 'Intern';

/** The status of the organization as a whole. */
export type OrganizationStatus = 'Onboarding' | 'Active' | 'Suspended' | 'Inactive';

/**
 * The lifecycle status of a structural element. `Archived`/`Merged` elements are
 * retained (never deleted) so historical structures remain queryable.
 */
export type OrgLifecycleStatus = 'Planned' | 'Active' | 'Archived' | 'Merged';

/** Solid (direct) vs dotted (matrix) reporting. */
export type ReportingType = 'Solid' | 'Dotted';

/** How often an official process is meant to run. */
export type Cadence =
  | 'Continuous'
  | 'Daily'
  | 'Weekly'
  | 'Monthly'
  | 'Quarterly'
  | 'Annual'
  | 'AdHoc';

/** The lifecycle of a Discovery & Assessment engagement (ADR-0007). */
export type EngagementStatus = 'Draft' | 'Active' | 'Ingesting' | 'Frozen' | 'Closed';

/** The kind of official artifact — the governance/catalog discriminant. */
export type OfficialArtifactKind =
  | 'Process'
  | 'Capability'
  | 'System'
  | 'Policy'
  | 'Role'
  | 'Workflow'
  | 'ApprovalChain';
