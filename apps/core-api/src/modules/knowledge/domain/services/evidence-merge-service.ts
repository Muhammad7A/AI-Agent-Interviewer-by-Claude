import type { Evidence } from '@oi/contracts';

/**
 * **Domain service (port).** Combines two evidence sets when nodes merge,
 * preserving all provenance (invariant K1) — no supporting evidence is ever lost
 * in a merge. Interface only.
 */
export interface EvidenceMergeService {
  merge(existing: readonly Evidence[], incoming: readonly Evidence[]): readonly Evidence[];
}
