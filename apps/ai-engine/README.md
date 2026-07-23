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

### Evidence tagging (interview → grounded findings)

After the interview, the loop tags the transcript into **evidence-bound claim
proposals** (`ai_engine/evidence/`). Each proposed claim must quote the subject
verbatim; a deterministic grounding verifier then *locates* that quote in the
immutable transcript and turns it into a resolvable `EvidenceRef`. If the quote
isn't found — a hallucinated or paraphrased "quote" — the claim is **rejected**,
not shown. This is the confabulation filter (F4): it reports a
`confabulation_rate = ungrounded / total` and never trusts the model's honesty.

Claims are always `status = proposed` (AI proposes, the domain/consultant
validates — C3), carry no confidence score yet (truth ≠ confidence — C2), and are
logged to a **separate** `*.interpretation.jsonl` file so the interpretation
layer is never fused with testimony (C7). Tagging runs automatically after each
interview; pass `--no-tag` to skip it. With `ANTHROPIC_API_KEY` set, extraction
uses the model; offline it uses a deterministic keyword tagger whose claims
ground by construction.

### Validation gate (AI proposes → human validates)

Proposed claims become truth only when a human accepts them (`ai_engine/validation/`,
C3/C4). Each decision — **accept / reject / amend** — is a recorded event carrying
the validator's identity and the evidence they reviewed; you cannot decide without
referencing the evidence, and reject/amend require a reason (friction against
rubber-stamping, F6). Decisions land in a **separate** `*.validation.jsonl` file —
the fourth dataset layer, never fused with the others — and each record is the
supervised label the learning loop compounds on (research program Q6). Pass
`--validate` to review by hand; otherwise an **auto-sim reviewer** decides (clearly
flagged `auto-sim` so demo labels are excluded from real learning).

### Report (the deliverable)

Validated findings render to a Markdown report (`ai_engine/report/`) grouped by
finding type. Only accepted/amended findings appear — rejected and unvalidated
proposals are excluded — and every finding carries a verbatim evidence quote that
resolves to the immutable transcript (no finding without provenance, C1/C5). A
simulated-validation report is stamped **DEMO ONLY** so it can't be mistaken for a
real deliverable. Written to `<data_dir>/<id>.report.md`.

### The full pipeline

```
interview  →  transcript  →  evidence tags  →  validation  →  report
(testimony)   (immutable)    (interpretation)   (validation)   (deliverable)
```

One command runs all four stages and writes each dataset layer to its own file:

```bash
python3 -m ai_engine.cli --simulated --candor open      # auto-sim validation
python3 -m ai_engine.cli --validate                     # you interview AND validate
```

### Evaluation harness (the system's conscience)

The only technical moat is knowing whether the output is *true*, not just fluent
(Art. VIII, moat analysis §9). Because the simulated personas hold a fixed set of
tier-tagged latent truths, the harness has **known ground truth** and scores the
pipeline in two layers that fail independently:

- **Elicitation** — did the interview get the truth *out* into the transcript?
  (recall vs the candor-achievable set)
- **Synthesis** — did tagging turn transcript truth into correct, grounded claims?
  (precision, confabulation, value density)

It uses **gates, not averages**: *safety* gates (no confabulation, no over-claim,
no candor leak) must pass on every case; *capability* gates (recovery ≥ 50%, value
density ≥ 50%) are judged at the candor ceiling (open). Calibration is deliberately
**not** scored — no confidence signal exists yet (C2), and faking one is the exact
failure the harness exists to catch.

```bash
python3 -m ai_engine.eval           # deterministic, offline; exit 0 = all gates pass
python3 -m ai_engine.eval --write   # also write eval_report.md
```

The headline output is the **candor curve** — elicitation recall rising as the
persona's candor rises — which is the candor experiment run as a measurement. Exit
code is 0 iff all gates pass, so the harness doubles as a CI gate. With
`ANTHROPIC_API_KEY` set, the interviewer, subject, and tagger all use the live
model — the first *real* measurement of the system.
