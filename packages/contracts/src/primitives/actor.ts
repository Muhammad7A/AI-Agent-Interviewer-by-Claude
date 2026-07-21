import type { UserId } from './ids';

/** The kind of actor responsible for a domain mutation. */
export type ActorType =
  | 'Consultant'
  | 'PlatformAdmin'
  | 'OrgAdmin'
  | 'Interviewee'
  | 'SystemAgent';

/**
 * The actor responsible for a domain mutation or event. Resolved by the
 * Identity & Access context and carried as Published Language so every other
 * context can attribute changes without depending on the IAM model.
 */
export interface ActorRef {
  readonly actorType: ActorType;
  readonly userId: UserId;
}
