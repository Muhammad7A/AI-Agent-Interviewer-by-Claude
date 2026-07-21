# contracts

The **single source of truth** for the `core-api` ↔ `ai-engine` runtime
boundary. Contract definitions here generate **both** TypeScript types and
Python (pydantic) models, so the two runtimes cannot silently drift.

Covers both interaction styles:

- **Synchronous** — interview turns (latency-sensitive request/response).
- **Asynchronous** — extraction, knowledge construction, detection (batch, job
  or event driven).

Every derived-data contract carries `EvidenceRef`s by construction — the
evidence rule is enforced at the boundary, not left to callers.

See `../../docs/ARCHITECTURE.md` §6. No contracts defined yet — this is the
ratified skeleton.
