import type { Claim } from '../aggregates/claim';
import type { GraphMutation } from '../value-objects/graph-mutation';

/**
 * **Domain service (port).** Plans how a batch of resolved claims becomes nodes
 * and edges, honouring the substrate invariants (N1–N5) and the Knowledge
 * invariants (K1–K3). Returns a `GraphMutation` plan (a value object);
 * *executing* the plan is an application concern, not defined here. Interface
 * only.
 */
export interface GraphConstructionService {
  plan(resolvedClaims: readonly Claim[]): GraphMutation;
}
