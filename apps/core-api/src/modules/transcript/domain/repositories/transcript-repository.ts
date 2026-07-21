import type { TenantId, EngagementId, TranscriptId } from '@oi/contracts';
import type { Transcript } from '../aggregates/transcript';

/**
 * **Repository port** for `Transcript` aggregates. Tenant + engagement scoped by
 * contract (ADR-0003). Implementations live in infrastructure, not defined here.
 */
export interface TranscriptRepository {
  findById(tenantId: TenantId, engagementId: EngagementId, id: TranscriptId): Promise<Transcript | null>;

  save(transcript: Transcript): Promise<void>;

  findByEngagement(engagementId: EngagementId): Promise<readonly Transcript[]>;

  nextIdentity(): TranscriptId;
}
