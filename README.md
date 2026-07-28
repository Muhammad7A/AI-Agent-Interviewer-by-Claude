# Ontora

**Organizational intelligence from employee interviews, where every finding
resolves to a verbatim quote — or it doesn't ship.**

[![CI](https://github.com/Muhammad7A/AI-Agent-Interviewer-by-Claude/actions/workflows/ci.yml/badge.svg)](https://github.com/Muhammad7A/AI-Agent-Interviewer-by-Claude/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

Ontora conducts AI-driven interviews with employees, extracts what they
actually said about how work gets done, and produces a consultant-facing
report in which **every claim carries a quote that provably exists in the
transcript**. Claims that fail that test are dropped, not softened.

It is built for the discovery phase of AI-transformation consulting, where the
expensive, unscalable step is interviewing forty people to find out what is
really going on.

---

## Try it in 30 seconds

The engine has **zero third-party dependencies**. If you have Python 3.10+ you
can run the entire pipeline right now — no install, no API key, no network.

```bash
git clone https://github.com/Muhammad7A/AI-Agent-Interviewer-by-Claude.git
cd AI-Agent-Interviewer-by-Claude/apps/ai-engine
python3 -m ai_engine.cli --simulated --candor open
```

That runs a full interview against a scripted persona and prints the report.
Real output, abridged:

```markdown
## Workarounds & Shadow Tooling

### I keep my own private spreadsheet because the official dashboard is
    unusable, and I rebuild the weekly report by hand — about four hours
    every week.
_Tier 2 · amended_

> "I keep my own private spreadsheet because the official dashboard is
>  unusable, and I rebuild the weekly report by hand — about four hours
>  every week."
> — evidence `seg-9f5fcc9a6f99` [0:148] (exact)

## Summary
- Validated findings: 5
- Proposals rejected in validation: 0
- Interview coverage: 1/6 areas reached Tier 2+
```

Now run the same command against a guarded interviewee:

```bash
python3 -m ai_engine.cli --simulated --candor guarded
```

```
Turns: 14   Areas covered (Tier 2+): 0/6   Tier-2+ disclosures: 0
PROPOSED FINDINGS — 0 verified, 0 unsourced, 0 unsupported, confabulation rate 0%
```

**Zero findings, and that is the correct answer.** A guarded participant said
nothing substantive, so the system reports nothing. Most tools would have
produced a confident summary anyway. The gap between those two runs is the
problem this project exists to work on.

---

## The core idea: two independent gates

An LLM asked to summarize an interview will produce fluent, plausible,
partially invented findings. Fluency is not evidence. So no claim reaches a
report without passing two checks that fail for different reasons:

**Gate 1 — Grounding: does this quote actually exist?**
The quoted span is located in the immutable transcript by exact match, after
length-preserving Unicode normalization, with word-boundary guards. If the
model paraphrased, drifted a word, or invented the quote outright, the claim is
rejected. Not flagged — rejected.

**Gate 2 — Entailment: does the quote actually support the claim?**
A real quote can be attached to a claim it does not support. Gate 1 cannot
catch that, because the quote is genuine. Gate 2 checks the inferential step
from quote to claim and rejects the ones that don't hold.

Both gates are audited by a property-based fuzzer
(`python3 -m ai_engine.fuzz`) that mutates claims and transcripts adversarially
and fails the build on any false accept. It has caught real bugs in this
codebase, including a word-boundary error where `"vendor I"` matched inside
`"vendor ignores"`.

Findings are ranked on a **Tier 0–4 truth taxonomy**. Tier 0–1 is what anyone
would say in a town hall. The value is in Tier 2–4: the workaround, the
unsanctioned tool, the thing about a manager. A pipeline that produces only
Tier 0–1 has run successfully and learned nothing.

---

## The pipeline

```
  interview loop        a strategy engine picks each next question from
        │               coverage, candor signal, and information gain
        ▼
  immutable transcript  content-addressed; spans are permanent addresses
        │
        ▼
  evidence tagging      the model proposes claims, each with a quote span
        │
        ├─► GATE 1  grounding    does the quote exist verbatim?  ─► reject
        ├─► GATE 2  entailment   does it support the claim?      ─► reject
        │
        ▼
  human validation      a consultant accepts, amends, or rejects
        │
        ▼
  privacy firewall      pseudonymization, k-anonymity, aggregate-only release
        │
        ▼
  report                every finding carries its quote and its evidence ID
```

Across interviews, the aggregation layer clusters corroborating claims, detects
contradictions between participants, and scores confidence — which is then
checked for **calibration**, not only discrimination. A system that says "90%
confident" needs to be right about 90% of the time.

---

## Repository layout

```
apps/ai-engine/       Python. The part that runs today.
  ai_engine/
    interview/        the loop, the strategy engine, session state
    transcript/       immutable transcripts and evidence references
    evidence/         claim extraction and the two gates
    validation/       the human review step
    aggregation/      cross-interview clustering, contradiction detection
    confidence/       confidence scoring and calibration studies
    privacy/          pseudonymization, release policy, k-anonymity
    persistence/      encrypted event log, transcript + derived-result stores
    llm/              provider port, retries, deterministic-call cache
    webapp/           consultant workspace (FastAPI)
    employee/         employee-facing interview surface (FastAPI)
    eval/             the evaluation gate CI runs on every push
    fuzz/             adversarial audit of the two gates
    synthetic/        generates fake orgs with known ground truth
  tests/              273 tests, runnable with nothing installed

apps/core-api/        TypeScript / NestJS. Architecture skeleton — see Status.
packages/contracts/   Shared contract types between the two runtimes.
docs/                 Design, research, and strategy documents.
```

---

## Running everything else

All dependency-free:

```bash
cd apps/ai-engine
python3 -m unittest discover -s tests   # the full test suite
python3 -m ai_engine.eval               # evaluation gate — CI fails if this fails
python3 -m ai_engine.fuzz               # adversarial audit of both gates
python3 -m ai_engine.synthetic          # generate an org with known ground truth
python3 -m ai_engine.aggregation        # cross-interview aggregation
python3 -m ai_engine.confidence         # confidence + calibration study
```

The two web apps need extras:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[web]'
python3 -m ai_engine.webapp     # consultant workspace  → http://127.0.0.1:8000
python3 -m ai_engine.employee   # employee surface      → http://127.0.0.1:8100
```

### Configuration

| Variable | Unset | Set |
|---|---|---|
| `ANTHROPIC_API_KEY` | **mock mode** — scripted interviewer | live model |
| `ONTORA_STORE_KEY` | testimony stored **in plaintext** | encrypted at rest |
| `ONTORA_ENV` | `dev` — mocks and plaintext allowed | `production` — **refuses to start** without both of the above |
| `ONTORA_MODEL` | `claude-opus-4-8` | your choice |
| `ONTORA_DATA_DIR` | `data/interviews` | storage location |

Install the matching extras with `pip install -e '.[live,secure,web]'`.

`ONTORA_ENV=production` crashes at startup if either key is missing. That is
deliberate: a silent mock is indistinguishable from a working system until
somebody reads a transcript that nobody ever said.

---

## Privacy

This system records people saying things that could cost them their standing at
work. That shapes the architecture, not just the documentation:

- Participants are **pseudonymized at ingest** (HMAC-SHA256). The mapping back
  to real identities is a separate secret that never travels with deliverables.
- Testimony is **encrypted at rest** when a storage key is configured, including
  the event log.
- Nothing reaches an employer except through `privacy.release()`, which enforces
  **k-anonymity** and **aggregate-only** disclosure. Stripping the quote while
  keeping the claim is not redaction — the claim carries the same words — so
  release is aggregate-only by construction.
- `.gitignore` excludes `data/`, `*.testimony.jsonl`, and `identity-key*`, so
  testimony and re-identification keys cannot be committed by accident.

Three real leaks were found and fixed while building this, including a topic
label that was one participant's verbatim sentence, and side-counts that would
have identified a lone dissenter.

---

## Status — honestly

**`apps/ai-engine` is real and runs.** Full pipeline, 273 passing tests, an
evaluation gate and a fuzz audit enforced in CI on every push.

**`apps/core-api` (TypeScript / NestJS) is an architecture skeleton.** Bounded
contexts, domain types, and boundary rules are ratified; the business logic is
not implemented. Don't expect it to run.

**The system has never been run against a live model in production**, and has
never interviewed a real employee. The central empirical claim — that an AI
interviewer elicits more candid disclosure than a human consultant does — is
**untested**. [`docs/CANDOR_EXPERIMENT_DESIGN.md`](docs/CANDOR_EXPERIMENT_DESIGN.md)
describes the experiment that would test it. Until that runs, the thesis is a
hypothesis.

---

## Documentation

| Document | What it covers |
|---|---|
| [`ENGINEERING_CONSTITUTION.md`](docs/ENGINEERING_CONSTITUTION.md) | The rules this codebase is not allowed to break |
| [`CODE_WALKTHROUGH.md`](docs/CODE_WALKTHROUGH.md) | Every module, for a reader new to the codebase |
| [`REPO_MAP.md`](docs/REPO_MAP.md) | File-by-file index |
| [`RESEARCH_PROGRAM.md`](docs/RESEARCH_PROGRAM.md) | Falsifiable questions, and which are untestable today |
| [`CANDOR_EXPERIMENT_DESIGN.md`](docs/CANDOR_EXPERIMENT_DESIGN.md) | The experiment that would validate the core thesis |
| [`MOAT_ANALYSIS.md`](docs/MOAT_ANALYSIS.md) | Competitive analysis, written to be unflattering |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design and bounded contexts |
| [`EVALUATION_HARNESS.md`](docs/EVALUATION_HARNESS.md) | What the gates measure, and why |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: the test suite must
pass with **zero** third-party packages installed, and the evaluation gate and
fuzz audit must stay green. Both are enforced in CI.

For anything touching privacy or evidence integrity, read
[SECURITY.md](SECURITY.md) first — please don't open a public issue for those.

## License

[Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for a note on the duty of
care that comes with software that records people's testimony about their own
workplaces.
