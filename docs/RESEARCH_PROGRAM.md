# Groundwork — Scientific Research Program

*The set of scientific questions, experiments, and milestones that would turn
Groundwork from a clever product into a serious applied-research program. Not a
roadmap of features — a roadmap of what we do not yet know, how we would learn it,
and what would prove us wrong.*

---

## Framing: five kinds of claim (do not blur them)

Almost every argument inside Groundwork is really a disagreement about *which kind of
claim* is on the table. We separate them permanently:

| Claim type | Form | Verified by | Example in Groundwork |
|---|---|---|---|
| **Engineering** | "We can build X that does Y reliably" | Construction + tests | "The AI engine returns evidence-linked DTO proposals." |
| **Product** | "A user gets value V from X" | Usage, adoption, willingness to pay | "A consultant reaches a diagnosis faster with Groundwork." |
| **Statistical** | "Metric M differs by Δ ± U" | Powered measurement | "AI interviews surface 1.6× the Tier-3 disclosures of a survey." |
| **Scientific** | "Mechanism P holds in the world" | Falsifiable, generalizable experiment | "Structured AI questioning causally raises candor." |
| **Business** | "This creates defensible economic value" | Margin, moat, retention | "The learning loop compounds into a durable advantage." |

The company's failure mode is asserting a **business** or **scientific** claim on
the strength of an **engineering** demo. This program exists to stop that.

## The bottleneck under everything: there is no ground truth

Organizational truth is not observable. When the system is wrong, there is usually
no error signal. Every question below is therefore constrained by a prior
methodological question — **what is a defensible proxy for organizational truth,
and do the conclusions survive changing the proxy?** Our available proxies, none
clean:

- **Synthetic organizations** — simulated orgs with a *known latent structure*. We
  control truth and measure recovery. Cheap and powerful; external validity is the
  open question (that is itself research — Q16).
- **Seeded known truths** — leadership-verified facts. Partial, biased key.
- **Behavioral / telemetry corroboration** — logs show objective process reality.
- **Predictive outcomes** — a finding predicts a later measurable event. The gold
  standard, and the slowest.
- **List experiments / randomized response** — population prevalence without
  individual disclosure (immune to social desirability).
- **Expert / consultant consensus** — a biased proxy, useful as an interim ceiling.

**Convergence across proxies is our evidence. No single proxy is trusted.**

---

## 1. Research thesis

> **Groundwork is a bet on two hypotheses, not two facts.**
> **(H-A, the recovery hypothesis):** decision-grade organizational truth is
> recoverable from structured testimony at a quality and cost that beats surveys,
> junior consultants, and digital-exhaust analytics.
> **(H-B, the compounding hypothesis):** the *skill* of recovering it improves with
> validated feedback and *transfers across organizations* without leaking any
> client's data.
>
> H-A is an existence question — does the core loop produce truth at all? It is
> mostly testable now. H-B is a moat question — does the loop compound? It is
> **not** testable now (it is data-starved) and may be false. The research program
> is the disciplined, falsifiable path to learning whether each is true, and the
> willingness to conclude that either is not.

Two orthogonal axes organize the whole agenda, because each side fails
independently and needs its own science:

- **Elicitation** (getting truth *out of a person*) **vs Synthesis** (turning many
  disclosures *into organizational truth*).
- **Truth** (correspondence to reality) **vs Usefulness** (decision-relevance). A
  true-but-useless finding and a useful-but-unfalsifiable one are both failures.

---

## 2. Ranked open scientific questions

Ranked by **de-risking leverage × tractability now**. Tier A de-risks the company
and is testable now; Tier B creates the moat but is data-gated; Tier C is deep
science, slow, and partly maybe-unanswerable.

