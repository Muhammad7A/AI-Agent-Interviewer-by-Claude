import type { EngagementId } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * **Priority use case #2.** Turn validated `Claim`s into graph updates.
 *
 * Orchestration (implementation — domain rules live in Knowledge policies):
 *  1. `AuthorizationPort` (BuildKnowledgeGraph) + scope.
 *  2. Load `Unresolved` `Claim`s (Knowledge `ClaimRepository.findByStatus`), or the
 *     given `claimIds`.
 *  3. Resolution: Knowledge `EntityResolutionPolicy` (optionally aided by the
 *     `KnowledgeConstruction` AI ACL), then `GraphConstructionService` produces a
 *     `GraphMutation` plan — enforcing evidence-first (N1) and endpoint integrity (N3).
 *  4. Persist node/edge aggregates **individually** (Knowledge node/edge repos);
 *     graph-wide consistency is **eventual** (ADR-0006), reconciled via events, not
 *     one transaction. `AnchorProtectionPolicy` guards validated anchors (N4).
 *  5. Mark resolved `Claim`s `Resolved`; publish substrate events
 *     (KnowledgeNodeAdded / Merged / EdgeAdded) + application event
 *     (KnowledgeGraphUpdated).
 *
 * Each node/edge write is its own `UnitOfWork` — never a single transaction over
 * the whole graph.
 */
export interface BuildKnowledgeGraphCommand extends Command {
  readonly engagementId: EngagementId;
  /** Omit to process all currently-unresolved claims. */
  readonly claimIds?: readonly string[];
}

export interface BuildKnowledgeGraphResult {
  readonly claimsResolved: number;
  readonly nodesAdded: number;
  readonly edgesAdded: number;
  readonly nodesMerged: number;
}

export interface BuildKnowledgeGraphHandler
  extends CommandHandler<BuildKnowledgeGraphCommand, BuildKnowledgeGraphResult> {}
