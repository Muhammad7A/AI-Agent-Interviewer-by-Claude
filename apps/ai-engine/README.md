# ai-engine (FastAPI)

**Stateless AI cognition.** Organized by capability, each a pure function of its
inputs → structured output. Owns **no** business truth.

Capabilities: interview cognition · conversation memory · extraction · knowledge
construction · bottleneck detection · opportunity detection.

## Rules

- Never writes to the primary database. Never resolves tenancy or auth on its
  own — it receives already-scoped context from `core-api` and returns results
  tagged with the same scope for `core-api` to persist.
- Same layering as `core-api`: `domain` · `application` · `infrastructure` ·
  `presentation`, dependencies pointing inward. The domain is pure and
  framework-free.
- **The evidence rule:** every structured item emitted (fact, bottleneck,
  opportunity) carries one or more `EvidenceRef`s pointing at the transcript
  segments that justify it. Output without evidence is a contract violation.
- The LLM sits behind a domain port. No domain/application code names a model or
  SDK. Default to the latest Claude models; a provider change is an
  infrastructure-only change.

See `../../docs/ARCHITECTURE.md` and `../../docs/adr/`. No business logic yet —
this is the ratified skeleton.
