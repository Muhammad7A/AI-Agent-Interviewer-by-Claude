import type { Brand } from './brand';

/** The client organization / tenant. The isolation boundary for all data. */
export type TenantId = Brand<string, 'TenantId'>;

/** Alias: an organization *is* a tenant. */
export type OrganizationId = TenantId;

/** A Discovery & Assessment project — the scope of one knowledge graph. */
export type EngagementId = Brand<string, 'EngagementId'>;

/** A platform user account (from Identity & Access). */
export type UserId = Brand<string, 'UserId'>;

/** Identity of a node in the unified knowledge graph. */
export type KnowledgeNodeId = Brand<string, 'KnowledgeNodeId'>;

/** Identity of an edge in the unified knowledge graph. */
export type KnowledgeEdgeId = Brand<string, 'KnowledgeEdgeId'>;

/** An immutable interview transcript. */
export type TranscriptId = Brand<string, 'TranscriptId'>;

/** A stable segment within a transcript — the finest evidence anchor. */
export type SegmentId = Brand<string, 'SegmentId'>;

/** Identity of a single piece of provenance. */
export type EvidenceId = Brand<string, 'EvidenceId'>;

/** Identity of a validation-lifecycle transition. */
export type ValidationEventId = Brand<string, 'ValidationEventId'>;

/** Identity of a domain event. */
export type EventId = Brand<string, 'EventId'>;

/** A pseudonymized reference to an interviewee. Never carries PII. */
export type IntervieweeRef = Brand<string, 'IntervieweeRef'>;
