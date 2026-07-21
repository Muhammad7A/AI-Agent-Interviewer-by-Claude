import type { IdentityResolution } from '../aggregates/identity-resolution';
import type { IdentityResolutionId } from '../value-objects/ids';

/**
 * **Domain service (port).** Orders unresolved identity resolutions by how much
 * resolving them would sharpen the assessment (uncertainty × downstream impact),
 * so consultants reconcile the highest-value ambiguities first. Interface only.
 */
export interface ReconciliationPrioritizationPolicy {
  prioritize(resolutions: readonly IdentityResolution[]): readonly IdentityResolutionId[];
}
