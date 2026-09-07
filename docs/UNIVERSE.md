# Interview Simulation Universe

A composable scenario framework: **9 domains × 4 levels × 5 interview kinds**
(180 scenario families, 360 archetype/candor variants) composed from dimension
tables — not thousands of hardcoded prompts. Every composed scenario runs
through the real engine offline and is measurable by the evaluation lab.

## Composition model

```
domain  → vocabulary (nouns)          software_engineering: "the ingest pipeline", "10x load"
level   → a BAR, not content          senior: depth 3, breadth 3, signal floor 3, 12 turns
kind    → sentence shapes             debugging tier 2: "What would you rule out first…?"
competency → the content ladder       se_tradeoffs tier 3: "the shapes you picked"
archetype → truth mix (signals/red flags)     strong | mixed | weak
candor  → reachability (the cap)      guarded 1 · neutral 3 · open 4
```

`compose(domain, level, kind, …)` resolves these into a seed-deterministic
`ScenarioSpec` (difficulty is computed from declared inputs, never authored).
`render(spec)` materializes it into engine-shaped objects — a `Persona` whose
truths pair with the rendered question bank, the bank itself, the opening, the
specificity probes, per-area strategy parameters — **loudly refusing** (F1–F7
lint) anything that would half-work: duplicate texts, questions resume cannot
attribute, red flags the candor cap makes unreachable.

## Follow-up logic

Follow-ups are data, not prompts: kind defaults (vague → convert, guarded →
back off) are the strategy's existing intents; scenario rules compile to the
same moves. A red flag never auto-fails a candidate — it triggers an evidence
probe, and the probe's outcome (evidence present, or vague-strikeout) is the
hiring signal.

## Fairness

* Difficulty is a computed function of declared inputs — auditable, not authored.
* Identity/demographic stems are prohibited from every table and checked
  against produced utterances (`hiring/prohibited-topics`, fail-closed).
* A red flag never auto-fails anyone; markers against *real* humans are
  heuristic-class (capped), and high-stakes decisions require the model grader
  plus human review.
* Level bars normalize scoring: a junior is never compared to expert ceilings.

## Usage

```python
from ai_engine.universe import compose, render

spec = compose("software_engineering", "senior", "system_design")
scenario = render(spec)
# → scenario.persona, scenario.bank, scenario.opening, scenario.probes …
```

Seed scenarios: every `(domain, level, kind)` cell composes today — verified by
`tests/test_universe.py`'s grid execution through the real engine. Adding a
10th domain = one vocabulary table + 3–5 competency rows; zero code.

## Known gaps (documented, by design)

* Strategy memory is process-local: "never de-escalate twice" can be disturbed
  by a restart (persist strategy hints in draft schema v2).
* At the expert bar with a capped-candor candidate, the ladder may re-ask a
  tier text (the candidate cannot reach the required depth; the interview
  honestly keeps trying, then closes).
* Marker matching against real (non-scripted) humans is heuristic-class.
