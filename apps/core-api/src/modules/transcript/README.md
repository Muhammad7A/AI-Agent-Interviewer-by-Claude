# Transcript context

Supporting context and **Open-Host Service** — it publishes the immutable segment
that every `EvidenceRef` resolves to. It is upstream of the entire evidence spine
(ai-engine extraction, Knowledge, Insights, Reporting). See `docs/DOMAIN_MODEL.md`
§7.1.

**This slice is the `domain/` layer only — contracts, no behaviour.** No
persistence, infrastructure, application services, parsers, or extraction. Every
contract extends the Shared Kernel (`@oi/contracts`) without duplication —
`TranscriptId`, `SegmentId`, `CharSpan`, `EvidenceRef`, `SourcePerspective` are
reused, never re-declared.

## The three guarantees this context makes structural

1. **Deterministic `EvidenceRef` resolution** — `TranscriptSegmentResolver`
   resolves `(transcriptId, segmentId)` to an immutable `TranscriptSegment`, and
   the ref's `CharSpan` to an exact substring of `segment.text` (T2, T6).
2. **Append-only after finalization** — a `Finalized` transcript never mutates;
   new content arrives only as new segments in a new `TranscriptVersion` (T4).
3. **Versioning that never breaks refs** — versions are additive supersets;
   resolution is version-agnostic, so old `EvidenceRef`s keep resolving (T5).
   Corrections are additive (`SegmentCorrection`), never in-place edits.

## `domain/` layout

| Folder | Contents |
|---|---|
| `aggregates/` | `Transcript` (aggregate root: append-only record + versions + corrections). |
| `entities/` | `TranscriptSegment` (immutable evidence anchor), `Speaker`, `Recording`. |
| `value-objects/` | `SegmentText`, `TimeRange`, `VersionNumber`, `TranscriptVersion`, `SegmentCorrection`, `TranscriptStatus`, `RecordingMedium`, `SpeakerLabel`; ids (`SpeakerId`, `RecordingId`; re-exported `TranscriptId`/`SegmentId`); re-exported `CharSpan`. |
| `repositories/` | `TranscriptRepository` + `TranscriptSegmentResolver` (the deterministic resolver). |
| `events/` | `TranscriptOpened`, `SegmentAppended`, `SpeakerIdentified`, `TranscriptFinalized`, `TranscriptVersionAppended`. |
| `invariants/` | `TRANSCRIPT_INVARIANTS` (T1–T8). |
| `published-language.ts` | The Open-Host surface: immutable segment + resolver + span. |

## Type-check

```bash
cd packages/contracts && npm install
cd ../../apps/core-api && ../../packages/contracts/node_modules/.bin/tsc -p tsconfig.json
```
