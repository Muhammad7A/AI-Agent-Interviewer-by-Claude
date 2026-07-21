/**
 * How a piece of evidence came to be.
 *  - `Stated`: directly asserted by an interviewee.
 *  - `Corroborated`: independently supported by multiple sources.
 *  - `Inferred`: derived by a detector from a graph pattern (see `Derivation`).
 *  - `ConsultantAsserted`: added by a human consultant (authoritative).
 */
export type EvidenceKind = 'Stated' | 'Corroborated' | 'Inferred' | 'ConsultantAsserted';

/** How strongly the source expressed the underlying claim. */
export type SpeakerCertainty = 'Hedged' | 'Tentative' | 'Confident' | 'Certain';

/** Affective colouring of the source's statement. */
export type Sentiment = 'Frustrated' | 'Negative' | 'Neutral' | 'Positive';
