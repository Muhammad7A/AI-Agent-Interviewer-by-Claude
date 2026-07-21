import type { ValidationRecord } from '@oi/contracts';

/**
 * **Domain service (port).** The N4 / G5 gate: given an artifact's current
 * validation standing, may a machine recompute overwrite it? A consultant-
 * validated anchor must be protected. Pure predicate, interface only.
 */
export interface AnchorProtectionPolicy {
  mayOverwrite(validation: ValidationRecord): boolean;
}
