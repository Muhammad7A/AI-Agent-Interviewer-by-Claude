import type { Brand, Timestamp } from '@oi/contracts';

/**
 * A monotonic version of the official organizational structure. Bumped on every
 * structural change, so "official organizational data remains versioned" (ORG8)
 * and any point in history is addressable.
 */
export type OrganizationVersion = Brand<number, 'OrganizationVersion'>;

/**
 * The window during which a structural element is/was effective. `validTo`
 * absent means currently effective. Effective-dating is how "historical
 * structures remain queryable" (ORG9): elements are archived, never deleted.
 */
export interface EffectivePeriod {
  readonly validFrom: Timestamp;
  readonly validTo?: Timestamp;
}
