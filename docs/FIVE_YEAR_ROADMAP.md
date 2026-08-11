# Ontora — Five-Year Research & Product Roadmap

*How Ontora becomes better every year without losing product focus: a program for
building a defensible, compounding, scientifically credible organizational
reasoning system. Not a feature roadmap — a plan for turning validated customer
work into science, and science back into customer value, on a loop that widens
with time.*

---

## 1. Executive summary

Ontora's long-term value does not come from a model, a graph, or an architecture —
all rented, copyable, or invisible (see `MOAT_ANALYSIS`). It comes from a **loop**:

> **Product generates validated-outcome data → data enables science (calibration,
> learned policy, cross-client transfer) → science raises product value → better
> product wins more and deeper engagements → more validated data.**

The moat is the *rate and integrity* of this loop, protected by a trust/privacy
position the platforms cannot occupy and made durable by keeping every model
swappable. Three commitments define the whole roadmap:

1. **Frontier model improvement is a tailwind, not a threat.** We never own or bet
   on a model. We rent the best available behind an abstraction and capture the
   improvement as free quality and margin. What we own is the *validated-outcome
   dataset, the calibration, and the trust* — the layers models don't touch. If
   GPT-N+1 or Claude-N+1 gets better tomorrow, Ontora gets better tomorrow, for free.
2. **We do not promote a claim above its evidence.** Year 1 proves the *product*
   claim (the wedge works). Years 2–3 test the *scientific/business* claim (the loop
   compounds). We refuse to sell the second before we've earned it.
3. **There is an honest fork at Year 3.** If the loop compounds (skill transfers
   across clients), Ontora becomes a research company with a widening moat. If it
   does not, Ontora is a *very good product company* with a trust moat — we say so,
   delete the research overhead, and stop pretending. Both are fundable. Only
   self-deception is fatal.

The arc: **Year 0–1 prove the wedge · Year 1–2 make the loop reliable · Year 2–3
prove it compounds (the moat) · Year 3–4 add causal & economic reasoning · Year 4–5
validated organizational prediction.** Each year's product work is the data
generator for the next year's science.

---

## 2. The compounding mechanism (why the loop, not the code, is the asset)

| Stage | What produces it | What it unlocks | The thing that could break it |
|---|---|---|---|
| Validated engagements | Product + consultants | Raw four-layer dataset | Candor fails (F1); no product-pull |
| Validated-outcome labels | Consultant validation + real outcomes | Calibration, learned policy | Rubber-stamping; sparse/biased labels |
| Meta-layer patterns | Cross-client abstraction | Cross-client transfer (the moat) | Nothing transfers (H-B false); privacy leak |
| Calibrated confidence | Outcomes over time | Economic & causal reasoning | Non-stationarity; small-N |
| Validated world model | Longitudinal corpus | Predictive capability | Can't calibrate → confident fantasy |

**The levers shift by year.** Year 1 gains come from **prompts + UX** (data is too
thin to help). Year 2 gains shift to **data** as the validation loop starts paying.
Year 3+ gains come *primarily from data* — the compounding kicks in and UX work
turns toward trust and enterprise-readiness. Anyone who tries to win Year 3 with
better prompts has misunderstood the company.

---

## 3. Year-by-year roadmap

Each year: the **spine** (the one question), a **seven-track milestone table**, the
**north-star metric**, the **decision gate**, and the **top risks**.

### Year 0–1 — Prove the wedge *(does the core loop produce decision-grade truth, and fail safe?)*

| Track | Milestone |
|---|---|
| **Research** | Build the synthetic-org testbed + ground-truth methodology (Q16); run the Tier-A battery: elicitation superiority vs survey & junior consultant (Q1), candor experiment (Q2), value density (Q3), robustness/abstention (Q15). |
| **Product** | Thin MVP: interview → findings → evidence → report, consultant-in-the-loop, evidence-first UI. 3–5 real design partners doing real engagements. |
| **Data** | Stand up the four-layer validated dataset (testimony/interpretation/validation/outcome) and instrument *every* engagement. **Accumulation only — no learning claims.** Get the pipeline right so nothing is ever lost or fused. |
| **Model** | Single best frontier model behind a provider abstraction. **Prompts + eval only. No fine-tuning.** RAG only for within-engagement evidence grounding (provenance resolution). |
| **Trust / Workflow** | Confidentiality architecture live (employer-blinded guarantee); consultant validation as a first-class recorded domain event; evidence shown before any human judgment. |
| **Defensibility** | The trust posture + the *beginning* of the dataset. Nothing else claimed. |
| **Enterprise** | Consent + legal review; data firewall; SOC2 path started. |

