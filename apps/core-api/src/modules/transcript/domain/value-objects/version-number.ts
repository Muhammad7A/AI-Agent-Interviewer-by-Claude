import type { Brand } from '@oi/contracts';

/**
 * A monotonic transcript version number (starting at 1). Strictly increases with
 * each finalized snapshot; versioning is additive, so a higher number's segment
 * set is always a superset of a lower one's (T5).
 */
export type VersionNumber = Brand<number, 'VersionNumber'>;