| # | Question | Dominant claim type | Testable now? | Tier |
|---|---|---|---|---|
| Q16 | What proxy for organizational truth is defensible? *(meta)* | Scientific / methodological | **Yes** | A |
| Q1 | Do AI interviews extract truth materially better than surveys **and** than a junior consultant? | Statistical → Scientific + Product | **Yes** | A |
| Q2 | Under what confidentiality/framing conditions does candor become usable, and is the effect causal? | Scientific + Product | **Yes** | A |
| Q3 | Does synthesis produce **decision-grade** findings better than baseline (value density)? | Product + Scientific | **Yes** | A |
| Q15 | Does the system fail *gracefully* under low-signal interviews — abstain vs confabulate — and can it tell useful uncertainty from empty ambiguity? | Engineering + Scientific | **Yes** | A |
| Q7 | When is contradiction a *signal* (conflict/variation/complementarity) vs noise? | Scientific | Partly (synthetic) | A/B |
| Q8 | Can fusing multiple biased testimonies beat any single one (crowd truth)? | Scientific | Partly (synthetic) | A/B |
| Q6 | Does consultant validation actually improve the policy in a measurable way? | Scientific (the compounding crux) | **No — data-starved** | B |
| Q5 | Can a *learned* questioning policy outperform a scripted one? | Scientific + Engineering | **No — data-starved** | B |
| Q4 | Can confidence be calibrated against outcomes (evidence→belief updating)? | Statistical + Scientific | Partly (interim proxy) | B |
| Q9 | Does modeling *standpoint* (role/incentive) improve truth recovery? | Scientific | Yes (synthetic), partly real | B |
| Q13 | Does anything learned on client A improve performance on client B? | Scientific + Business (the moat) | **No — multi-client-gated** | B |
| Q14 | Can priors transfer across orgs without leaking sensitive data? | Engineering + Scientific | Mechanism yes; value only after Q13 | B/C |
| Q10 | How fast does organizational truth decay (non-stationarity)? | Scientific + Business | **No — longitudinal** | C |
| Q11 | Can testimony be upgraded from correlational to *causal*? | Scientific | **Likely not at small N** | C |
| Q12 | Can economic decision-confidence be validated against real outcomes? | Business + Scientific | **No — slow, small-N** | C |
| Q17 | Does the core loop generalize across industries/cultures? | Business + Scientific | Premature | C |

---

## 3. The questions in detail

Each: **why it matters · hypothesis · experiment · data needed · what supports ·
what falsifies · claim type · testability.**

### Tier A — de-risking, testable now

**Q16 — Ground-truth proxy validity *(area 1; meta)***
- *Why.* Every other result is only as trustworthy as the proxy behind it. If
  conclusions flip when the proxy changes, we know nothing.
- *Hypothesis.* Recovery quality measured against synthetic-org ground truth
  correlates with quality measured against seeded truths and telemetry (proxies
  agree).
- *Experiment.* Build a synthetic-organization testbed with known latent structure;
  run the full loop; compare rankings of system variants under each proxy.
- *Data.* Synthetic orgs; a small real design-partner set with seeded truths + logs.
- *Supports.* Variant rankings are stable across proxies (rank correlation high).
- *Falsifies.* Rankings reorder by proxy → our metrics measure the proxy, not truth.
- *Claim.* Scientific/methodological. *Testable now.* This is infrastructure that
  unblocks everything else — build it first.

