import type { PainPoint } from '../nodes/diagnostic/pain-point';
import type { PainMergeDecision } from '../value-objects/policy-results';

/**
 * **Domain service (port).** Detects duplicate pain points (the same friction
 * described by different sources) and proposes merges. A pure decision; no side
 * effects. Interface only.
 */
export interface PainDeduplicationPolicy {
  deduplicate(painPoints: readonly PainPoint[]): readonly PainMergeDecision[];
}
