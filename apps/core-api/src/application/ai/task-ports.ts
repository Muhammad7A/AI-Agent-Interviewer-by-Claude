import type { Layer, TranscriptId, SegmentId } from '@oi/contracts';
import type { AiResult } from './ai-engine-core';

/**
 * Task-specific AI ports. Each returns **DTO proposals** — never domain objects.
 * The use case maps a DTO into a domain candidate (with `validation.state =
 * 'Proposed'`) and validates it before persistence (ADR-0008 rule 3-4). Only two
 * ports are fleshed out here (the ones the priority use cases need); the rest
 * follow the identical shape over the generic `AiEnginePort`.
 */

/* ---- Claim extraction (StartTranscriptAnalysis) ---- */

/** A segment's immutable text handed to extraction (built from the Transcript aggregate). */
export interface SegmentTextDto {
  readonly segmentId: SegmentId;
  readonly text: string;
}

export interface ClaimExtractionInput {
  readonly transcriptId: TranscriptId;
  readonly segments: readonly SegmentTextDto[];
}

/**
 * A proposed claim — a raw subject/predicate/object with the span it came from
 * and a raw extraction confidence. Not a domain `Claim`: the handler maps it into
 * one, re-anchoring the span against the immutable segment (evidence-first).
 */
export interface ExtractedClaimDto {
  readonly subjectPhrase: string;
  readonly predicate: string;
  readonly objectPhrase: string;
  readonly targetLayer: Layer;
  readonly segmentId: SegmentId;
  readonly charStart: number;
  readonly charEnd: number;
  readonly extractionConfidence: number;
}

export interface ClaimExtractionOutput {
  readonly claims: readonly ExtractedClaimDto[];
}

/** The ACL port a use case calls to extract claims from a transcript. */
export interface ClaimExtractionPort {
  extract(input: ClaimExtractionInput, correlationId: string): Promise<AiResult<ClaimExtractionOutput>>;
}

/* ---- Mapping resolution (DetectDrift identity resolution) ---- */

/** An official element offered as a candidate match, in primitive form (handler maps to a domain ref). */
export interface OfficialCandidateDto {
  readonly officialKind: string;
  readonly officialId: string;
  readonly label: string;
}

/** The discovered element whose identity is being resolved. */
export interface MappingResolutionInput {
  readonly discoveredKind: string;
  readonly discoveredLabel?: string;
  readonly discoveredId?: string;
  readonly candidates: readonly OfficialCandidateDto[];
}

/** A ranked, explainable suggestion — a hypothesis, never an assertion. */
export interface MappingSuggestionDto {
  readonly officialId: string;
  readonly matchConfidence: number;
  readonly rationale: string;
}

export interface MappingResolutionOutput {
  readonly suggestions: readonly MappingSuggestionDto[];
}

/** The ACL port a use case calls to propose identity mappings (discovered ↔ official). */
export interface MappingResolutionPort {
  resolve(input: MappingResolutionInput, correlationId: string): Promise<AiResult<MappingResolutionOutput>>;
}