**Q1 — Elicitation superiority *(areas 1, 3; "better than surveys / junior
consultant")***
- *Why.* If AI interviews are not materially better than a survey or a junior
  consultant, the core product has no reason to exist.
- *Hypothesis.* On Tier 2–4 disclosure, AI interview ≥ 1.5× survey and ≥ junior
  consultant, at lower cost.
- *Experiment.* Within-subject, counterbalanced: same subjects through survey / AI /
  junior-consultant / senior-consultant (ceiling). Benchmark all against list-
  experiment prevalence and seeded truths.
- *Data.* One–two real orgs, 15–40 subjects; the candor-experiment instruments.
- *Supports.* AI meets the pre-registered ratio and reaches ≥ 0.8× the senior ceiling.
- *Falsifies.* AI ≈ survey, or < junior consultant → no elicitation edge.
- *Claim.* Statistical (the Δ) upgrading to Scientific (the mechanism) + Product.
  *Testable now.*

**Q2 — Candor & social desirability *(area 2)***
- *Why.* Candor is the top existential risk (F1) and it may be structurally capped.
- *Hypothesis.* A confidential/employer-blinded guarantee causally raises Tier 3–4
  disclosure, mediated by perceived safety.
- *Experiment.* The pre-registered 30-day candor experiment (see
  `CANDOR_EXPERIMENT_DESIGN`): Arm A vs Arm B, four truth estimators, GO/PIVOT/KILL.
- *Data.* Real org; list/randomized-response block; perceived-anonymity scale.
- *Supports.* Positive, mediated trust-lift; Tier 2–4 capture ratio ≥ 0.5 of truth.
- *Falsifies.* No arm clears the setting gate → digital candor is structurally dead.
- *Claim.* Scientific + Product. *Testable now.*

**Q3 — Value density / decision usefulness *(area 8)***
- *Why.* "Interesting ≠ commercially useful" (F2). Truth that changes no decision is
  worthless.
- *Hypothesis.* Groundwork's synthesis yields more *evidence-backed findings a
  consultant would stake a recommendation on* than a strong LLM-summary baseline,
  and ≥ a human analyst.
- *Experiment.* Blind panel: senior consultants score each channel's output for
  decision-grade findings, blind to source; the harness's Value-Density metric.
- *Data.* Matched transcripts; ≥ 3 blind expert raters; adjudication protocol.
- *Supports.* Groundwork ≥ human on decision-grade findings; low generic-summary share.
- *Falsifies.* Groundwork ≈ generic summarizer, or < human → synthesis has no edge.
- *Claim.* Product + Scientific. *Testable now.*

**Q15 — Robustness & the abstention question *(area 15; "useful uncertainty vs
empty ambiguity")***
- *Why.* A system that confabulates when the signal is thin is a liability, not a
  tool (F4). Knowing *when to say "I don't know"* is a capability, not a gap.
- *Hypothesis.* As interview signal degrades (short, guarded, sparse), a
  well-designed system's *precision holds while recall falls* (it abstains) rather
  than fabricating.
- *Experiment.* Systematically ablate interview length/candor on synthetic + real
  transcripts; measure confabulation rate and abstention vs signal level; distinguish
  *useful uncertainty* (informative "we don't know, and here's the disagreement")
  from *empty ambiguity* (vague hedging).
- *Data.* Graded-signal transcript sets; planted-false-premise controls.
- *Supports.* Confabulation stays ≤ 5% as signal drops; system abstains gracefully.
- *Falsifies.* Confidence stays high as signal vanishes → the system hallucinates
  under pressure.
- *Claim.* Engineering + Scientific. *Testable now.* Cheap and safety-critical.

**Q7 — Contradiction as signal vs noise *(area 4)***
- *Why.* Disagreement is either Groundwork's richest signal (real conflict) or its
  worst noise (error). Mislabeling it corrupts everything downstream.
- *Hypothesis.* The system can classify a contradiction as conflict / variation /
  complementarity / error better than chance and better than a naive LLM.
- *Experiment.* Synthetic orgs where the *type* of each contradiction is known by
  construction; measure classification accuracy; replicate on seeded real cases.
- *Data.* Synthetic contradiction library with ground-truth types.
- *Supports.* Well-above-chance typing that transfers to real seeded cases.
- *Falsifies.* Typing collapses on real data → contradiction is unusable as signal.
- *Claim.* Scientific. *Testable now on synthetic; real is harder.*

**Q8 — Cross-person reconciliation *(area 5)***
- *Why.* The bet that many partial, biased views fuse into something truer than any
  one (organizational wisdom-of-crowds).
- *Hypothesis.* Fused multi-testimony estimates are closer to latent truth than the
  best single testimony, and error falls with the number of independent perspectives.
- *Experiment.* Synthetic orgs (known truth): measure reconstruction error vs number
  and diversity of testimonies; test whether correlated bias breaks the gain.
- *Data.* Synthetic orgs with controllable per-role bias.
- *Supports.* Monotonic error reduction with diverse perspectives.
- *Falsifies.* Fusion doesn't beat the best single source, or correlated bias
  dominates → reconciliation adds nothing.
- *Claim.* Scientific. *Testable now on synthetic.*

### Tier B — moat-creating, data-gated (not fully testable early)

**Q6 — Consultant validation as reward signal *(area 7; "does validation improve
the policy measurably")***
- *Why.* This is the crux of H-B. If validation data cannot improve the policy, the
  compounding moat does not exist and Groundwork is a static tool.
- *Hypothesis.* A policy trained/selected on validated-finding labels beats the
  frozen baseline on held-out engagements, above the noise floor.
- *Experiment.* Once ≥ N validated engagements exist, offline policy evaluation:
  train on validated labels, test on sealed held-out engagements. Pre-register N and
  the effect threshold. Use synthetic data first to prove the *mechanism can* learn.
- *Data.* Many validated engagements (the four-layer dataset). **We do not have
  this yet.**
- *Supports.* Measurable, replicated lift on held-out engagements.
- *Falsifies.* No lift beyond noise, or validation labels too sparse/biased to learn
  from → the loop does not compound.
- *Claim.* Scientific. **Not testable now — data-starved (cold start).** De-risk the
  *mechanism* on synthetic data; test for real in Year 2–3.

**Q5 — Learned vs scripted questioning policy *(area 3; "learned policy outperform
scripted")***
- *Why.* A learned interview policy is a candidate moat; a scripted one is copyable.
- *Hypothesis.* A learned questioning policy raises Tier 2–4 yield / value-of-
  information per question vs the best scripted policy.
- *Experiment.* Simulated interviewees (synthetic) first; then A/B on real
  interviews once data exists. Measure information gain per turn.
- *Data.* Interview simulator + volume of real interviews. **Insufficient now.**
- *Supports.* Learned policy dominates on information-per-turn, replicated.
- *Falsifies.* Scripted ≈ learned → no policy moat; keep the script (product win).
- *Claim.* Scientific + Engineering. **Not testable now.**

**Q4 — Evidence→belief updating & calibration *(area 6; "confidence calibrated
against outcomes")***
- *Why.* Calibration is a moat precondition and the difference between a decision
  tool and a confident liar (F11).
- *Hypothesis.* The system's confidence is calibrated: p-confident findings are
  right ≈ p of the time — first against consultant validation (interim), then
  against real outcomes.
- *Experiment.* Reliability diagrams / ECE against validation now; against realized
  outcomes later. Compare Bayesian-style evidence updating vs heuristic aggregation.
- *Data.* Validated findings now; outcome-linked findings later (slow).
- *Supports.* Low ECE, stable across tiers, improving over time.
- *Falsifies.* Systematic over/under-confidence that resists correction.
- *Claim.* Statistical + Scientific. *Partly testable now* (interim proxy); full
  outcome calibration is **longitudinal.**

**Q9 — Standpoint / perspective modeling *(area 9)***
- *Why.* Testimony is never a view from nowhere; ignoring who speaks may bias
  synthesis.
- *Hypothesis.* Conditioning on standpoint (role, incentive, exposure) improves
  truth recovery vs treating testimony as unweighted.
- *Experiment.* Synthetic orgs with role-dependent bias: compare standpoint-aware vs
  standpoint-blind reconstruction.
- *Data.* Synthetic (now); real role-tagged testimony (later).
- *Supports.* Standpoint-aware fusion reduces error, esp. under correlated bias.
- *Falsifies.* No improvement → standpoint is overhead, not signal.
- *Claim.* Scientific. *Testable now on synthetic.*

**Q13 — Cross-client learning *(area 13; the moat engine)***
- *Why.* If nothing transfers across clients, there is no compounding data moat —
  only per-engagement value.
- *Hypothesis.* A *meta-layer* (elicitation patterns, calibration, finding
  taxonomies) learned across clients improves cold-start performance on a *new*
  client, even though org facts do not transfer.
- *Experiment.* Leave-one-client-out: does training on clients 1…k−1 improve
  performance on client k vs from-scratch? Separate meta-layer transfer from
  fact-leakage.
- *Data.* Many clients + validated outcomes. **Multi-client-gated — not now.**
- *Supports.* Consistent leave-one-out lift attributable to the meta-layer.
- *Falsifies.* No transfer → the dataset is a pile of stale, non-transferable
  (and legally radioactive) transcripts; the compounding moat is dead.
- *Claim.* Scientific + Business. **Not testable until multiple clients exist.**

**Q14 — Privacy-preserving prior transfer *(area 14; "priors transfer without
violating privacy")***
- *Why.* Even if priors transfer (Q13), doing it without leaking a client's data is
  a hard constraint and a trust requirement.
- *Hypothesis.* Federated / differentially-private aggregation of priors preserves
  the transfer benefit within an acceptable privacy budget.
- *Experiment.* Compare transfer lift with and without DP/federation; measure the
  privacy-utility tradeoff; adversarial reconstruction tests.
- *Data.* Multi-client priors (after Q13); DP tooling.
- *Supports.* Meaningful transfer survives a defensible privacy budget; no
  reconstruction.
- *Falsifies.* Privacy kills the signal, or the signal leaks identities → the moat
  and the trust position are incompatible.
- *Claim.* Engineering + Scientific. *Mechanism testable now; value only after Q13.*

### Tier C — deep science, slow, partly maybe-unanswerable

**Q10 — Organizational non-stationarity *(area 10)***
- *Why.* Governs whether the dataset compounds or rots (moat §10). If truth decays
  faster than we accumulate it, there is no asset.
- *Hypothesis.* Organizational truths have measurable, type-dependent half-lives
  (structure slow, sentiment fast).
- *Experiment.* Longitudinal re-interviewing of the same orgs over quarters;
  measure belief-decay curves by finding type.
- *Data.* Multi-quarter longitudinal panels. **We do not have time yet.**
- *Supports.* Stable, estimable decay curves that inform refresh cadence.
- *Falsifies.* Decay so fast/erratic that findings expire before they're used.
- *Claim.* Scientific + Business. **Untestable now — inherently longitudinal.**

**Q11 — Causal upgrading *(area 11)***
- *Why.* Recommendations imply causes ("X *causes* the delay"). Testimony gives
  correlation and belief, not intervention.
- *Hypothesis.* Testimony + structure can license *some* defensible causal claims
  above correlational baselines.
- *Experiment.* Where natural experiments / interventions exist, test predicted
  causal effects against outcomes; otherwise restrict to falsifiable causal
  sub-claims.
- *Data.* Interventions / natural experiments — rare and expensive.
- *Supports.* Predicted causal effects verified post-intervention.
- *Falsifies.* Causal claims no better than correlation → do not sell causal claims.
- *Claim.* Scientific. **Likely not answerable at current N/setup** — causal
  inference from observational testimony without intervention is fundamentally hard.
  *State this honestly to buyers: today Groundwork surfaces causal hypotheses, not
  causal proofs.*

**Q12 — Economic decision-confidence *(area 12)***
- *Why.* The ultimate value claim: decisions made on Groundwork's output beat decisions
  made without it, at a knowable confidence.
- *Hypothesis.* Recommendations carry confidence that predicts realized economic
  outcome.
- *Experiment.* Track recommendation → decision → outcome over engagements; compare
  to a counterfactual/holdout baseline.
- *Data.* Many decisions with measurable outcomes. **Slow, small-N, confounded.**
- *Supports.* Confidence predicts outcome; Groundwork-informed decisions win.
- *Falsifies.* No predictive link → economic confidence is unfounded.
- *Claim.* Business + Scientific. **Not testable at meaningful power for years.**

**Q17 — Cross-industry generalization *(area; "does the loop generalize")***
- *Why.* Determines whether Groundwork is a market or a niche.
- *Hypothesis.* The core loop's advantage holds across verticals/cultures after
  minimal adaptation.
- *Experiment.* Replicate the Tier-A battery in a second, then third, distinct
  vertical/culture; test for degradation.
- *Data.* Multi-vertical engagements. **Premature — needs single-vertical success
  first.**
- *Supports.* Advantage replicates with bounded adaptation cost.
- *Falsifies.* Advantage is vertical-specific → the market is smaller than pitched.
- *Claim.* Business + Scientific. **Premature now.**

---

## 4. One-year research program — *prove H-A exists, and fail safely*

Goal: a defensible answer to "does the core loop produce truth better than the
alternatives, and does it fail gracefully?" — plus the infrastructure to answer
H-B later.

1. **Build the synthetic-organization testbed + ground-truth methodology (Q16).**
   Infrastructure; unblocks Q7/Q8/Q9/Q15 and the mechanism-checks for Q5/Q6.
2. **Run the candor experiment (Q2)** and the **elicitation head-to-head (Q1)** —
   AI vs survey vs junior vs senior ceiling.
3. **Value-density blind panels (Q3).**
4. **Robustness & abstention study (Q15).**
5. **Contradiction typing (Q7) and reconciliation (Q8) on synthetic orgs.**
6. **Instrument every real engagement to capture the four-layer validated dataset —
   accumulation only, no learning claims yet.** This is the seed corn for Year 2.

Deliverable: an existence proof (or refutation) of H-A, and a growing validated
dataset. **Explicitly not claimed this year:** that the loop learns or compounds.

## 5. Three-year research program — *test H-B, the compounding moat*

With accumulated validated data:

1. **Validation-as-reward (Q6)** — does the loop *learn*? The single most important
   result for the company's identity.
2. **Learned vs scripted policy (Q5).**
3. **Cross-client transfer (Q13)** — the moat existence proof; leave-one-client-out.
4. **Calibration against interim then early real outcomes (Q4).**
5. **Standpoint modeling (Q9)** on real role-tagged data.

Deliverable: evidence that Groundwork *improves with data* and that skill *transfers
across clients* — or a clear refutation that reclassifies Groundwork as a
(valuable) static product. **Gate:** if Q6 and Q13 both fail, H-B is dead; stop
funding the research lab and become a product company (see §9).

## 6. Five-year research agenda — *the ambitious science (if earned)*

Pursued only if H-B holds:

- **Non-stationarity models (Q10)** — belief-decay curves; refresh cadence.
- **Privacy-preserving federated priors at scale (Q14)** — the trust-compatible moat.
- **Causal upgrading (Q11)** — from causal hypotheses toward defensible causal
  claims where interventions exist. *May remain unanswerable; treat as a frontier,
  not a promise.*
- **Economic decision-confidence (Q12)** — outcome-validated recommendation
  confidence.
- **Cross-industry generalization (Q17).**
- **Synthesis:** a *validated organizational world model* whose beliefs are
  calibrated against reality over time — the genuine research contribution, and the
  thing that would make Groundwork a lab, not a tool. Only credible after the above.

---

## 7. Smallest set of experiments that de-risks the company

Four, all runnable in ~one quarter on 1–2 design partners plus the synthetic
testbed. If these fail, stop — it is the cheapest possible kill:

1. **Candor (Q2)** — will people tell the truth at all?
2. **Elicitation superiority (Q1)** — better than a survey and a junior consultant?
3. **Value density (Q3)** — is the output decision-grade, not just interesting?
4. **Robustness/abstention (Q15)** — does it fail safe instead of confabulating?

These four test H-A end to end. Everything downstream is moot if they fail.

## 8. Highest-leverage experiments that could create a moat

The moat lives in exactly two results, both data-gated:

1. **Q6 — validation improves the policy measurably** (the loop *learns*).
2. **Q13 — skill transfers across clients** (the loop *compounds*).

Because both need data we don't have, the highest-leverage *early* action is not an
experiment but **infrastructure**: build the synthetic testbed to prove the
learning *mechanism* can work in principle (de-risking Q6 before real data), and
instrument every engagement to capture the four-layer dataset so Q6/Q13 become
answerable the moment volume exists. **The moat is bought in Year 1 by
instrumentation and proven in Year 2–3 by these two experiments.**

## 9. Results that would make Groundwork more product-oriented (less research)

Any of these means: stop funding the lab, ship the tool, compete on trust/workflow.

- **H-A holds but H-B fails** — elicitation/synthesis are real and robust, but the
  loop does **not** compound (Q6/Q13 fail). You have a valuable *static* tool.
- **A simple scripted approach already hits value density (Q3),** making learned
  policy (Q5) unnecessary.
- **Heuristic confidence is calibrated enough (Q4),** making the epistemology build
  unnecessary.
- **Reconciliation/standpoint add little (Q8/Q9)** beyond a strong single-pass
  synthesis.

In all of these, the *simple* version works and the *compounding* version doesn't —
so become a product company and delete the research overhead (Constitution Art.
XVIII).

## 10. Results that would make the agenda more ambitious (more research)

- **Cross-client transfer is real (Q13)** → build the federated organizational
  foundation model.
- **Learned policy beats scripted with modest data (Q5)** → invest in
  RL-from-validated-outcomes.
- **Confidence calibrates against real outcomes (Q4/Q12)** → pursue economic
  decision-confidence and the world-model agenda.
- **Causal upgrading shows any traction (Q11)** → a genuine, publishable scientific
  frontier.

Each of these upgrades a *product* claim into a *scientific* one and justifies a
real research organization.

---

## 11. Honest register (say the quiet part)

**Not testable now — data-starved (cold start):** Q5, Q6, Q13, Q14-value. The
compounding thesis cannot be tested until validated engagements accumulate. Do not
claim the loop learns before Q6 returns. De-risk mechanisms on synthetic data
meanwhile.

**Too expensive / too slow now — inherently longitudinal:** Q10 (non-stationarity),
Q12 (economic decision-confidence), full-outcome Q4. These require quarters-to-years
of realized outcomes and are confounded at small N.

**Likely unanswerable with the current setup:** Q11 (causal upgrading) at small N
without interventions — causal inference from observational testimony is
fundamentally hard; today Groundwork produces causal *hypotheses*, not proofs, and we
should sell it as such. A fully general Q17 is premature until one vertical works.

**Currently unfalsifiable and therefore not yet science:** large parts of the
organizational epistemology (belief decay, credal sets, causal graph evolution) are
*engineering dressed as science* until outcome data exists to falsify them. They are
legitimate *engineering* scaffolding — but must not be described as validated
*scientific* claims until Q4/Q10/Q12 give them a falsification surface.

---

## Closing note

The intellectually honest position is that Groundwork today has **strong engineering
claims, plausible product claims, almost no validated statistical claims, no
established scientific claims, and an unproven business claim.** That is not an
indictment — it is a normal starting point for an applied-research company. What
would be an indictment is pretending otherwise. This program's discipline is
simple: **do not promote a claim to a higher type than the evidence supports, run
the cheapest experiment that could kill each hypothesis first, and be genuinely
willing to conclude that the compounding thesis — the entire scientific ambition —
is false, and that Groundwork is a good tool rather than a new science.** We will know
which within three years. Most companies never let themselves find out.