- **North star:** *Decision-grade findings per engagement vs baseline* (value density),
  and *Tier 2–4 candor capture ratio*.
- **Decision gate (the investment bar):** to deserve further investment, by end of
  Year 1 — candor clears the setting gate, value density ≥ human baseline, robustness
  fails safe (confabulation ≤ 5%), AND product-pull exists (design partners renew /
  pay). If candor or value density fail → **pivot or stop.** This is H-A.
- **Top risks:** candor structurally capped (F1); "interesting ≠ useful" (F2); no
  product-pull; confabulation under thin signal (F4).

### Year 1–2 — Make the interview & validation loop reliable *(can the loop even learn?)*

| Track | Milestone |
|---|---|
| **Research** | Prove the *learning mechanism* on synthetic data (Q6/Q5 in simulation — can validation-as-reward improve a policy in principle?); interim calibration against consultant validation (Q4); standpoint modeling on real data (Q9). |
| **Product** | Eval-driven interview improvements (still scripted+prompted); richer consultant workflow; within-client longitudinal memory (RAG over prior findings/evidence). |
| **Data** | Reach the volume + label-quality threshold where offline policy evaluation becomes possible; validation friction reduced *without* inviting rubber-stamping. |
| **Model** | Base still swappable; retrieval matures; **lightweight adapters considered only if a narrow task plateaus on the best base model. Full fine-tuning still avoided** (lock-in, base models improve faster). |
| **Trust / Workflow** | Calibrated confidence surfaced to consultants ("70%" that means something); override/validation UX that respects human authority. |
| **Defensibility** | Within-client leave-one-engagement-out value appears; calibration begins to be provable. |
| **Enterprise** | SOC2 Type II; SSO; audit logs; data-residency options. |

- **North star:** *Interim calibration (ECE against validation)* and *validation
  throughput × quality*.
- **Decision gate:** the loop shows a *learnable signal* on synthetic data and
  labels are clean enough to learn from. If no learnable signal even in simulation,
  or labels are hopelessly noisy/biased → the compounding thesis is in doubt; lean
  product-oriented.
- **Top risks:** rubber-stamping degrades label quality (F6); validation too sparse;
  the loop learns its own hallucinations (F18).

### Year 2–3 — Learn cross-engagement patterns *(THE moat test — does skill transfer across clients?)*

| Track | Milestone |
|---|---|
| **Research** | Q6 for real (does validation improve the policy on held-out engagements?); **Q13 cross-client transfer via leave-one-client-out** — the moat existence proof; Q5 learned > scripted on real data. |
| **Product** | Learned questioning policy (if Q5 passes); cross-engagement pattern library surfaced as priors → faster, better cold start on new engagements. "Gets better every engagement" becomes a *measured* claim, not a slogan. |
| **Data** | Multi-client validated corpus; extract the **meta-layer** (elicitation strategies, finding taxonomies, calibration curves). **Never pool raw cross-client testimony.** |
| **Model** | Fine-tuning/adapters now permissible on *stable, narrow, high-volume* tasks **only if prompting has plateaued** — and treated as **disposable, re-derivable from the dataset**; base stays swappable. |
| **Trust / Workflow** | Privacy-preserving cross-client priors (Q14 mechanism): abstracted patterns only, DP/federation, adversarial reconstruction tests. |
| **Defensibility** | **The moat is proven or refuted this year:** cross-client transfer + calibration + trust. |
| **Enterprise** | Procurement-grade: DPA, pen tests, RBAC, hardened multi-tenant isolation. |

- **North star:** *Cross-client transfer lift (leave-one-client-out)* — **the single
  most important number in the five years.**
- **Decision gate (the fork):** if Q6 **and** Q13 fail → H-B is dead. Reclassify as a
  product company, stop funding the lab, delete the research overhead (Constitution
  Art. XVIII), compete on trust/workflow. If they pass → the compounding moat is
  real; fund the deep science.
