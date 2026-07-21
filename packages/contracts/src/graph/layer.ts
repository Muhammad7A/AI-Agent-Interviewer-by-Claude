/**
 * The six lenses over the one graph.
 *
 * A "graph" (Department, Process, Workflow, Pain Point, Opportunity,
 * Recommendation) is a *query by `Layer`* over the single unified substrate —
 * not a separate store (ADR-0004, ADR-0005). The layer vocabulary is closed and
 * owned by the Shared Kernel; a lens is `findByLayer`.
 */
export type Layer =
  | 'Structural'
  | 'Capability'
  | 'Operational'
  | 'Diagnostic'
  | 'Opportunity'
  | 'Synthesis';
