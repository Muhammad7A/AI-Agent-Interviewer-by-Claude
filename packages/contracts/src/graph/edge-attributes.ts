import type { EdgeType } from './edge-type';

/**
 * Base for predicate-specific edge attribute payloads, carrying the predicate
 * discriminant. Each owning context extends this with a literal `edgeType`
 * (e.g. `EdgeAttributes<'hands-off-via'>`), possibly adding fields (a handoff's
 * latency, a `precedes` rework flag). The Shared Kernel fixes only the seam.
 */
export interface EdgeAttributes<TType extends EdgeType = EdgeType> {
  readonly edgeType: TType;
}
