import type { Brand } from './brand';

/** An ISO-8601 timestamp string. */
export type Timestamp = Brand<string, 'Timestamp'>;

/**
 * A probability-like score in the closed interval [0, 1]. The range is a domain
 * invariant enforced by the owning context's factories — the contract fixes only
 * the branded primitive, not the guard.
 */
export type Score = Brand<number, 'Score'>;

/** A monotonic version counter for an aggregate. */
export type Version = Brand<number, 'Version'>;

/** The canonical, resolved human-readable label of a graph node. */
export type Label = Brand<string, 'Label'>;

/** A role title as described in an interview (e.g. "AP Clerk"). */
export type RoleLabel = Brand<string, 'RoleLabel'>;

/** A department name as described in an interview (e.g. "Finance"). */
export type DepartmentLabel = Brand<string, 'DepartmentLabel'>;
