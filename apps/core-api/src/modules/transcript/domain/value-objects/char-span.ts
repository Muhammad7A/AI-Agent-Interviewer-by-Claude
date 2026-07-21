/**
 * The Transcript context uses the **Shared Kernel's** `CharSpan` unchanged (no
 * duplication). This is deliberate: `EvidenceRef.span` is that exact `CharSpan`,
 * so a span produced against a segment here is the same span the evidence spine
 * resolves — a half-open `[start, end)` range indexing into a segment's `text`.
 */
export type { CharSpan } from '@oi/contracts';
