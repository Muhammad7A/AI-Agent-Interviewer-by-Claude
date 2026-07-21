import type { EngagementId, ValidationState } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/** The consultant's disposition of an AI-proposed recommendation. */
export type ValidationDecision = 'Validate' | 'Reject' | 'Edit';

/**
 * Apply a consultant validation decision to an Insights `Recommendation` — the
 * human-in-the-loop gate where a proposal becomes (or is denied) authoritative
 * domain truth.
 *
 * NOTE (seam): Insights aggregates are **state-only** contracts (no transition
 * behaviour), so the transition — producing a Shared Kernel `ValidationEvent` and
 * advancing the `ValidationRecord` — is currently assembled at the application
 * boundary. This is a seam to close by promoting validation transitions to a
 * domain service (see the seams list).
 *
 * Composes (impl): Insights `InsightsNodeRepository`, `Clock`, `AuthorizationPort`
 * (ValidateRecommendation), `DomainEventPublisher` (ArtifactValidated /
 * DownstreamRescoreRequested).
 */
export interface ValidateRecommendationCommand extends Command {
  readonly engagementId: EngagementId;
  readonly recommendationId: string;
  readonly decision: ValidationDecision;
  readonly reason?: string;
}

export interface ValidateRecommendationResult {
  readonly recommendationId: string;
  readonly newState: ValidationState;
}

export interface ValidateRecommendationHandler
  extends CommandHandler<ValidateRecommendationCommand, ValidateRecommendationResult> {}
