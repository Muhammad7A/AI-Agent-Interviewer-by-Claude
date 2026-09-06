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
export GROUNDWORK_MODEL=claude-sonnet-5      # optional; this is also the default
python3 -m ai_engine.cli --simulated     # interviewer AND persona now use the model
```

The LLM sits behind a port (`ai_engine/llm/`); switching providers is an
infrastructure-only change. No domain/application code names a model or SDK.

### The employee interview surface (a separate app, on purpose)

Until this existed, the interview ran *inside the consultant workspace* — which means
the consultant was present. That destroys the candour the whole product depends on
measuring (F1): the experiment design requires the employee **alone** with the tool,
employer-blinded.

```bash
python3 -m ai_engine.webapp     # consultant workspace, port 8000
python3 -m ai_engine.employee   # interview surface,   port 8100
```

It is a **different ASGI application**, not extra routes on the workspace. That is the
whole point: there is no path from here to a transcript list, a review queue, a report,
or anyone else's interview, because those routes *do not exist in this app*. A boundary
enforced by absence cannot be defeated by a misconfigured guard. Verified live:

```
/              -> HTTP 404      /invitations   -> HTTP 404
/engagement    -> HTTP 404      /transcripts   -> HTTP 404
```

**The participant is never asked who they are.** The consultant creates an invitation,
and the pseudonym is assigned *there*; the interview surface has **zero input fields**
besides the answer box (asserted by a test). Identity enters the system once, on the
consultant's side, and is never collected from the person whose candour depends on its
absence. Access is an unguessable `secrets.token_urlsafe` token — not an interview id,
which would let one link enumerate other people's interviews.

**The confidentiality statement is the first thing shown**, because in the candor
experiment it *is* the treatment being measured. Every promise it makes is one the code
enforces — pseudonymisation, aggregate-only employer release, k-anonymity, and discard
on withdrawal:

> - Your name is not attached to your answers.
> - Your employer does not see your answers — they receive a summary across everyone
>   interviewed, with no names and no quotes.
> - A topic is only reported if several people raise it.
> - You can stop at any time, and what you have said is discarded.

That last one is real, not a form of words. In-flight interviews are held **in memory
only** — an interview that was never submitted has not been consented to, so it is never
written to disk. Losing it on restart is the correct failure mode. A test withdraws
mid-interview and then greps the entire data directory to prove the words are nowhere.

Unknown, completed and withdrawn tokens all return the **same** page, so a probe cannot
learn which tokens exist by comparing responses.

### Derived-result cache (what makes the app usable live)

Measuring the aggregation cost turned up something worse than the cost itself:
**nothing was cached**. The consultant workspace recomputed the entire pipeline on
every page view — the same stored interviews produced the same model calls on a
refresh, and an engagement report re-ran every pairwise relation call each time it was
opened. Measured, three stored interviews produced three model calls per dashboard
render, identically on the second render. With a live model that is minutes of latency
and repeated spend *per click*, not per engagement.

The cache boundary is **temperature**, which is a principled line rather than a
convenient one:

- At `temperature = 0` the provider is asked for its single best answer, so calling
  twice with identical input requests the same thing twice. Reusing it changes cost and
  latency, not behaviour. Tagging, entailment and relation classification all run at 0.
- Above 0 the caller is deliberately sampling. The interview loop runs at 0.4 because
  an interviewer that asks every participant the same scripted question is not an
  interviewer. Caching there would replace variation with repetition — a behaviour
  change disguised as an optimisation — so it is refused.

Measured effect on repeated renders:

| | dashboard | engagement |
|---|---|---|
| 1st render | 3 calls | 0 |
| 2nd render | **0** | 0 |
| 3rd render | **0** | 0 |

Two properties make this correct rather than merely fast. **Transcripts are immutable
and finalized**, so a derived result is a pure function of its inputs and can never go
stale against a transcript that changed underneath it — none ever does. And **keys
carry the prompt version and the model**, so editing a prompt invalidates its own
entries instead of silently serving the previous behaviour, and one model never serves
another's answers.

The cache is encrypted at rest with the same cipher as everything else, because cached
extraction output contains verbatim claim statements — an unencrypted cache would
quietly reintroduce the plaintext leak the event logs just had. Failures are never
cached, so a transient outage cannot become a permanently empty answer, and a corrupt
entry is treated as a miss: the cache is an optimisation and must never be able to
break the pipeline. Set `GROUNDWORK_CACHE=0` to measure what an uncached run really costs.

### The consultant workspace (web app)

The MVP loop as a local web app — **consultant-only**, on purpose. The employer never
gets a login; they receive a generated, firewalled document. That keeps the privacy
boundary a property of the architecture rather than a permissions checkbox a future
feature can tick.

```bash
pip install -e '.[web]'
python3 -m ai_engine.webapp          # http://127.0.0.1:8000
```

Interview → review evidence → validate → report. Notable properties:

- **Pseudonymised at ingest.** You type a real name to start an interview; it is
  converted immediately and appears nowhere afterwards — the page shows `P-5a3e43`.
- **Evidence renders before the controls.** The quote sits above the accept/reject
  buttons in the markup, because a verdict recorded without reviewing the evidence is
  a rubber stamp (F6), and the gate stores the evidence you reviewed with the decision.
- **The gate is the engine's, not the UI's.** Rejecting without a reason is refused
  because `ValidationGate` refuses it, not because a form validates.
- **Verdicts survive restarts**, which required making claim identity
  content-addressed (`claim_id_for`): with random ids, re-tagging a transcript in a
  new process minted new ids and silently orphaned every recorded judgement.
- **Testimony is escaped, never interpolated raw** — transcript text is untrusted
  input, and this is a tool for handling sensitive material.
- **No authentication, deliberately**, and stated in the startup banner: a localhost
  single-consultant tool for the Year-0/1 experiments. Auth arrives with the second
  user (Art. XIX). Binding to a non-loopback host prints a warning.
- The turn loop is **not duplicated**: `InterviewDriver` defines a turn once and both
  the batch CLI and the request-per-turn web app drive it.

The firewall demonstrably works in both directions. With **one** interviewee the
employer receives *nothing* — all topics withheld, because one person's findings
cannot be anonymous. With **three**, the same engagement releases group-level findings:

```
- **Interviews:** 3        - **Topics released:** 5

