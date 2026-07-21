/**
 * Transcript bounded context — domain layer (contracts only).
 *
 * The full internal surface: value objects, entities, the `Transcript` aggregate
 * root, repository + resolver ports, domain events, and invariants. The curated
 * external surface is `./published-language`.
 *
 * Every contract extends the Shared Kernel (`@oi/contracts`) without duplication
 * — `TranscriptId`, `SegmentId`, `CharSpan`, `EvidenceRef`, `SourcePerspective`,
 * `Timestamp` and `DomainEvent` are all reused, never re-declared. No behaviour,
 * persistence, infrastructure, application services, parsers, or extraction
 * appear in this layer.
 */
export * from './value-objects';
export * from './entities';
export * from './aggregates';
export * from './repositories';
export * from './events';
export * from './invariants';
