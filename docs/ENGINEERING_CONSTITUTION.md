# The Ontora Engineering Constitution

*The permanent law governing how Ontora is built, extended, refactored, reviewed,
and removed. Not an architecture document, not a spec, not a plan — the small set
of rules that keep the system coherent when the team is larger than any one person
can supervise.*

---

## Preamble

Ontora builds a system that claims to know things about real organizations and
real people. That claim is the whole product, and it is fragile: a fluent system
that is confidently wrong is worse than no system at all. Our engineering choices
are therefore not matters of taste — they are the difference between a trustworthy
instrument and an expensive confabulation engine.

This constitution exists because, past a certain size, **team behavior governs
outcomes more than code quality does.** Individual brilliance cannot hold a system
coherent; shared law can. These rules are deliberately few and deliberately
strict. They are written to *reduce future arguments* — when two engineers
disagree, the constitution should already contain the answer. Where it does not,
the disagreement becomes an ADR, not a Slack thread.

The constitution is strict about a small number of things that are existential
(truth, provenance, boundaries, the AI/domain line, deletion) and silent about the
many things that are merely preferences. Strictness where it matters buys freedom
everywhere else.

---

## The Founding Canons

Fourteen principles from which every article is derived. If an article ever
contradicts a canon, the canon wins and the article is amended.

- **C1 — Evidence-first.** Nothing enters Ontora's model of the world without
  evidence attached at creation. No evidence, no existence.
- **C2 — Truth is not confidence.** What is true and how sure we are are two
  different things, separately represented. We never collapse them.
- **C3 — AI proposes, the domain validates.** Cognition may *suggest*; only the
  domain may *commit*. The model's output is a proposal until a domain rule or a
  human accepts it.
- **C4 — Human authority is final.** The consultant, not the model, holds
  truth-authority. The system is an instrument for judgment, never a replacement.
- **C5 — No truth without provenance.** Every asserted fact resolves, transitively,
  to an immutable source segment. An orphan claim is a bug.
- **C6 — No cross-context reach-in.** Bounded contexts communicate only through
  published language. Reaching into another context's internals is forbidden.
- **C7 — No silent data fusion.** Testimony, interpretation, validation, and
  outcome are distinct layers, never merged except by an explicit, recorded act.
- **C8 — No hidden eval leakage.** What grades us never touches what trains or
  builds us. The holdout is sacred.
- **C9 — Deletion is a feature.** The ability to remove a subsystem is designed in
  from the start, not discovered during a crisis.
- **C10 — Cognition and storage are strangers.** The AI engine never knows how, or
  whether, anything is persisted. It receives inputs and returns proposals.
- **C11 — Product before platform.** We earn generality by observing repeated need.
  We do not presume it. A framework precedes its second real user by zero days.
- **C12 — Learning requires validated outcomes.** We update our beliefs and our
  models only from what a human or reality confirmed — never from raw model output.
- **C13 — Elegant abstractions are suspects.** Beauty is not evidence of
  correctness. An abstraction must earn its place with call sites, not aesthetics.
- **C14 — Major subsystems remain removable.** Drift, the official-org model, the
  graph, the epistemology — each must be deletable without collapsing the rest.

---

# TITLE I — THE DOMAIN (truth and structure)

## Article I — Domain Modeling
- **Rule.** The domain models organizational *truth and its provenance*, nothing
  else. Aggregates enforce their own invariants; no invariant lives in a service
  that an aggregate could enforce itself.
- **Why.** The domain is the one place where correctness is guaranteed rather than
  hoped for. If invariants leak into services, correctness becomes optional.
- **Forbids.** Anemic aggregates; invariants enforced only in application code;
  domain types that carry transport, persistence, or UI concerns.
- **Enables.** Confidence that a constructed domain object is *always* valid,
  everywhere it appears.
- **Enforcement.** CI `tsc` on `packages/contracts` and each context; factory/
  constructor guards for every invariant (e.g. evidence invariants N1–N5, E1);
  CODEOWNERS per context; review question R1.
- **Prevents.** The "valid here, invalid there" bug where an object is well-formed
  in one path and corrupt in another.

## Article II — Evidence & Provenance *(C1, C5)*
- **Rule.** Every node, edge, observation, finding, and recommendation carries ≥1
  `Evidence` at the moment of creation. Inferred evidence resolves deterministically
  to immutable transcript segments via `EvidenceRef` + `Derivation`.
