import type { SubGraph } from '@oi/knowledge';
import type { PainPoint } from '../nodes/diagnostic/pain-point';
import type { Finding } from '../aggregates/finding';
import type { RootCauseHypothesis } from '../entities/root-cause-hypothesis';

/**
 * **Domain service (port).** Proposes root-cause hypotheses for a group of pain
 * points, drawing on the supporting findings and the structural context of the
 * Knowledge graph (`SubGraph`, from Knowledge's Published Language — read-only,
 * Insights never mutates it). Interface only.
 */
export interface RootCauseAnalysisPolicy {
  analyze(
    painPoints: readonly PainPoint[],
    findings: readonly Finding[],
    context: SubGraph,
  ): readonly RootCauseHypothesis[];
}
