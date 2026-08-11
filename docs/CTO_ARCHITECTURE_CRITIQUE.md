# CTO Critique — First Principles

> **Author:** Founding CTO, accountable for the first production release.
> **Purpose:** challenge the architecture from first principles before customers
> do. This is not a design doc and not a defense of prior work. It is a list of
> where I think we are wrong.

---

## 0. The core indictment

**We spent a cathedral's worth of effort modeling the *aftermath* of a capability
we have never proven we possess.**

We have six bounded contexts, ~300 contract files, an evidence-provenance spine, a
drift-detection engine, and a probabilistic identity-resolution layer — and **zero
evidence that we can extract one useful, reliable insight from one real employee
interview.** We modeled the *output* of the product (organizational knowledge,
drift, recommendations) in exhaustive detail and the *input* of the product (a
good AI interview) almost not at all. That is the priority inversion that should
scare us most. Everything downstream is conditioned on an unvalidated assumption.

If I ranked our effort against our risk, they are nearly inverted. The riskiest,
least-understood parts of this business — *can we run a good interview, will
employees be honest, is the extraction accurate, will consultants actually use
it* — received the least modeling. The most speculative, most mature-product parts
— drift, provenance chains, six-factor confidence — received the most.

---

## 1. Assumptions that could be wrong (ranked by how fatal)

1. **That the AI interview produces reliable structured knowledge.** The entire
   stack sits on this. It is the least-built and least-validated part of the
   system. If interviews yield shallow or generic transcripts, "evidence-first"
   just faithfully preserves noise. **This is the whole ballgame and we treated it
   as "the ingestion layer."**
2. **That employees will be honest with an AI their employer bought.** People
   don't tell the truth about bottlenecks, blockers, or bad managers — especially
   to a recorded tool. Fear, politics, and performance will dominate. No amount of
   graph rigor fixes a candor problem, and we have modeled nothing to earn candor
   (anonymity guarantees, consent, "who sees this").
3. **That customers have official structure to compare against.** The Organization
   context assumes `OfficialProcess`, `OfficialWorkflow`, `OfficialApprovalChain`,
   `OfficialPolicy` — richly declared, versioned intent. **Most mid-market
   companies have none of this in structured form.** Their "process" is tribal
   knowledge and a stale Confluence page. If the official side is empty, the entire
   Drift context computes against null.
4. **That consultants want AI proposals to validate.** "AI proposes, human
   disposes" assumes validation is cheap. Consultants are the most expensive input
   in the business. If the tool hands them 200 proposed pain points to confirm one
   by one, it *adds* work and they abandon it. The validation workflow may be
   net-negative on the exact users we need.
5. **That organizations share one ontology.** `Workflow / Activity / Handoff /
   System / Artifact` as universal node types is a bet that a hospital, a law firm,
   a SaaS startup, and a factory decompose the same way. They don't. We committed
   to a universal schema before seeing three real orgs.
6. **That drilling to evidence is a purchase driver.** We built provenance so a
   boardroom insight resolves to a transcript sentence. Elegant — but customers may
   just want "your top 5 bottlenecks," and the provenance machinery is trust
   infrastructure for a trust objection nobody has raised yet.

---

## 2. What will not survive contact with real customers

- **The official Organization model.** Customers won't populate it. It will
  collapse to "import whatever messy directory export they can give us," and the
  rich `Official*` catalog will be mostly empty fields.
- **Drift as a first-class product.** It needs two clean sides. Customers will have
  one messy side. Drift becomes a "nice v3 feature," not a launch context.
- **Per-item validation.** Consultants will demand batch review, sampling, or
  "just show me what's high-confidence." The `ValidationRecord`-per-artifact model
  will be redesigned around their time, not our correctness.
- **The universal node ontology.** It will fracture into per-industry templates or
  a looser, more emergent/tag-based structure. The rigid typed graph will bend.
