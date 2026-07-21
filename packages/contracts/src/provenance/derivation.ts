import type { EvidenceId } from '../primitives/ids';

/**
 * How an `Inferred` piece of evidence was produced: the detector that fired, the
 * graph pattern it matched, its input evidence, and a human-readable
 * explanation. The anchor for inferred evidence.
 *
 * Invariant E1 (transitive resolvability): `inputEvidence` is non-empty and each
 * referenced item is itself resolvable within the engagement — so every
 * inference resolves transitively down to `Stated` transcript segments. This is
 * what makes inferred insights auditable.
 *
 * Discriminated from `EvidenceRef` by `anchorType`.
 */
export interface Derivation {
  readonly anchorType: 'Derivation';
  readonly detectorId: string;
  readonly graphPattern: string;
  readonly inputEvidence: readonly EvidenceId[];
  readonly explanation: string;
}