- **Top risks:** nothing transfers (moat is a mirage); privacy leak in transfer
  (kills trust *and* moat at once); fine-tune lock-in creeping in.

### Year 3–4 — Causal & economic reasoning *(from description to defensible cause and value)*

| Track | Milestone |
|---|---|
| **Research** | Causal upgrading where interventions/natural experiments exist (Q11); economic decision-confidence (Q12); full calibration against *real outcomes* (Q4); non-stationarity / decay curves from now-available longitudinal data (Q10). |
| **Product** | Recommendations carry *outcome-validated* economic confidence; causal *hypotheses* upgraded to causal *claims* only where warranted (sold honestly); refresh cadence driven by measured decay. |
| **Data** | Outcome-linked findings accumulate; longitudinal panels; causal validation where interventions occur. |
| **Model** | Mature; value is now overwhelmingly data + calibration; base still swappable — frontier gains are pure margin. |
| **Trust / Workflow** | Outcome-validated confidence becomes the ultimate trust artifact ("decisions on our 70% findings paid off ≈70% of the time"). |
| **Defensibility** | Outcome data + calibration is now very hard to copy; the moat widens with every engagement. |
| **Enterprise** | Enterprise-scale deployments; integrations (HRIS, process-mining complement). |

- **North star:** *Outcome-validated decision-confidence* (does stated confidence
  predict realized outcome?).
- **Decision gate:** if causal shows no traction (Q11 may be unanswerable) → do **not**
  sell causal claims; stay descriptive + economic. If economic confidence doesn't
  predict outcomes → don't overclaim; remain a calibrated diagnosis tool.
- **Top risks:** selling causal proofs we don't have (F5 legal); small-N/confounded
  economic claims; decay faster than accumulation.

### Year 4–5 — Organizational simulation / predictive capability *(the validated world model, if earned)*

| Track | Milestone |
|---|---|
| **Research** | Predictive organizational simulation **validated against realized outcomes**; counterfactual reasoning; the world-model synthesis. |
| **Product** | Predictive capability ("if you change X, expect Y") shipped **only with calibrated confidence**; scenario / what-if planning for transformations. |
| **Data** | Rich longitudinal, multi-client, outcome-linked corpus — the compounding asset at maturity. |
| **Model** | Ontora is now a data + calibration company renting whatever frontier model is best; frontier improvement is pure tailwind. |
| **Trust / Workflow** | Predictions are calibrated and evidence-grounded, or they are not shipped. |
| **Defensibility** | The validated organizational world model + trust + the loop; a new entrant needs *years of validated engagements* to match it. |
| **Enterprise** | Platform maturity; ecosystem; partner integrations. |

- **North star:** *Predictive calibration against realized outcomes.*
- **Decision gate:** if simulation cannot calibrate → do **not** ship predictions
  (confident fantasy is F4 at maximum blast radius). Remain the best diagnosis +
  economic tool — still a great company.
- **Top risks:** predictive overreach; non-stationarity defeats prediction; the
  ambition outruns the evidence.

---

## 4. Consolidated milestone tables

**Data milestones (the spine — everything else depends on these):**
| Year | Data milestone |
|---|---|
| 0–1 | Four-layer dataset live; every engagement instrumented; zero fusion, zero loss. |
| 1–2 | Volume + label-quality threshold for offline policy evaluation reached. |
| 2–3 | Multi-client corpus; meta-layer extracted; raw testimony never pooled. |
| 3–4 | Outcome-linked, longitudinal panels. |
| 4–5 | Mature longitudinal × multi-client × outcome corpus. |

**Model-quality milestones:**
| Year | Model milestone |
|---|---|
| 0–1 | Provider abstraction; prompts + eval; no fine-tuning; evidence-grounding RAG. |
| 1–2 | Retrieval matures; adapters only if a narrow task plateaus. |
| 2–3 | Fine-tuning permissible on stable/narrow/high-volume tasks, disposable, base swappable. |
| 3–4 | Model commoditized internally; value in data + calibration. |
| 4–5 | Best-available frontier model rented; improvement = pure tailwind. |