- **The six-factor confidence model.** Customers and consultants will collapse it
  to "high / medium / low." Nobody will ask for `sourceAuthority` vs
  `inferenceDepth` decomposition in year one.

---

## 3. Over-engineered abstractions (speculative surface we built anyway)

| Abstraction | Why it's speculative |
|---|---|
| **Entire Drift/Assessment context (44 files)** | Solves a comparison problem that requires data customers don't have, built before Knowledge extraction was proven. |
| **Identity resolution** (`MappingHypothesis`, `IdentityResolution`, `ReconciliationCandidate`) | Probabilistic interviewee↔employee matching — only matters if we have clean employee data *and* drift is the value prop. Two unproven ifs. |
| **Six-factor `ConfidenceFactors`** | Explainability nobody requested; one score would ship v1. |
| **Transcript versioning + `SegmentCorrection` + additive supersession** | Built append-only re-versioning before a single transcript exists. When does a transcript get re-versioned in practice? Unknown. |
| **`Official*` governance catalog** | Assumes declared, versioned processes/policies most customers can't provide. |
| **Synthesis layer** (`DiagnosticCluster`, `RecommendationBundle`, `RootCauseHypothesis`, `RecommendationConflict`) | Sophisticated aggregation over recommendations we've never generated. |
| **`MaturityScore` / `ReadinessScore`** | Invented scores with no methodology and no customer asking for them. |
| **Corrections/versioning across three contexts** | Three separate versioning mechanisms, zero versioned data. |

None of this is *wrong* engineering. It's the *wrong time*. It's answering
questions no customer has asked.

---

## 4. Missing abstractions (the things that actually decide the outcome)

- **The interview engine.** Adaptivity, follow-up logic, when to probe, when to
  stop — the actual IP — is a skeleton folder. We modeled the transcript we get
  *after* a great interview, not how to run one.
- **Employee trust: consent, anonymity, and visibility.** For honest data we need
  guarantees about who sees what. We have a pseudonymized `IntervieweeRef` and
  nothing else. This is existential for data quality **and** legally required (EU
  works councils, GDPR). Its absence is the most dangerous gap in the model.
- **The learning loop.** How consultant validations improve extraction/detection
  over time. Deferred — but it's how the product compounds. Without it we're a
  static template, not an intelligence platform.
- **Unit economics.** Every interview + extraction burns real tokens. There is no
  cost attribution, quota, or margin model. `Administration` is a stub. At scale
  this decides whether the business works.
- **Data ingestion / onboarding.** How the customer's org data arrives. The
  Organization model assumes data materializes.
- **Language and culture.** Global orgs interview in many languages; nothing
  models it.

We built the parts that are intellectually satisfying and skipped the parts that
are commercially decisive.

---

## 5. Bounded contexts: collapses and splits I expect

**Likely to collapse together:**
- **Insights + Drift → "Analysis."** Drift is a *category* of insight
  (misalignment is a bottleneck). We stood up two contexts with parallel
  confidence/validation/scoring/event machinery. That's premature separation; the
  duplication cost is real and the boundary is thin.
- **Knowledge + Insights.** They already share the graph substrate, and
  `Observation→Finding→PainPoint` mirrors `Claim→Node`. Two pipelines, much
  parallel machinery. The seam may not earn its keep.
- **Transcript + Interview Orchestration.** Once interviews exist, "conduct" and
  "store" may be one context.

**Likely to split further:**
- **Knowledge** into ingestion (extraction/resolution) vs. graph-of-record vs.
  query/lens — they have different change rates and scaling.
- **The AI engine** per capability — interview cognition, extraction, and detection
  have different models, latencies, and cost profiles; one runtime won't hold.
