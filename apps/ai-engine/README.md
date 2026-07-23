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

See `../../docs/ARCHITECTURE.md` and `../../docs/adr/`. The hexagonal `src/`
tree is the ratified skeleton (still contracts only). The **runnable interview
loop** lives in the `ai_engine/` Python package below.

---

## Runnable interview loop (thin slice)

A deliberately-thin, working implementation of the interview cognition
capability — enough to run the Year-0/1 gate experiments (candor, elicitation,
value density, robustness) on real people. It is **not** the full skeleton; it
under-builds on purpose (see `../../docs/FIVE_YEAR_ROADMAP.md`, Year 0–1).

What it does:

- Conducts a hypothesis-driven, tier-laddering interview (`ai_engine/interview/`)
  that pushes toward Tier 2–4 disclosure — the only tiers with commercial value.
- Produces an **immutable, evidence-addressable transcript** (`ai_engine/transcript/`):
  every segment is a fixed evidence anchor, so any later claim resolves to an
  exact source span via `EvidenceRef` (the evidence-first invariant, C1/C5).
- Writes only the **testimony layer** of the learning dataset as append-only
  JSONL (`ai_engine/persistence/`) — never fuses interpretation/validation/outcome (C7).
- Runs **with no model and no API key** via a deterministic mock interviewer and
  a simulated persona that holds known, tier-tagged truths behind a candor dial —
  this doubles as the in-code candor experiment and the synthetic-org testbed
  (research program Q1/Q2/Q16).

### Run it

```bash
cd apps/ai-engine

# Fully automated: the engine interviews a simulated employee (no key needed).
python3 -m ai_engine.cli --simulated --candor neutral
python3 -m ai_engine.cli --simulated --candor guarded   # withholds Tier 2-4
python3 -m ai_engine.cli --simulated --candor open       # discloses everything

# Live interview at the terminal (you play the employee).
python3 -m ai_engine.cli

# Tests (stdlib only, no network):
python3 -m unittest discover -s tests
```

The candor dial makes the core risk visible immediately: a **guarded** persona
yields ~0 Tier-2+ disclosures, **open** yields the full set — the candor capture
ratio with a known denominator.

### Use a live model

```bash
pip install -e '.[live]'
export ANTHROPIC_API_KEY=sk-...
export ONTORA_MODEL=claude-opus-4-8      # optional; defaults to a current Claude
python3 -m ai_engine.cli --simulated     # interviewer AND persona now use the model
```

The LLM sits behind a port (`ai_engine/llm/`); switching providers is an
infrastructure-only change. No domain/application code names a model or SDK.
