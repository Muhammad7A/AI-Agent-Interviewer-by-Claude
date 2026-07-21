/**
 * Closed enumerations used by the Knowledge node attribute contracts. All are
 * string-literal unions — pure type-level, no runtime footprint. Values reflect
 * *described* reality (as reported in interviews), not a normative taxonomy.
 */

/** Seniority of a role, as described. */
export type Seniority = 'Junior' | 'Mid' | 'Senior' | 'Lead' | 'Executive';

/** How often a process runs. */
export type Cadence =
  | 'Continuous'
  | 'Daily'
  | 'Weekly'
  | 'Monthly'
  | 'Quarterly'
  | 'Annual'
  | 'AdHoc';

/** How critical a process is to the organization. */
export type Criticality = 'Low' | 'Medium' | 'High' | 'Critical';

/** How frequently a workflow or activity occurs. */
export type Frequency = 'Rare' | 'Occasional' | 'Frequent' | 'Continuous';

/** The degree to which an activity is automated today. */
export type AutomationLevel = 'Manual' | 'SystemAssisted' | 'Automated';

/** The channel over which a handoff occurs — where context and time are lost. */
export type HandoffChannel = 'Email' | 'Meeting' | 'System' | 'Document' | 'Verbal' | 'None';

/** Described quality of a system's integration with its neighbours. */
export type IntegrationQuality = 'Poor' | 'Partial' | 'Good' | 'Unknown';

/** The form an artifact takes as it moves through a workflow. */
export type ArtifactFormat =
  | 'Document'
  | 'Spreadsheet'
  | 'Ticket'
  | 'Dataset'
  | 'Email'
  | 'Form'
  | 'Other';
