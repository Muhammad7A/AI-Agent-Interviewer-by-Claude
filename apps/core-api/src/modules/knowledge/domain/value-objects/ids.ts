import type { Brand } from '@oi/contracts';

/**
 * Knowledge-context identities. They reuse the Shared Kernel's `Brand` primitive
 * (no duplication of the branding mechanism) for types the Shared Kernel does not
 * own, because they belong to this context's aggregates and entities.
 */

/** Identity of a `Claim` aggregate. */
export type ClaimId = Brand<string, 'ClaimId'>;

/** Identity of a `Contradiction` entity. */
export type ContradictionId = Brand<string, 'ContradictionId'>;
