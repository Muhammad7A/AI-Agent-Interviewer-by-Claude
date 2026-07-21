import type { EngagementId, TranscriptId } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * **Priority use case #1.** Kick off analysis of a finalized transcript: extract
 * claims via the AI ACL, validate them, and forward accepted output into the
 * Knowledge flow.
 *
 * Orchestration (implementation — no domain logic here):
 *  1. `AuthorizationPort` (StartTranscriptAnalysis) + verify `ctx` scope.
 *  2. Load the **finalized** Transcript (Transcript `TranscriptRepository`);
 *     reject if not `Finalized` (evidence must be immutable).
 *  3. Build `ClaimExtractionInput` from the immutable segments; call
 *     `ClaimExtractionPort` (AI ACL). On `AiEngineError` → `AppError('AiUnavailable')`.
 *  4. Map each `ExtractedClaimDto` → a Knowledge `Claim` candidate with
 *     `validation.state = 'Proposed'`, re-anchoring the span against the immutable
 *     segment via the Transcript resolver. **Never persist AI output directly.**
 *  5. Drop candidates whose span/segment does not resolve (evidence-first);
 *     count accepted vs rejected.
 *  6. Persist accepted `Claim`s (Knowledge `ClaimRepository`) inside a `UnitOfWork`.
 *  7. Publish domain events (ClaimExtracted) + application event
 *     (TranscriptAnalysisStarted). Optionally enqueue BuildKnowledgeGraph.
 *
 * Idempotent on `idempotencyKey` (re-run of the same transcript is a no-op).
 */
export interface StartTranscriptAnalysisCommand extends Command {
  readonly engagementId: EngagementId;
  readonly transcriptId: TranscriptId;
}

export interface StartTranscriptAnalysisResult {
  readonly analysisId: string;
  readonly extractedClaimCount: number;
  readonly acceptedClaimCount: number;
  readonly rejectedClaimCount: number;
}

export interface StartTranscriptAnalysisHandler
  extends CommandHandler<StartTranscriptAnalysisCommand, StartTranscriptAnalysisResult> {}