- **Why.** Ontora's product *is* traceable truth. An unsourced accusation is both a
  correctness failure and a legal liability (F5).
- **Forbids.** Creating any truth-bearing object without evidence; mutating a source
  segment an `EvidenceRef` points to; evidence that dead-ends in another inference
  with no immutable root.
- **Enables.** "Show me why you believe this" as a first-class, always-available
  operation. Defensibility in front of a skeptical executive or a lawyer.
- **Enforcement.** Domain factories reject evidence-less construction; transcript
  segments are append-only after finalization; a provenance-resolution test proves
  every `EvidenceRef` terminates at an immutable segment.
- **Prevents.** Confabulation laundered into "findings" (F4).

## Article III — Confidence & Uncertainty *(C2)*
- **Rule.** Truth-value and confidence are separate fields with separate lifecycles.
  Confidence is explicit, calibrated against the evaluation harness, and never
  inferred from fluency or verbosity.
- **Why.** Conflating the two is how a system becomes confidently wrong. Calibration
  is a moat precondition (see moat analysis); miscalibration is fatal (F11).
- **Forbids.** Boolean "known/unknown" where a graded belief is required; deriving
  confidence from text length, model self-report, or how convincing an output reads.
- **Enables.** Decision-sufficiency reasoning — acting when confidence is *enough*
  for the decision at hand, not when the prose sounds sure.
- **Enforcement.** Confidence values must trace to an eval-backed calibration source;
  reviewers reject any confidence that originates in model narration.
- **Prevents.** The demo that dazzles and the deployment that misleads (the
  demo–production inversion).

## Article IV — Boundaries & Imports *(C6)*
- **Rule.** A context may import from another context *only* through its
  `published-language` entrypoint, and from the shared kernel (`@oi/contracts`).
  Nothing else. Deep imports are prohibited.
- **Why.** Every reach-in is a coupling that makes future deletion (C14) and
  refactoring (Article XIII) impossible.
- **Forbids.** `import` paths into another context's `domain/aggregates`, `services`,
  or internal files; cyclic context dependencies; the shared kernel importing from
  any context.
- **Enables.** Contexts that can be reasoned about, tested, and deleted in isolation.
- **Enforcement.** tsconfig path aliases expose only published language;
  eslint/dependency-cruiser boundary rules fail CI on any other cross-context path;
  the shared kernel has zero context dependencies by construction.
- **Prevents.** The slow slide from modular monolith to distributed mud.

## Article V — Application Orchestration *(C3)*
- **Rule.** The application layer *wires*; it does not *decide*. It coordinates
  contexts, ports, transactions, and idempotency. Business truth lives in the
  domain; cognition lives behind the AI ACL.
- **Why.** When orchestration starts deciding truth, the invariants (Article I) are
  bypassed and the domain becomes decorative.
- **Forbids.** Domain rules re-implemented in handlers; handlers that persist AI
  output directly; orchestration that reads another context's private state.
- **Enables.** Thin, testable use cases; a domain that remains the sole authority
  on correctness.
- **Enforcement.** Use cases depend only on ports and published language; the
  AI ACL (`AiEnginePort`, task ports) returns DTO proposals a domain factory must
  accept before anything is committed; review question R3.
- **Prevents.** Logic sprawl where the same rule exists in three handlers and drifts.

---

# TITLE II — COGNITION (the AI)

## Article VI — AI Boundary Design *(C3, C10)*
- **Rule.** The AI engine is a stateless proposer reached only through an
  anti-corruption layer. It receives inputs and returns typed DTO *proposals*. It
  never persists, never reads the database, never learns of storage.
- **Why.** Cognition changes weekly; the system of record must not. Coupling them
  makes both unmaintainable and lets ungoverned output become fact.
- **Forbids.** The `ai-engine` importing domain repositories; AI output written to
  storage without passing a domain validation port; prompts embedded in domain code.
- **Enables.** Swapping models, providers, or prompts with zero domain change; a
  clean seam to test cognition and storage independently.
- **Enforcement.** `ai-engine` has no dependency on `core-api` persistence; the
  contract between them is `packages/contracts` DTOs only; a proposal is inert until
  a domain factory accepts it.
- **Prevents.** The day a model change silently corrupts the system of record.

