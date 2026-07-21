import type { Brand } from '../primitives/brand';

/**
 * Discriminator for an edge's predicate (e.g. "owns", "hands-off-via",
 * "addresses"). Context-owned values, Shared-Kernel-fixed shape — the same
 * sovereignty rule as `NodeType` (ADR-0005).
 */
export type EdgeType = Brand<string, 'EdgeType'>;