### workaround: keep, report, unusable, weekly, because
_workaround · 3 participants · confidence 0.87_
- 3 participants raised this. Individual responses are withheld.
  - _withheld: individual responses, attribution, verbatim quotes, per-participant confidence_
```

Zero real names, zero verbatim quotes — asserted by a test that scans the employer
page for every 5-word phrase from every stored utterance.

### Durable evidence + the production posture (prerequisites for any app)

Two gaps that a CLI tolerates and a deployed app cannot.

**1. Evidence used to die at process exit.** The architecture claims every finding
resolves to an immutable source, but the transcript lived only in memory and the
event log recorded `chars=len(answer)` — never the words. So after the process
exited, every `EvidenceRef` in every report pointed at a segment that no longer
existed: quotes couldn't be re-verified, the safety gates couldn't be re-run, and a
consultant couldn't answer *"show me why you believe this"* the next day. An
evidence-first system with no durable evidence.

`persistence/transcript_store.py` stores transcripts write-once (a finalized
transcript is immutable, so overwriting is refused) and rehydrates them exactly —
ids, order, and text byte-for-byte, because offsets are character positions and a
single normalisation would silently shift every quote. The invariant its tests
assert directly:

> a rehydrated transcript resolves every `EvidenceRef` to exactly the same text.

Demonstrated end-to-end: one process runs the interview and stores it; a **fresh
process** loads it, re-runs both safety gates on the stored testimony, and resolves
evidence to the original span.

**2. The silent mock was a production liability.** With no API key every component
fell back to *scripted* behaviour — a misconfigured deployment would have served
fabricated interviews to real employees and logged them as genuine testimony. Add a
storage key that isn't set and verbatim attributable testimony lands on disk in
plaintext. Both are right for local work and unacceptable in production:

```bash
GROUNDWORK_ENV=production python3 -m ai_engine.cli     # refuses, listing every problem
```
```
ConfigurationError: GROUNDWORK_ENV=production, but this configuration is not safe to
serve real interviews:
  - no ANTHROPIC_API_KEY: cognition would silently fall back to the scripted mock
    interviewer, serving fabricated interviews to real people and recording them
    as genuine testimony
  - no GROUNDWORK_STORE_KEY: verbatim, attributable employee testimony would be
    written to disk in plaintext