## Article VII — Prompt Design
- **Rule.** Prompts are versioned, single-purpose, and specify objective, inputs,
  reasoning behavior, output schema, what to avoid, and uncertainty/contradiction
  handling. No "be helpful" prompts. Every prompt has a matching eval.
- **Why.** A prompt is production logic with no type system; the only discipline
  available is explicitness, versioning, and measurement.
- **Forbids.** Vague instructions; prompts that request truth without demanding
  evidence; unversioned prompt edits; prompts without an eval that guards them.
- **Enables.** Reasoning about behavior changes; rolling back a regression to a known
  prompt version.
- **Enforcement.** Prompts live in versioned files, not inline strings; a prompt
  change without a corresponding eval change is rejected in review (R6).
- **Prevents.** Silent behavioral drift no one can reproduce or roll back.

## Article VIII — Evaluation Design *(C8)*
- **Rule.** The evaluation harness is the system's conscience and is treated as
  production. It gates over averages, rewards value density over verbosity, measures
  calibration and confabulation, and its holdout is sealed. What grades never trains.
- **Why.** The eval is the only technical moat and the precondition for safe
  automation (see moat analysis §9). An eval that leaks is worse than none — it
  certifies overfitting as skill.
- **Forbids.** Training, prompt-tuning, or few-shot selection on holdout data;
  metrics that reward length or generic summaries; shipping a capability whose eval
  does not exist yet; "the demo looked good" as evidence.
- **Enables.** Provable claims ("this is calibrated," "this beats the baseline") and
  the ability to answer "why not the 6-week copycat?"
- **Enforcement.** Holdout stored with a hashed manifest; access to it is logged and
  outside the training/tuning path; CI blocks a capability PR that ships no eval;
  gates are pass/fail, not averaged.
- **Prevents.** The benchmark that rewards confident nonsense (F20).

## Article IX — Dataset Design *(C7, C12)*
- **Rule.** The learning dataset keeps four layers permanently distinct —
  **testimony, interpretation, validation, outcome** — event-sourced and never
  fused. We learn only from validated outcomes, never from raw model output.
- **Why.** Fusing the layers destroys the ability to know *what was said* vs *what we
  inferred* vs *what was confirmed*. It is the difference between a compounding asset
  and a stale, non-transferable liability pile (moat analysis §10).
- **Forbids.** A record that mixes testimony and interpretation; training on
  unvalidated inferences; treating a model proposal as ground truth; deleting a
  belief instead of decaying it.
- **Enables.** A meta-layer (elicitation skill, calibration, validated-finding
  patterns) that actually transfers across engagements.
- **Enforcement.** Schema-level separation of the four layers; ingestion refuses
  cross-layer writes; the learning pipeline reads only from the validation/outcome
  layers; belief decay is modeled, not deletion.
- **Prevents.** A learning loop that quietly teaches itself its own hallucinations
  (F18).

---

# TITLE III — TRUST (the subject and the human)

## Article X — Privacy & Identity *(C7)*
- **Rule.** Employee testimony is pseudonymized at ingest, firewalled from the
  employer, and released only above a k-anonymity threshold. Raw sensitive
  disclosure never reaches management. Identity resolution is explicit, probabilistic,
  and reversible.
- **Why.** The neutral-third-party trust posture is Ontora's only structural moat and
  the precondition for candor (F1, F3). One leak is not a bug — it is the company.
- **Forbids.** Joining raw testimony to identity outside the sanctioned resolution
  seam; surfacing sub-threshold aggregates; attributing Tier 3–4 content to a named
  person to the employer; implicit identity fusion.
- **Enables.** The confidentiality guarantee that makes candor possible at all.
- **Enforcement.** Pseudonymization in the ingestion boundary; k-anonymity checks
  before any employer-facing release; identity resolution isolated to one auditable
  component; access logging on raw testimony.
- **Prevents.** The re-identification event that ends the company (F3/F5).

## Article XI — Consultant Workflow & Human Authority *(C4)*
- **Rule.** The consultant is the final authority on truth. The system proposes
  findings with evidence and confidence; a human validates, overrides, or rejects.
  Validation is a first-class, recorded domain event, not a UI checkbox.
- **Why.** Automated authority over organizational truth is legally and
  epistemically indefensible (F6 rubber-stamping, F7 distrust). Human judgment is
  the actual seat of authority (moat analysis §5).
