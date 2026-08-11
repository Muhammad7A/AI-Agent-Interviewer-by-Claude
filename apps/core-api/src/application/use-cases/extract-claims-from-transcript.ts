import type { EngagementId, TranscriptId } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * The focused AI-extraction step: transcript → validated `Claim`s. This is the
 * granular use case `StartTranscriptAnalysis` composes; it is exposed separately
 * so extraction can be re-run (e.g. with a better model) without the broader flow.
 *
 * Composes (impl): Transcript `TranscriptRepository` + `TranscriptSegmentResolver`,
 * `ClaimExtractionPort` (AI ACL), Knowledge `ClaimRepository`, `UnitOfWork`.
 */
export interface ExtractClaimsFromTranscriptCommand extends Command {
  readonly engagementId: EngagementId;
  readonly transcriptId: TranscriptId;
}

/** A one-line outcome per extracted claim (opaque `claimId` at the boundary). */
export interface ExtractedClaimSummary {
  readonly claimId: string;
  readonly targetLayer: string;
  readonly accepted: boolean;
}

export interface ExtractClaimsFromTranscriptResult {
  readonly claims: readonly ExtractedClaimSummary[];
}

export interface ExtractClaimsFromTranscriptHandler
  extends CommandHandler<ExtractClaimsFromTranscriptCommand, ExtractClaimsFromTranscriptResult> {}
