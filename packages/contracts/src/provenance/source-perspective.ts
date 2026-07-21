import type { IntervieweeRef } from '../primitives/ids';
import type { RoleLabel, DepartmentLabel } from '../primitives/scalars';

/**
 * Whose viewpoint a piece of evidence represents.
 *
 * The engine is perspective-aware: the same fact stated by different sources is
 * retained rather than collapsed, and disagreement between perspectives is
 * treated as signal (often a bottleneck marker), never silently resolved.
 */
export interface SourcePerspective {
  readonly personRef: IntervieweeRef;
  readonly role: RoleLabel;
  readonly department: DepartmentLabel;
}
