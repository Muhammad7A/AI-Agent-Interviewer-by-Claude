import type { EdgeType } from './edge-type';

/**
 * Base marker for predicate-specific edge attributes (e.g. a handoff's latency).
 * Each owning context extends this and discriminates on `edgeType`.
 */
export interface EdgeAttributes {
  readonly edgeType: EdgeType;
}