```

Every run now prints its posture — `env=dev cognition=MOCK storage-at-rest=PLAINTEXT`
— so nobody has to infer it.

**On encryption:** no cipher is hand-rolled here. `persistence/crypto.py` defines a
port and adapts `cryptography`'s Fernet (authenticated, so tampering is detected)
via the `secure` extra; `NullCipher` is plaintext, reports
`protects_at_rest = False`, and production refuses it. A *configured* key that cannot
actually encrypt raises rather than silently downgrading — an installed-but-broken
crypto library is the dangerous case, since it reads as "available" right up to the
first write.

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
layer is never fused with testimony (C7).

**Two verification gates, not one.** Grounding proves the quote is *real*; a second
**entailment** gate (`ai_engine/evidence/entailment.py`) proves the quote actually
*supports* the claim. This closes a real hole: a model can quote a genuine sentence
and staple a fabricated claim to it ("uses ChatGPT" → "leaked customer data") — the
quote grounds perfectly, but entailment rejects the over-reach. The confabulation
rate now counts both kinds of fabrication (unsourced quotes **and** unsupported
claims). Offline uses a conservative heuristic that catches escalation into
accusations; with a live model, a strict natural-language-entailment check drops in
through the same seam. Tagging runs automatically after each
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

### The privacy firewall (Constitution Article X, in code)

Article X mandated pseudonymization at ingest, an employer firewall, and
k-anonymity. Until this was built, the implementation was **zero** — it existed only
in the docs, while the org report printed *"**Dana:** we follow the process"* beside
*"**Eli:** nobody follows it"*, attributing a Tier-3 dissent to a named employee.
That is the anonymity paradox (F3) shipping as a feature, and it attacks the only
structural moat the analysis identified: being the party an employee can safely tell
the truth to.

`ai_engine/privacy/` implements one distinction the system previously did not make —
**two audiences with different rights**:

```bash
python3 -m ai_engine.aggregation --audience employer --k 3   # redacted (default)
python3 -m ai_engine.aggregation --audience consultant       # inside the firewall
```

| | consultant (inside) | employer (outside) |
|---|---|---|
| identity | pseudonym + separately-held key | never |
| verbatim quotes | yes | never |
| per-participant detail | yes | never — **aggregate only** |
| disagreement | positions shown | *that* it exists, never the sides |
| sub-k topics | shown | withheld, with a logged reason |

**Pseudonymization at ingest** (HMAC-SHA256 per engagement) means every downstream
artifact — logs, aggregation, confidence, reports — carries only a pseudonym.
Pseudonyms are stable within an engagement (corroboration still works), **not
linkable across engagements** (two clients' data cannot be joined), and not
reversible without the key, which is written to its own `*.RESTRICTED.*` file and
gitignored.

#### Three leaks implementing this exposed

Writing the gate found problems that documenting it never would:

1. **The topic label was one participant's verbatim sentence** (the aggregation
   labels a topic with its longest member statement). Employer labels are now built
   only from vocabulary **two or more** participants share — by construction not
   unique to anyone.
2. **Stripping only the `quote` field was a fake redaction**, because the synthesised
   `statement` carries the same words. Hence *aggregate-only*: per-member content is
   per-person disclosure however it is packaged.
3. **Side sizes identify a lone dissenter** even with names removed — "3 say X, 1
   says Y" is the leak. Contested topics now report only that a disagreement exists.

The ungated `render_org_report` was **deleted** rather than left in place: an
ungated renderer is a loaded gun, and the invariant is that nothing reaches an
employer except through `release()`. Two hard invariants are asserted over a whole
generated org — **no real name** and **no verbatim 5-word phrase** anywhere in an
employer release — because redaction that removes only names is not redaction.

### Multi-interview aggregation (from interview tool to organizational intelligence)

One interview is a data point; an organization is the pattern across many. The
aggregation module (`ai_engine/aggregation/`) fuses the findings of many interviews
of the *same* org:

- Findings are **clustered into topics** by shared vocabulary (one issue seen
  through multiple lenses — a "friction" finding and a "bottleneck" finding about
  the same approval step land in one topic).
- Where independent people say the same thing → **corroboration** (raises
  confidence, shown with each person's own provenance).
- Where they disagree → a **contradiction**, typed as conflict / variation /
  complementarity (research program Q7/Q8). A conflict is a *signal to
  investigate*, surfaced — not averaged away.

Crucially, aggregation **never invents a fact** — it only relates findings that
each already carry their own evidence, and every statement still resolves to its
own interview's transcript. The relation check is a port: a conservative offline
heuristic (opposing polarity on a shared topic = conflict), or a live-model NLI
classifier through the same seam.

```bash
python3 -m ai_engine.aggregation           # runs a 3-person demo org, offline
python3 -m ai_engine.aggregation --write   # also writes org_report.md
```

The demo org is built so its interviews **corroborate** on one thing (a director's
approval bottleneck, all three) and **conflict** on another (does anyone follow the
official process? — one says yes, one says no). In production you aggregate
*validated* findings; the demo aggregates tagged proposals for a runnable example.

### Confidence + calibration (a number that had to earn the right to exist)

Confidence was deliberately absent until aggregation existed, because a confidence
score derived from nothing is the exact failure the eval harness is meant to catch.
Now there are **real structural signals**, so `ai_engine/confidence/` derives one —
and then *measures whether it means anything*.

Confidence accumulates in **log-odds space** from observable signals only:

| signal | why it's legitimate |
|---|---|
| independent corroboration | people who *agree with this specific finding* (diminishing returns) |
| direct contradiction | if two people flatly disagree, at most one is right — and the lone dissenter is penalised more than the majority side |
| disclosure tier | costly, self-implicating admissions are rarely invented by the subject |
| evidence match exactness | interpretive distance from the immutable source is a small risk signal |

It is **never** derived from fluency, verbosity, or the model's own narration
(Constitution Art. III), and every score decomposes into named contributions, so
"why 0.89?" always has an answer:

```
confidence 0.89 (high)
  +0.20  prior: passed grounding + entailment (p=0.55)
  +1.43  corroboration: 3 independent participant(s) assert this (Ben, Cleo agree)
  +0.35  disclosure_tier: tier 3 (costly to disclose)
  +0.10  evidence_match: quote matched source: exact
