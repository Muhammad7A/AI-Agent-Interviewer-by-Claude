import type { OrganizationId, EngagementId } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * Open a new Discovery & Assessment engagement for an organization.
 *
 * Composes (impl): Organization `EngagementRepository` (create), `Clock`,
 * `AuthorizationPort` (OpenEngagement), `DomainEventPublisher` (EngagementStarted),
 * `ApplicationEventPublisher` (EngagementOpened).
 */
export interface OpenEngagementCommand extends Command {
  readonly organizationId: OrganizationId;
  readonly name: string;
  /** Optional baseline pin (OrganizationVersion as a raw number at the boundary). */
  readonly baselineOrganizationVersion?: number;
}

export interface OpenEngagementResult {
  readonly engagementId: EngagementId;
}

export interface OpenEngagementHandler
  extends CommandHandler<OpenEngagementCommand, OpenEngagementResult> {}
