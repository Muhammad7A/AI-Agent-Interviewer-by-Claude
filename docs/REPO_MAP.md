# Repo Map — what is live, what is design, what can be deleted

This repository contains two models of the same domain, at very different maturities.
Anyone opening it deserves to know which is which in the first ten seconds, because
the larger of the two by file count has never executed.

---

## The short version

| | path | status | lines | runs? |
|---|---|---|---|---|
| **The working product** | `apps/ai-engine/ai_engine/` | **live** | ~10,900 | yes — 360 tests, 8 CLIs, CI |
| Ratified design (shared kernel) | `packages/contracts/src/` | contracts only | ~1,000 | no — `tsc` only |
| Ratified design (platform) | `apps/core-api/src/` | contracts only | ~4,700 | no — `tsc` only |
| Reserved skeleton | `apps/ai-engine/src/` | empty placeholders | 0 | no |
| Web app | `apps/web/src/` | empty placeholder | 0 | no |
| Strategy & design docs | `docs/` | ~25 documents | — | n/a |

**If you are looking for code that does something, it is `apps/ai-engine/ai_engine/`.**
Start with [`CODE_WALKTHROUGH.md`](./CODE_WALKTHROUGH.md).

---

## Why two models exist

The TypeScript tree is the **ratified architecture** (ADRs 0001–0008): bounded
contexts, aggregates, invariants, published language. The five-year roadmap needs it
in Year 1–2, when persistence, multi-tenancy, and enterprise readiness become real
work. It was designed first, deliberately, and then the product was built as a thin
Python slice so the Year-0/1 experiments could run against real people.

Nothing is wrong with that sequence. What *was* wrong is that the two models were
kept in step **by hand, in comments** — and drifted. The Python `EvidenceRef` had
dropped `transcriptId`, so a reference could not resolve itself; after
multi-interview aggregation it could be resolved against the wrong person's
transcript and yield someone else's words as evidence. A comment cannot catch that.

## How the two are held together now

`apps/ai-engine/tests/test_contract_conformance.py` parses the TypeScript interfaces
and compares them to the Python dataclasses, failing the build on any **undeclared**
divergence in either direction:

- a Python field unknown to the contract means the runtime invented a concept;
- a required contract field absent from Python must be a **recorded** omission with a
  stated reason.

The thin slice is allowed to implement less than the ratified design — transcript
versioning, `CharSpan` as a value object, the `anchorType` discriminant, and audio
timecodes are all deliberately deferred. The point is that each is *declared*, and a
stale declaration (something now implemented, or no longer in the contract) also
fails.

## Deletion paths (Constitution Art. XVIII)

Every major subsystem must be removable. Concretely:

- **`apps/core-api/src/`** — nothing in `ai_engine` imports it. `git rm -r` removes it
  without touching the working product; the conformance test's `CORE_API` cases would
  need removing too. Keep while the Year 1–2 platform work is still planned; delete if
  the roadmap's Year-3 fork concludes the platform is not needed.
- **`packages/contracts/src/`** — same: no runtime dependency from `ai_engine`. Removing
  it drops the conformance gate, so the Python model would become the sole source of
  truth (which is a decision, not an accident).
- **`apps/ai-engine/src/`, `apps/web/src/`** — empty `.gitkeep` placeholders. Deletable
  at any time with zero consequence.
- Within the live product, the removable subsystems are `aggregation/`, `confidence/`,
  `synthetic/`, and `fuzz/`: each is additive, and the single-interview pipeline
  (`interview → transcript → evidence → validation → report`) runs without them.

## What is genuinely load-bearing

Only these, in the live product:

```
interview/    the questioning loop
transcript/   the immutable record — every other module depends on it
evidence/     grounding + entailment: the two safety gates
validation/   human authority over truth
privacy/      the firewall; nothing reaches an employer except through release()
report/       the deliverable
```

Everything else — aggregation, confidence, the testbed, the fuzzer, and the entire
TypeScript tree — is either additive or aspirational, and is documented above as
such rather than presented as infrastructure.