- **Forbids.** Auto-committing model conclusions as validated truth; validation
  flows so frictionless they invite rubber-stamping; hiding the evidence a human is
  asked to validate against.
- **Enables.** Defensible output ("a named consultant stands behind this") and the
  validated-outcome signal the learning loop requires (C12).
- **Enforcement.** Validation emits a domain event carrying validator identity and
  the evidence reviewed; the UI presents evidence *before* accepting a judgment;
  unvalidated findings are visibly distinct from validated ones.
- **Prevents.** The consultant reduced to a stamp, and the false confidence that
  follows (F6).

---

# TITLE IV — THE CRAFT (how we build)

## Article XII — Test Strategy
- **Rule.** Test the invariant, not the incident. Domain invariants get exhaustive
  unit tests; context boundaries get contract tests; cognition gets evals (Article
  VIII), not brittle output assertions. Coverage of *guarantees* matters, not the
  percentage.
- **Why.** Tests exist to protect the properties the system promises; testing
  implementation details freezes the wrong things and rots on the first refactor.
- **Forbids.** Snapshot tests of AI prose as correctness gates; tests that assert
  private structure across a boundary; coverage-number theater.
- **Enables.** Fearless refactoring (Article XIII) because the guarantees are pinned.
- **Enforcement.** Invariant tests co-located with aggregates; contract tests at
  published-language seams; AI behavior guarded by evals; review question R8.
- **Prevents.** A test suite that is green, brittle, and meaningless at once.

## Article XIII — Refactoring Policy *(C13)*
- **Rule.** Refactor toward *fewer concepts and clearer boundaries*, never toward
  cleverness. A refactor that adds an abstraction must remove more complexity than it
  adds and must not weaken a boundary or a deletion path.
- **Why.** Most architectural decay arrives disguised as improvement — an elegant
  generalization that couples two things that should have stayed apart.
- **Forbids.** Abstraction introduced for fewer than three real call sites (C13);
  refactors that merge bounded contexts for convenience; "DRY" that fuses two
  concepts that merely look alike (semantic duplication is not physical duplication).
- **Enables.** A codebase that gets simpler under maintenance, not more ornate.
- **Enforcement.** Boundary rules (Article IV) still pass post-refactor; reviewer
  applies the "what did this delete?" test; ADR required if a boundary moves.
- **Prevents.** The beautiful abstraction that no one can later remove.

## Article XIV — Dependency Policy *(C14)*
- **Rule.** Every dependency — library or subsystem — is a liability until proven
  otherwise. Core domain and shared kernel stay dependency-light. Major subsystems
  sit behind ports so they remain removable.
- **Why.** Dependencies are how deletion (C9, C14) and portability quietly die.
- **Forbids.** Pulling a heavy framework into the domain; depending on a subsystem's
  internals instead of its port; adding a dependency without justifying its removal
  cost.
- **Enables.** Deleting Drift, the org model, or a provider without a rewrite.
- **Enforcement.** Shared kernel has zero runtime framework deps; subsystem access
  goes through ports; new dependencies require a one-line justification in the PR.
- **Prevents.** The transitive dependency web that makes "just remove it" impossible.

## Article XV — Naming Policy
- **Rule.** One concept, one name, one home. Names come from the domain and the
  ubiquitous language, not from implementation. If two things share a name, they are
  the same concept; if they are different, they get different names.
- **Why.** Naming is category discipline. Semantic duplication (Article XIII) begins
  as a naming accident.
- **Forbids.** The same term meaning two things across contexts; technical names
  (`Manager`, `Helper`, `Data`) for domain concepts; a concept defined in two places.
- **Enables.** A shared mental model where "Evidence" or "Finding" means exactly one
  thing everywhere.
- **Enforcement.** Shared kernel owns cross-cutting vocabulary; reviewers reject
  synonyms and homonyms (R5); glossary lives with the domain model.
- **Prevents.** Category confusion — the quiet killer of large domains.

## Article XVI — Logging & Observability
- **Rule.** Behavior is observable or it does not ship. Every AI proposal,
  validation, confidence assignment, and provenance resolution is traceable. Logs of
  sensitive testimony obey Article X. No hidden behavior.
- **Why.** A system that claims truth must be auditable; "why did it conclude this?"
  must always be answerable after the fact, not just in the moment.