**Defensibility milestones:**
| Year | Defensibility milestone |
|---|---|
| 0–1 | Trust posture + dataset seeded. |
| 1–2 | Within-client learning value; calibration provable. |
| 2–3 | **Cross-client transfer proven (or moat refuted).** |
| 3–4 | Outcome data + calibration = hard-to-copy widening moat. |
| 4–5 | Validated world model + years-of-engagements barrier. |

**Enterprise-readiness milestones:** consent/firewall (Y0–1) → SOC2 Type II, SSO,
audit (Y1–2) → DPA, pen tests, RBAC, tenant isolation (Y2–3) → enterprise scale +
integrations (Y3–4) → platform/ecosystem (Y4–5).

---

## 5. Metric definitions (north stars)

- **Value density** — evidence-backed, Tier 2–4 findings a consultant would stake a
  recommendation on, per engagement, blind-scored vs baseline. *Not* verbosity or
  sentiment.
- **Candor capture ratio** — disclosed sensitive-truth prevalence ÷ list-experiment
  true prevalence, on Tier 2–4 (from `CANDOR_EXPERIMENT_DESIGN`).
- **Calibration (ECE)** — expected calibration error of confidence vs correctness;
  against consultant validation (interim) then realized outcomes (full).
- **Cross-client transfer lift** — leave-one-client-out performance gain on a *new*
  client attributable to the meta-layer, not fact-leakage.
- **Outcome-validated decision-confidence** — correlation between stated confidence
  and realized economic outcome.
- **Predictive calibration** — reliability of predictions against realized outcomes.

Every north star is chosen to resist gaming: none reward length, fluency, or
demo-shine; each is measured against an external truth proxy.

---

## 6. Decision gates (consolidated)

| Year | Pass condition | Fail → action |
|---|---|---|
| 0–1 | Candor clears; value density ≥ human; fails safe; product-pull | Pivot or stop (H-A false) |
| 1–2 | Learnable signal (synthetic); clean labels | Lean product; question compounding |
| 2–3 | **Q6 + Q13 pass** | **Fork: become a product company, delete research overhead** |
| 3–4 | Economic confidence predicts outcomes | Don't sell causal/economic; stay diagnostic |
| 4–5 | Predictions calibrate | Don't ship predictions; remain best diagnosis tool |

---

## 7. Risks by year (one-line each)

- **Y0–1:** candor cap (F1); interesting≠useful (F2); no product-pull.
- **Y1–2:** rubber-stamping (F6); sparse/biased labels; learning its own hallucinations (F18).
- **Y2–3:** nothing transfers (moat mirage); privacy leak in transfer; fine-tune lock-in.
- **Y3–4:** selling causal we don't have (F5); confounded economics; fast decay.
- **Y4–5:** predictive overreach; non-stationarity; ambition outrunning evidence.

---

## 8. Assumptions that must remain true (or the company collapses)

1. **Employees disclose Tier 2–4 truth under the trust guarantee.** The load-bearing
   assumption. If false, nothing else matters.
2. **Validated-outcome data compounds** (the meta-layer transfers across clients).
3. **The neutral-third-party trust position is durable** and platforms won't/can't
   occupy it.
4. **Frontier models keep improving and remain rentable** (the tailwind holds).
5. **Consultants and buyers accept AI-proposed, human-validated truth.**
6. **Privacy-preserving transfer is technically achievable** without leakage.
7. **Legal exposure from sensitive testimony stays manageable.**

## 9. Assumptions that may be safely discarded if evidence disagrees

*(Designed to be droppable — the Constitution keeps each behind a seam.)*

- The org **knowledge graph** is necessary (could be projected/replaced/deleted).
- The full **epistemology** (belief decay, credal sets, causal graphs) is needed
  early (it is engineering scaffolding until outcomes falsify it).
- **Drift / official-org model / identity resolution** are load-bearing (all
  deletable).
- A **learned policy** beats a scripted one (if Q5 fails, keep the script — a product
  win).
- **Fine-tuning** is ever required (if base + prompting suffice, never do it).
- **Causal / predictive** capability is achievable (if Q11/simulation fail, stay
  descriptive — still valuable).
- Ontora **must be a research company** (if H-B fails, be a product company — that is
  a success, not a failure).

## 10. What the company must refuse to do — even if it becomes fashionable

- **Refuse to own or train a foundation model.** Betting against your suppliers is
  suicide; models are a tailwind, not a moat.