- **Organization** into "directory" (messy HR import) vs. "governance catalog"
  (the aspirational `Official*` model most won't use).

The lesson: **we drew context boundaries from a whiteboard, not from observed rates
of change.** Some are too fine (Insights/Drift), some too coarse (Knowledge), and
we won't know which until real usage tells us. Boundaries drawn this early are
guesses dressed as decisions.

---

## 6. Hypothetical vs observed problems

**Solving hypothetical problems:** drift, identity resolution, six-factor
confidence, transcript versioning, official governance, maturity/readiness scores,
cross-engagement history, anchor-protection recompute. Every one is a *scale* or
*maturity* concern for a product with many happy customers.

**Observed problems we have NOT solved** (because we can't, without customers):
can we elicit useful truth in an interview; will employees engage; is extraction
accurate enough to trust; will a consultant find the output worth their time; can
we make money per engagement. These are the only problems that matter for release
one, and the architecture barely touches them.

---

## 7. Decisions that DO maximize long-term leverage (credit where due)

I'm not torching everything. These are genuinely good bets and I'd keep them:

- **Contracts-first, fully type-checked.** Cheap to change, self-documenting,
  refactor-safe. This is why we *can* delete half of it without fear.
- **Ports/adapters for AI and storage.** Lets us swap models and databases as we
  learn. The AI ACL especially is the right seam.
- **Evidence-first as a *principle*.** The traceability instinct is a real
  differentiator *if* trust becomes the objection. Keep the principle; shed the
  heavy implementation until it's needed.
- **Modular monolith (not microservices).** Correct; avoids distribution tax we
  haven't earned.
- **Tenant isolation as first-class.** Non-negotiable for B2B; right to bake in.
- **Published-Language boundaries.** Even if the boundaries move, the discipline of
  explicit cross-context contracts is what makes moving them survivable.

The through-line: the *mechanisms* (contracts, ports, boundaries) are high
leverage; the *specific domain bets* (drift, official model, confidence depth) are
where we over-committed.

---

## 8. Where we've created unnecessary maintenance cost

- **Six contexts before one customer.** Every customer-driven change now ripples
  across six contexts' aggregates, events, invariants, read models, and PLs. We
  maximized change-amplification at exactly the stage we need change to be cheap.
- **Duplicated cross-cutting machinery.** Each context re-declares confidence
  aliases, invariant registries, validation wiring, event envelopes. DRY debt
  compounding silently.
- **Structural friction we invented.** The PL/id-export gap, the indexed-access id
  hacks, three versioning schemes — self-inflicted from over-structuring boundaries
  before they were load-bearing.

---

## 9. Rewrite forecast — after 100 customer interviews in 6 months

What I'd bet actual money we rewrite or delete:

- **Delete/shelve for v1:** Drift/Assessment, the `Official*` governance model,
  identity resolution, the synthesis layer (clusters/bundles/root-cause),
  maturity/readiness scores, transcript versioning/corrections.
- **Rewrite:** the node ontology (toward per-industry flexibility or a looser
  schema); the confidence model (down to 1–2 numbers); the validation workflow
  (around consultant time, not per-item); the Organization model (down to "import
  the mess").
- **Build for the first time:** the interview engine, the consent/anonymity model,
  the learning loop, unit economics. **The things that decide the business are the
  things not yet built.**
- **Keep:** contracts discipline, ports, tenant isolation, the modular monolith,
  and the evidence-first *principle* (thinned out).

Rough estimate: **50–70% of the domain surface we've written will be deleted,
shelved, or materially rewritten within two quarters of real usage.** That is not
a failure — it's the expected cost of having modeled ahead of learning. The failure
would be *defending* it.

---

## 10. The reframe: what release one should actually be

Not this. The first release should be the **thinnest possible learning loop:**

> Run one AI interview → extract a handful of candidate insights → put them in
> front of one real consultant → measure if they're useful and true.

For that, most of these contexts should not exist yet. Keep a transcript store, a
minimal claim/insight store, and the AI ports. Everything else is a bet we should
be *able* to make later — which, thanks to the contracts and ports, we can — but
should not have made now.

**The architecture's greatest strength is that it's cheap to delete. Our job this
quarter is to earn the right to keep each piece by observing a customer need it —
and to delete, without ceremony, everything that no customer reaches for.**