```

**Then it gets graded.** The calibration study interviews a study org that contains
*deliberately mistaken beliefs* — so there are real false findings to catch — and
measures **AUC** (does confidence rank truth above falsehood?), **Brier**, and
**ECE** with reliability bins.

```bash
python3 -m ai_engine.confidence           # the calibration study
python3 -m ai_engine.confidence --write   # also writes calibration_study.md
```

Current offline result: **AUC 1.00** — all three false findings score below all
fifteen true ones, with the lone dissenter's mistaken belief lowest at 0.20.

**The honest caveat, stated in the report itself:** the share of false findings in
the study org is a *design choice*, so **ECE is not a verdict** on the scorer — it
reflects an invented base rate. AUC is base-rate independent and therefore the
meaningful offline number. The weights are deliberately **not** tuned to minimise
mock ECE, because that would be fitting to a fiction; real calibration needs real
outcomes (research program Q4).

### Safety-gate fuzz audit (property-based adversarial testing)

The product's credibility rests on two gates — **grounding** (is the quote real?) and
**entailment** (does the quote support the claim?) — and each can fail in two
opposite directions with very different costs:

- **False accept** — a fabrication is admitted. The dangerous direction (F4/F5).
- **False reject** — a true quote is refused. Silently destroys recall and would
  make the eval report a worse system than we have.

Example-based tests only check the cases an author thought of. `ai_engine/fuzz/`
generates thousands of **near-misses** and asserts properties over all of them:

```bash
python3 -m ai_engine.fuzz                       # audit; exit 0 only if clean
python3 -m ai_engine.fuzz --cases 1500 --seed 4 --verbose
```

The rigour comes from knowing the expected answer *independently of the code under
test*: a **cosmetic** mutation (curly quotes, dashes, case, whitespace, trailing
punctuation) keeps the words, so it MUST still ground; a **semantic** mutation
(substitute, delete, insert, negate, swap, renumber) changes them, so it MUST NOT.
Semantic cases are gated by a word-level precondition and *skipped* rather than
asserted if a mutation coincidentally still appears in the source. Properties
checked: cosmetic accept, semantic reject, interviewer-quote reject, **evidence
offset integrity** (do the char offsets point at the words actually matched?),
entailment accept-faithful, entailment reject-escalation (every severe/legal stem),
and never-crash on hostile input (empty, unicode, 5 KB, injection-looking strings).

A **meta-test** replaces grounding with a gate that accepts everything and asserts
the audit catches it — otherwise a green audit would mean nothing.

#### What the audit found

A real bug in the shipped grounding filter, on seed 4 of a deep sweep:

> The fabricated quote **`"vendor I"`** was **accepted** against the real text
> *"…that vendor **i**gnores each deadline"* — the flexible matcher had no
> word-boundary anchors, so it could match **half a word**, producing evidence that
> pointed at a fragment of a different word.

Every match path is now word-boundary guarded (applied only on sides where the
needle itself starts/ends with a word character, so punctuation-led quotes like
`"— pretty standard"` are not over-constrained). Verified across **12 seeds and
~60,000 property checks**, with the specific case pinned as a regression test. The
audit also caught one bug in *its own oracle* first — a character-level integrity
comparison that wrongly flagged 142 correct whitespace-tolerant matches — a reminder
that the oracle needs as much care as the code.

### Synthetic organization generator (the testbed)

Hand-written personas prove a pipeline *runs*; they cannot make an evaluation
statistically meaningful. Six people is an anecdote, and a fixture hand-tuned until
it passes measures the fixture. `ai_engine/synthetic/` generates organizations to
order, with ground truth known by construction and full reproducibility from a seed:

```bash
python3 -m ai_engine.synthetic --size 20 --seed 3 --verbose   # inspect an org
python3 -m ai_engine.confidence --generate 24 --seed 5        # study one
```

Controllable: **size**, **candor mix** (guarded employees withhold their Tier 2+
beliefs, so this directly gates how much truth is reachable), **corroboration
depth**, **contradiction rate**, **bias rate**, and two adversarial dials described
below.

Generated text has to survive four real downstream mechanisms, so the topic
templates are engineered to satisfy them *systematically* rather than by hand-tuning:
elicitation (keywords hit the interviewer's question ladder), clustering (a shared
core guarantees vocabulary overlap), agreement detection, and contradiction
detection. **Tests assert this vocabulary contract** — including that no two
distinct topics accidentally merge, and that every planted contradiction is actually
*detected*. Both classes of bug are silent: they would leave the benchmark reporting
a number while measuring nothing.

#### What the testbed found

Building it immediately produced two results that hand-written fixtures could not:

1. **A real bug in the generator.** All "unfounded attribution" beliefs initially
   shared one template, so independent bias-holders clustered and *corroborated each
   other* — manufacturing **0.92 confidence on false findings**. Bias is now
   single-source by construction (distinct targets), guarded by a test.
2. **A real limitation of the confidence scorer**, now reproducible on demand:

| regime | AUC |
|---|---|
| majority is right (`minority_correct_rate=0`) | **0.73** — works |
| majority is wrong (`minority_correct_rate=1`) | **0.17** — *inverted* |

Corroboration-weighted confidence is only valid while **errors are independent**.
Where a wrong majority outvotes a correct minority, or a shared misconception
corroborates itself (`correlated_bias_rate`), the signal **reverses** — the scorer
becomes confidently wrong. Both regimes are pinned by tests so neither can regress,
and the study report prints a loud warning whenever AUC falls below chance. This is a
documented limitation, not a defect: a testbed that can only flatter the scorer is
not a testbed.

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