- **Refuse premature fine-tuning** and never treat a fine-tune as the asset — the
  *dataset* is the asset; fine-tunes are disposable.
- **Refuse to fuse the four dataset layers** for convenience, ever.
- **Refuse to pool raw cross-client testimony** even when it would boost transfer —
  abstracted, privacy-preserved patterns only.
- **Refuse to auto-commit AI conclusions as truth** — human authority is final.
- **Refuse to sell causal or predictive claims before they calibrate against
  outcomes** — no confident fantasy.
- **Refuse to become the employer's surveillance tool** to buy distribution — the
  neutrality *is* the moat.
- **Refuse generic "AI agent" hype** that dilutes the wedge.
- **Refuse any finding without evidence and provenance**, and any benchmark that
  rewards verbosity.

## 11. Answers to the specific strategic questions

- **What must be true by end of Year 1 to deserve investment?** Candor is achievable
  under the guarantee; value density ≥ human; the system fails safe; and real
  design partners pull (renew/pay). H-A proven, dataset accumulating.
- **Better prompts vs data vs UX?** Prompts + UX carry Year 1 (data too thin); data
  becomes the lever in Year 2 and the *durable* one from Year 3. Win Year 1 on craft,
  win Year 3+ on data.
- **When fine-tune, when avoid?** Avoid until you have volume + validated labels and a
  narrow task that has plateaued on the best base model. Even then, fine-tunes are
  disposable and re-derivable; the base stays swappable. If prompting + retrieval
  suffice, never fine-tune.
- **When does RAG matter, and what justifies it?** Immediately for *evidence
  grounding* (provenance resolution over immutable segments) and within-engagement
  memory. Later for *cross-engagement priors* — but retrieval must honor the privacy
  firewall (retrieve abstracted patterns, never raw other-client testimony).
  Justified by measured value-density or calibration lift.
- **When does causal modeling become a priority?** Year 3–4, and only after
  calibration works and outcome data exists to validate causal predictions. Not
  before — an uncalibrated causal claim is a liability.
- **When does simulation become a priority?** Synthetic-org simulation as a *research
  testbed*: Year 0–1. Predictive organizational simulation as a *product*: Year 4–5,
  and only if it can be calibrated against reality.
- **How should cross-client priors evolve without privacy risk?** Staged: none
  (Y0–2, per-engagement only) → abstracted meta-patterns (Y2–3) → federated/DP
  aggregation with a privacy budget and adversarial reconstruction testing (Y3+).
  What transfers is validated *pattern*, never data.
- **What keeps Ontora valuable even as frontier models improve fast?** The
  validated-outcome dataset, the calibration, the trust position, and workflow
  entrenchment — none of which a better model provides. Frontier gains flow *into*
  Ontora as free quality; Ontora's moat accrues in the layers models don't reach.

---

## 12. Concluding thesis — how this turns Ontora into a compounding system

Most startups compound *distribution* or *capital*. Ontora, if it works, compounds
*validated knowledge of how organizations actually work* — a slower but far rarer
asset, because it can only be produced by doing trusted, well-measured work over
time, and it decays if not continuously refreshed. The roadmap is engineered so
that **the ordinary act of serving a customer well is the same act that produces the
scientific asset** — validation events, outcome links, calibration data — and so
that **the scientific asset, once it transfers across clients, makes the next
customer cheaper to serve and better served.** That is the loop. Its integrity is
protected by the Constitution (evidence, provenance, no fusion, deletability), its
truth is tested by the Research Program (falsifiable, claim-typed, willing to fail),
and its economics are shielded by refusing to own a model, so that every advance in
frontier AI is a gift rather than a threat. The roadmap's deepest discipline is that
it *knows which company it is building at each stage* — a product company proving a
wedge, then possibly a research company proving a science — and it has pre-committed
to telling the truth about which one it turns out to be. If the loop compounds,
Ontora becomes something a competitor cannot copy in six weeks or bundle away for
free: a calibrated, trusted, ever-deepening model of organizational reality that
took years of validated engagements to earn. If it does not compound, Ontora is
still a genuinely useful, trust-differentiated product — and it will have spent the
minimum to find out. Either way, the company is built to learn the truth about
itself, which is the only foundation on which a system that claims to learn the
truth about others can honestly stand.
