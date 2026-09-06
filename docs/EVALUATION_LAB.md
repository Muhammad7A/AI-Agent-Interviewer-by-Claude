# Evaluation Lab

The lab turns the repository from an application that calls a language model
into a **measurable AI system**: every important AI behavior has a scenario, a
rubric, a score, a stored result, and a regression tripwire.

```
 dataset (golden.json, versioned)
        │  load_dataset — refuses malformed records, no silent drops
        ▼
 runner (ai_engine/lab/runner.py)
   turn   : prefix + candidate answer → REAL driver (resume replay) → produced turn
   gate   : claim + quote → grounding + entailment → verdict vs expected
   report : interviews → gates → validation ledger → rendered deliverable
   full   : whole conversation vs a persona → coverage + disclosures
        │  rubrics.py — every criterion declares its grader class:
        ▼
 TurnEvaluation (score + per-criterion evidence + latency + output hash)
        │  schemas.LAB_SCHEMA JSON
        ▼
 results file  ──compare──►  committed baseline (baselines/golden-baseline.json)
                                    │
                                    ▼
                       RegressionReport → exit 1 on drift
```

## The anti-fake-confidence rule

Every rubric criterion declares which class of evidence backs it, and the
report shows that class next to every score:

| Class | Meaning | Examples in this lab |
|---|---|---|
| `deterministic` | Computed from the system's own inspectable structures. Same input, same verdict, forever. | strategy intent matches the state's demand; state transitions; question-bank area mapping; report provenance; repeat-identity |
| `heuristic` | A computed approximation a human could disagree with. Labeled as signal, never as truth. | communication hygiene bands (length, leak patterns); live-mode vocabulary-overlap relevance fallback |
| `model` | Requires a live provider. **Reported UNSCORED without one — the lab never invents this score.** | `communication/naturalness` (declared, on by default only when a provider is configured) |

## Dataset schema (`groundwork.lab.dataset/v1`)

```json
{
  "schema": "groundwork.lab.dataset/v1",
  "version": "golden-v1",
  "scenarios": [{
    "id": "golden-guarded-deferral",
    "title": "Refusal: back off, never twice running",
    "kind": "golden | standard | edge | adversarial",
    "dimension": "reasoning",
    "unit": "turn | gate | report | full",
    "prefix": [{"role": "interviewer|subject", "text": "..."}],
    "pending_question": "the question awaiting the candidate answer",
    "candidate_answer": "the participant reply under evaluation",
    "criteria": [{"rubric_id": "reasoning/intent",
                  "params": {"expected_intent": "de_escalate"}}],
    "tags": ["candor", "strategy"],
    "persona": {…},         // `full` scenarios only
    "gate": {"claim": "…", "quote": "…", "expect": "supported|rejected"}  // `gate` only
  }]
}
```

Malformed records, unknown kinds, unknown fields, and duplicate ids are
**refused at load** — a silently-dropped scenario is a hole in the measurement.

## Rubric schema (`lab.rubric/v1`)

| id | dimension | class | what it grades |
|---|---|---|---|
| `relevance/area` | relevance | deterministic (mock) / heuristic (live) | produced turn addresses the current target area |
| `correctness/state` | correctness | deterministic | recorded state matches the scenario's demanded transitions (`areas_touched`, `tier_credited`, `pending_area`, `areas_covered_min`) |
| `reasoning/intent` | reasoning | deterministic | strategy intent matches the state's demand (`open`, `de_escalate`, `specificity_conversion`, `contradiction`, `ladder`, `close`) |
| `communication/hygiene` | communication | heuristic | non-empty, 10–2000 chars, no leaked internals (`should_close`, `assessment`, raw JSON), not a verbatim echo of the answer |
| `consistency/repeat` | consistency | deterministic | N repeats produce identical output (hash-compared) |
| `interview_quality/coverage` | interview_quality | deterministic | full conversation elicits `min_covered` areas and `min_disclosures` tier-2+ disclosures |
| `feedback_quality/provenance` | feedback_quality | deterministic | report carries `min_evidence_lines`, omits `forbidden_statements`, keeps firewall framing |
| `communication/naturalness` | communication | **model** | model-judged naturalness — UNSCORED without a live provider |

## Regression workflow

```bash
# After an intentional behavior change, re-baseline:
python -m ai_engine.lab --save-baseline baselines/golden-baseline.json

# CI (runs on every push): compare, exit 1 on drift
python -m ai_engine.lab --baseline baselines/golden-baseline.json --check
```

A regression is: a total-score drop beyond `--tolerance`; a criterion that
passed in the baseline failing now; variance appearing where the baseline was
deterministic; an engine failure where the baseline succeeded. **Latency is
reported, never failed** — hardware noise is not behavior.

## Repeatability

`--repeats N` runs every scenario N times and reports, per scenario: distinct
output hashes (deterministic engine → exactly 1), score min–max, failure
count, latency mean ± stddev. In mock mode the variance must be zero — any
drift is a nondeterminism finding. With a live provider the same table becomes
the model's variance profile.

## Golden suite

`ai_engine/lab/data/golden.json` (13 scenarios) curates the behaviors whose
regression would break the product's promises: opening safety, refusal
back-off, specificity conversion, contradiction surfacing, tier crediting,
resume equivalence, injection-as-refusal, both evidence gates, the employer
firewall, report provenance, full-coverage elicitation, and repeat
consistency. The suite must pass 1.0 in mock mode; `tests/test_lab.py` fails
otherwise.
