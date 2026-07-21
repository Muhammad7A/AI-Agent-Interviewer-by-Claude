/**
 * Discriminator for an edge's predicate (e.g. "owns", "hands-off-via",
 * "addresses"). An **open string** with context-owned values and a
 * Shared-Kernel-fixed seam — the same sovereignty rule as `NodeType` (ADR-0005).
 * Each context narrows this to a literal union.
 */
export type EdgeType = string;
