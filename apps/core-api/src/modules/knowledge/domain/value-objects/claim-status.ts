/**
 * The lifecycle status of a `Claim` as it moves from raw extraction to the graph.
 *  - `Unresolved`: extracted, not yet linked to nodes/edges.
 *  - `Resolved`: promoted into one or more nodes/edges (`resolvedInto` non-empty).
 *  - `Rejected`: discarded during resolution.
 */
export type ClaimStatus = 'Unresolved' | 'Resolved' | 'Rejected';
