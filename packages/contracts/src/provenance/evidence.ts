import type { EvidenceId } from '../primitives/ids';
import type { Timestamp } from '../primitives/scalars';
import type { EvidenceKind, SpeakerCertainty, Sentiment } from './evidence-kind';
import type { EvidenceRef } from './evidence-ref';
import type { Derivation } from './derivation';
import type { ExtractionMethod } from './extraction-method';

/**
 * The anchor of a piece of evidence: either an immutable transcript pointer
 * (stated/corroborated) or a derivation (inferred). A discriminated union keyed
 * by `anchorType`.
 */
export type EvidenceAnchor = EvidenceRef | Derivation;

/**
 * A single unit of provenance and the spine of the whole engine.
 *
 * Every node, edge and insight in the graph carries at least one `Evidence`
 * (invariant N1 / G1). Evidence is append-only. The `anchor` links a stated fact
 * to its transcript span, or an inference to its derivation — and inference
 * chains resolve transitively to stated segments (E1).
 */
export interface Evidence {
  readonly id: EvidenceId;
  readonly kind: EvidenceKind;
  readonly anchor: EvidenceAnchor;
  readonly certainty?: SpeakerCertainty;
  readonly sentiment?: Sentiment;
  /** Present when machine-extracted; absent for `ConsultantAsserted` evidence. */
  readonly method?: ExtractionMethod;
  readonly createdAt: Timestamp;
}