- **Forbids.** Silent fallbacks; swallowed errors; AI decisions with no trace; logging
  raw sensitive testimony in violation of the privacy firewall.
- **Enables.** Post-hoc audit, incident diagnosis, and the evidence chain regulators
  and executives will demand.
- **Enforcement.** Structured, correlated traces across the AI seam; privacy-aware log
  redaction; alerting on confidence/confabulation anomalies.
- **Prevents.** The un-diagnosable "it just said that" incident.

## Article XVII — ADR Policy
- **Rule.** Decisions that change a boundary, an invariant, the AI/domain line, the
  privacy model, or a canon are recorded as ADRs *before* merge. ADRs are immutable
  once accepted; they are superseded, never edited. Reversible, local decisions do
  not need one.
- **Why.** Institutional memory is how a growing team avoids re-litigating settled
  questions and avoids silently reversing them.
- **Forbids.** Changing a ratified decision (ADR 0000–0008 and successors) in code
  without a superseding ADR; ADRs for trivia; editing accepted ADRs.
- **Enables.** A durable record of *why*, so newcomers inherit reasoning, not just
  outcomes.
- **Enforcement.** A boundary/invariant-touching PR without a linked ADR is blocked;
  ADRs are append-only and numbered.
- **Prevents.** Architecture drift by a thousand un-recorded reversals.

---

# TITLE V — EVOLUTION (how we change and remove)

## Article XVIII — Feature Deletion *(C9, C14)*
- **Rule.** Deletion is a designed capability. Every major subsystem ships with a
  documented deletion path and sits behind a seam. Removing a feature is a normal,
  celebrated act — not a defeat.
- **Why.** The adversarial reviews concluded that much of what is built (Drift, the
  official-org model, identity resolution, the epistemology build) is deletable if
  the core bets fail. A system that cannot shed weight cannot survive being wrong.
- **Forbids.** Subsystems with no removal path; features kept alive out of sunk cost;
  coupling that makes deletion a rewrite.
- **Enables.** Responding to a failed experiment (candor, usefulness) by *removing*
  the speculative half, cheaply.
- **Enforcement.** Each major subsystem's README states its deletion path and blast
  radius; boundary and port rules keep that path real; periodic "what could we
  delete?" review.
- **Prevents.** The bloated system that outlived its assumptions and can't be cut down.

## Article XIX — Experimentation *(C11)*
- **Rule.** Risky bets are validated by the cheapest experiment that can *kill* them,
  pre-registered, before they are built into the system. Product need is demonstrated
  before platform generality is built. We build to answer a question, then decide.
- **Why.** The company's fate rests on a few cheap, untested behavioral bets (candor,
  usefulness). Building ahead of evidence is the most expensive mistake available
  (F15 build-not-sell).
- **Forbids.** Generalizing before a second real user exists (C11); building a
  subsystem whose core assumption is untested; experiments that can only conclude
  "promising."
- **Enables.** Learning which subsystems deserve to exist before paying to maintain
  them.
- **Enforcement.** A new major subsystem cites the validated question it answers; the
  30-day experiment pattern (pre-registered, GO/PIVOT/KILL) precedes speculative
  build-out.
- **Prevents.** An elegant platform for a product no one validated.

## Article XX — Long-Term Maintainability *(C10, C11, C13)*
- **Rule.** Optimize for the engineer who arrives in two years and must change one
  thing safely. Prefer boring, local, deletable, well-named code over clever, global,
  entangled, impressive code. Cognition stays swappable; storage stays hidden; the
  domain stays authoritative.
- **Why.** The codebase will outlive every current assumption about the product. The
  maintainer's ability to change it safely is the real asset.
- **Forbids.** Premature optimization; global cleverness; performance work without a
  measured problem; abstractions that serve the author's taste over the maintainer's
  comprehension.
- **Enables.** A system that survives model churn, team churn, and pivots.
- **Enforcement.** Reviewers optimize for legibility and locality; performance changes
  require a benchmark; the canons are re-read, not assumed.
- **Prevents.** The two-year-old codebase no one dares to touch.

---

## Constitutional Violations

A change is *unconstitutional* — and must be blocked regardless of how good it looks
— if it does any of the following:

1. Creates a truth-bearing object without evidence *(C1, Art. II)*.
2. Asserts a fact that does not resolve to an immutable source *(C5, Art. II)*.
3. Collapses truth and confidence into one value *(C2, Art. III)*.
4. Imports across a context boundary except through published language *(C6, Art. IV)*.
5. Persists AI output without domain validation *(C3, Art. V/VI)*.
6. Gives the AI engine knowledge of storage or a database dependency *(C10, Art. VI)*.
7. Ships a capability with no eval, or tunes on the sealed holdout *(C8, Art. VIII)*.
8. Fuses two dataset layers, or trains on unvalidated output *(C7, C12, Art. IX)*.
9. Joins raw testimony to identity outside the sanctioned seam, or releases a
   sub-threshold aggregate to the employer *(Art. X)*.
10. Auto-commits a model conclusion as validated truth *(C4, Art. XI)*.
11. Introduces an abstraction for fewer than three real call sites, or merges two
    concepts that merely look alike *(C13, Art. XIII/XV)*.
12. Leaves a major subsystem with no documented deletion path *(C9, C14, Art. XVIII)*.
13. Moves a boundary, invariant, or canon without a superseding ADR *(Art. XVII)*.
14. Builds a subsystem whose core assumption has not been validated *(C11, Art. XIX)*.
15. Introduces hidden behavior — a silent fallback, a swallowed error, an untraceable
    AI decision *(Art. XVI)*.

## Review Questions (ask before approving any PR)

- **R1 — Invariants:** Are all new invariants enforced *inside* the aggregate, so the
  object cannot exist in an invalid state?
- **R2 — Evidence:** Does every new truth-bearing object carry evidence that resolves
  to an immutable source?
- **R3 — AI line:** Does any AI output reach storage without passing a domain
  validation port?
- **R4 — Boundaries:** Does every cross-context import go through published language
  only? Any new cycle?
- **R5 — Naming:** One concept, one name, one home? Any synonym or homonym introduced?
- **R6 — Prompts/Eval:** Does every prompt change come with an eval change? Any holdout
  contamination?
- **R7 — Dataset:** Are the four layers still separate? Are we learning only from
  validated outcomes?
- **R8 — Tests:** Do the tests pin *guarantees*, or do they freeze implementation
  detail?
- **R9 — Deletion:** Could this subsystem still be deleted after this change? Is the
  path documented?
- **R10 — Simplicity:** What did this change *remove*? Does the abstraction earn its
  call sites?
- **R11 — ADR:** Does this touch a boundary, invariant, privacy model, or canon? If so,
  is there an ADR?
- **R12 — Privacy:** Could this expose identity or sub-threshold testimony to the
  employer?

## Decisions Intentionally Left Open (future ADRs)

The constitution deliberately does *not* settle these; they are ratified per-context
via ADR when real need arrives, so we do not over-constrain before we know:

1. When (if ever) a context becomes a separately deployed service rather than a module.
2. The concrete belief-representation formalism (point vs credal/imprecise) per use.
3. Whether the org graph is persisted as a native graph store or projected from events.
4. The identity-resolution algorithm and its human-review threshold.
5. Cross-client prior-sharing policy — what, if anything, transfers between engagements.
6. Retention and right-to-erasure mechanics for pseudonymized testimony.
7. The exact GO/PIVOT/KILL thresholds per experiment (owned by each experiment's
   pre-registration, not the constitution).
8. Whether cognition is single-provider or multi-provider, and the failover model.
9. The point at which the eval harness itself gets versioned as a released artifact.
10. When Drift / the official-org model graduate from "removable experiment" to
    "load-bearing subsystem" — or are deleted.

---

## Engineering Ethos

We are building an instrument that people will trust with the truth about their
organizations and, sometimes, about each other. That trust is the entire company,
and it is earned in the parts of the work no demo ever shows: the evidence that
resolves to a real sentence someone actually said, the confidence number that was
calibrated instead of asserted, the boundary that let us delete a failed idea
cleanly, the eval that told us we were wrong before a customer did. We are
skeptical of our own cleverness and ruthless about our own sunk costs. We let the
AI propose and never let it decide; we let the human decide and always show them
why. We keep our concepts few, our boundaries hard, our subsystems removable, and
our claims provable. We would rather ship something modest that we can stand
behind than something impressive that we cannot. This constitution is not here to
make us feel disciplined — it is here so that, when we are tired, rushed, and
sure we know better, the system still tells the truth.
