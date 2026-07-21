/**
 * The atomic subject–predicate–object assertion a `Claim` carries, in raw
 * (pre-resolution) phrasing as extracted from a transcript segment. Resolution
 * (Stage 2 of the pipeline) maps these phrases onto canonical graph identities.
 */
export interface ClaimTriple {
  readonly subjectPhrase: string;
  readonly predicate: string;
  readonly objectPhrase: string;
}
