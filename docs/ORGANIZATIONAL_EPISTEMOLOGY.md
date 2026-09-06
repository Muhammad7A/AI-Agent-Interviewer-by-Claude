# Toward Organizational Truth: An Epistemic Foundation for Groundwork

**A research agenda, not a specification.**

---

## Abstract

Groundwork is not an information system. It is an **epistemic engine**: a machine that
continuously estimates the enacted reality of an organization from a stream of
partial, perspectival, non-stationary, and strategically distorted human testimony,
and reports its estimates to a decision-maker at the resolution their decision
requires. This paper reframes the platform's foundations away from *storage of
asserted facts* toward *inference over a latent, moving target*. We argue that the
central object of the platform is not a knowledge graph but a **time-indexed belief
measure over organizational world-models**, and that the central operation is not
extraction but **Bayesian inversion of a learned testimony-generating process**. We
develop fourteen coupled constructs — from a testimony likelihood and a
standpoint-aware fusion rule to belief decay, causal upgrading, and
decision-relative sufficiency — and we delete three assumptions inherited from the
incumbent architecture that we now regard as category errors. The defensible asset,
we conclude, is neither the model nor the data but the **hierarchically learned
priors** that let each new engagement start closer to the truth than the last.

---

## 1. Introduction: the epistemic reframing

The incumbent architecture treats knowledge as a set of asserted propositions, each
carried by immutable evidence and blessed into truth by a consultant. Every clause
of that sentence conceals an error. Propositions about organizations are not
asserted; they are *estimated*. Evidence does not carry truth; it carries
*testimony*, which is truth twice-filtered. And a consultant does not bless truth;
a consultant is another fallible observer whose word is strong evidence, not an
oracle.

We propose instead that Groundwork is a **Bayesian filter over a non-stationary latent
organizational process**, equipped with a *learned, perspective-aware testimony
likelihood*, pursuing *decision-sufficient* posterior resolution, while accounting
for its own *reflexive* perturbation of the system it observes. Everything that
follows elaborates that single sentence.

The stakes of the reframing are practical. If knowledge is asserted, the product is
a database and its moat is data volume — commoditized the moment a competitor rents
the same model. If knowledge is *estimated from a learned generative model of human
testimony*, the moat is the estimator, and the estimator compounds. The
epistemology is the business model.

---

## 2. The seven axioms of an organizational epistemology (Construct 1)

We take organizational knowledge to be governed by seven axioms, each of which
constrains the formalism that follows.

- **A1 — No God's-eye view.** There is no accessible ground truth about how an
  organization works. All access is testimonial and indirect. Any design that
  presumes an oracle (immutable evidence, consultant sign-off) is unsound.
- **A2 — Enacted primacy.** The object of knowledge is *enacted* reality — what is
  actually done — which systematically diverges from *espoused* reality — what is
  said to be done (after Argyris & Schön). The divergence is itself knowable and is
  the platform's richest signal.
- **A3 — Perspectival realism.** There *is* a real organization, but it is knowable
  only through aggregated, weighted standpoints. Disagreement between well-placed
  observers is information about the world, not merely noise to be averaged away
  (after standpoint epistemology and the Rashomon problem).
- **A4 — Non-stationarity.** Organizational truth changes on multiple timescales.
  Knowledge is therefore *perishable*: a belief unrefreshed decays toward ignorance.
- **A5 — Reflexivity.** To surface a belief about an organization is to change the
  organization (Hawthorne; Goodhart). The epistemology must model its own
  intervention.
- **A6 — Decision-relativity.** Truth is not pursued to certainty but to the
  resolution a decision requires. "How sure are we?" is ill-posed without "sure
  enough for *what*?"
- **A7 — Fallible aggregation.** Every source — interviewee, document, and
  consultant alike — is a fallible observer with a characterizable bias. None is an
  oracle; all are likelihoods.

These axioms are not decoration. A3 forbids naive averaging; A4 forbids permanent
storage of belief; A5 forbids purely observational causal claims; A6 forbids a
scalar global confidence; A7 forbids treating validation as ground truth. The
incumbent architecture violates all five.

---

## 3. The organizational world model (Construct 14, stated first because it is the substrate)

Let **Ω** be the space of *organizational world-models*. A single ω ∈ Ω is a
complete specification of the organization's enacted reality: its work, flows,
decision rights, dependencies, and the causal mechanisms among them. ω is latent
and never observed.

Crucially, ω is not static. We model the organization as a **latent stochastic
process** {ω_t}, evolving under both endogenous drift and exogenous shocks
(reorgs, tooling changes, market events). Groundwork's task is *filtering*: maintaining
a belief over ω_t given the observation history, and *smoothing*: revising past
beliefs in light of later evidence.

> **Definition (World model).** ω_t ∈ Ω is the enacted state of the organization at
> time t: a structured object comprising entities, the flows and dependencies among
> them, and the causal mechanisms that generate outcomes. It is the hidden state of
> a partially observed, non-stationary stochastic process.

Observations are *not* draws from ω. They are draws from a **testimony-generating
process** parameterized by ω *and by the observer* (§5). This distinction — between
the world and its testimony — is the pivot of the entire theory.

---

## 4. Belief representation (Construct 2)

Groundwork's state of knowledge at time t is a **belief measure** B_t over Ω:

    B_t : Ω → [0,1],   a (possibly imprecise) probability measure over world-models.

Because Ω is astronomically large and structured, B_t is represented *factorized*
over propositions and causal edges. For a proposition p (a statement about ω, e.g.
"invoice reconciliation is performed by manual re-keying"), belief is the marginal
`B_t(p) = ∫_{ω ⊨ p} dB_t(ω)`.

We insist on two departures from the incumbent scalar "confidence":

1. **Second-order uncertainty.** We track not only `B_t(p)` (the probability) but
   the *stability* of that probability — whether it rests on thick, corroborated
   evidence or a single thin utterance. Formally we carry a distribution over the
   probability, or, where evidence is too sparse for a sharp prior, a **credal set**
   (an interval or set of measures) after imprecise-probability theory. This lets us
   separate **risk** ("a well-estimated coin flip") from **ambiguity** ("we simply
   do not know") — a distinction (Knight; Ellsberg) that a scalar confidence
   collapses and that consultants desperately need.
2. **The belief graph replaces the knowledge graph.** Nodes and edges do not assert
   facts; they carry belief measures and decay parameters. An edge is a
   *hypothesis with a posterior*, not an asserted relation. The "one graph" survives
   the reframing — but as a **probabilistic graphical model**, not an assertion
   store.

> **Deletion.** The scalar `Confidence` with six hand-chosen factors is discarded.
> It conflated risk with ambiguity, had no calculus of combination, and could not be
> made decision-relative. It is replaced by (first-order belief, second-order
> stability, credal width).

---

## 5. The testimony likelihood and belief update (Construct 3)

Here is the load-bearing idea the incumbent architecture is missing. An observation
o (an utterance, a document line) is not evidence about ω. It is evidence about ω
*as filtered through an observer*. We posit a two-stage generative model:

    o  ~  Express( Perceive(ω, s) , c )

where **s** is the observer's *standpoint* (their observational access — what their
role lets them see) and **c** is their *candor/incentive state* (how faithfully they
report what they perceive, given fear, politics, and self-image). This yields the
**testimony likelihood**:

    P(o | ω, s, c)  =  perception filter (ω → what they see)  ∘
                       expression filter (what they see → what they say).

Belief update is Bayesian inversion of this likelihood:

    B_{t+1}(ω) ∝ B_t(ω) · P(o_{t+1} | ω, ŝ, ĉ)

with the observer parameters (ŝ, ĉ) *jointly inferred*, not assumed. A department
head describing their own workflow has a favorable standpoint; the same person
describing another team's is nearly blind. A frightened junior "reporting" a
process is emitting mostly expression-filter, little signal.

> **Principle (Testimony, not evidence).** The immutable transcript segment is
> evidence about (ω, s, c) *jointly*. Treating it as evidence about ω directly —
> the incumbent "evidence-first" stance — is a conflation that imports the speaker's
> distortion into the belief as if it were the world. **Provenance is preserved;
> presumed veracity is deleted.** We know exactly who said what, and we no longer
> pretend that what they said is what is true.

The espoused/enacted gap (A2) is now formal: the *espoused* register is
high-expression-filter testimony about the official ω; the *enacted* register is
lower-filter testimony about the real ω. The engine actively seeks to lower the
expression filter (this is precisely the interview engine's candor problem, §13 of
that document) and to weight the enacted register above the espoused.

---

## 6. Evidence accumulation (Construct 4)

Evidence does not accumulate by *counting*. It accumulates as **log-likelihood-ratio
(Bayes-factor) contributions**, each discounted by two factors the incumbent model
ignores:

    weight of o for p  ≈  log[ P(o | p) / P(o | ¬p) ]  ×  independence(o)  ×  decay(age of o)

- **Independence.** Two informants who both read the same wiki page, or both repeat
  the same rumor, are *not* independent evidence; their shared source must be
  factored out or their corroboration double-counts (the classic failure of naive
  likelihood products). We therefore model a **source-dependence structure** among
  observers and pool accordingly. Corroboration from *independent standpoints* is
  worth orders of magnitude more than repetition through a single rumor mill.
- **Decay** (§11) — old evidence is weaker evidence about a moving target.

> **Corollary.** The most valuable next observation is not the one that confirms the
> leading hypothesis but the one from the *least-correlated standpoint* — the
> observer whose vantage is most independent of everyone heard so far. This is a
> formal justification, from the epistemology, for *who* the interview engine should
> talk to next.

---

## 7. Multi-interview belief fusion (Construct 11)

Fusing testimony across informants is **supra-Bayesian aggregation of perspectival
observations**, not opinion averaging. Each informant i contributes a likelihood
`P(o_i | ω, s_i, c_i)`; the posterior is their correlation-aware product against the
prior. Three properties are non-negotiable:

1. **Standpoint weighting.** An informant's contribution to belief about p is
   weighted by how well s_i observes the slice of ω that p concerns. A CFO is a poor
   witness to shop-floor rework; a shop-floor operator is a poor witness to capital
   allocation.
2. **Correlation-awareness.** Shared culture, shared documents, and shared rumor
   induce dependence; the fusion discounts redundant vantage (§6).
3. **Role-bias correction.** Systematic, role-conditioned distortions (sales
   optimism, engineering pessimism, managerial self-service) are *learned* (§15) and
   subtracted, not naively believed.

The output of fusion is not a consensus point but a **posterior with structured
residual disagreement** — which is itself the input to contradiction management.

---

## 8. Contradiction management (Construct 5)

Disagreement is a first-class object of knowledge, not an error to be resolved. When
two informants diverge on p, we classify by comparing their standpoints:

- **Epistemic conflict** — their standpoints *should* agree (they observe the same
  slice) yet they diverge. This is genuine uncertainty; seek an independent
  tie-breaker.
- **Ontic variation** — the process genuinely differs across people, units, or time.
  The disagreement is not noise; it *is* a true proposition: *"p is
  non-standardized."* We **promote the disagreement to a belief** about the
  organization's coherence. Non-standardization, fragmentation, and unclear
  ownership are discovered here — and they are among the most valuable findings a
  consultant can receive.
- **Perspectival complementarity** — their standpoints observe different slices and
  are both right; fuse into a richer ω.

> **Definition (Coherence field).** Over each proposition and process, we maintain a
> measure of *how consistently* the organization enacts it across standpoints. Low
> coherence is not low confidence — it is high-confidence knowledge that the
> organization is internally inconsistent. The incumbent "reconcile-error vs
> capture-signal" heuristic is the shadow of this construct; we make it the object.

The "official vs discovered drift" of the incumbent architecture is re-derived here
as a *special case*: two posteriors over the same ω conditioned on different evidence
sources — declared documents (high espousal) versus enacted testimony. Drift is the
**KL divergence** between these conditioned posteriors, and the valuable question is
never *that* they diverge but *why* — which the coherence field answers and a
fact-versus-fact comparison cannot.

---

## 9. Uncertainty propagation (Construct 6)

Beliefs about *derived* propositions — bottlenecks, opportunities, recommendations —
are functionals of primitive beliefs, composed through the inference and causal
graph. Uncertainty must propagate through that composition, at both orders:

- **First-order** propagation gives the probability of a derived claim.
- **Second-order** propagation gives its *stability* — a bottleneck inferred from a
  long chain of thin, correlated testimony must arrive *fragile*, and be reported as
  such.

Where evidence is thin, we propagate **credal sets** (interval bounds) rather than
sharp probabilities, so that "we don't yet know" survives all the way to the
consultant instead of being laundered into a false point estimate. The cardinal sin
— committed by any system that reports a single number — is **spurious precision**:
presenting ambiguity in the costume of risk.

---

## 10. Causal graph evolution (Construct 12)

Organizational knowledge is ultimately *causal* — a consultant does not want to know
that re-keying and delay co-occur; they want to know that automating re-keying would
*reduce* delay, i.e. `P(delay | do(automate))`. But interviews yield observational,
confounded testimony. We therefore treat the causal structure as *learned and
progressively upgraded* through five tiers of increasing warrant:

1. **Correlational** — co-occurrence in testimony.
2. **Temporal** — reported precedence ("first X, then Y").
3. **Mechanistic** — testimony of a mechanism ("Y happens *because* X").
4. **Quasi-experimental** — natural variation across units (a team that lacks X and
   also lacks Y).
5. **Interventional (gold standard)** — a client acts on a recommendation and we
   *observe the outcome*. This is the only tier that licenses `do`-calculus claims,
   and it is where Groundwork's causal knowledge becomes genuinely scientific.

> **Reflexivity (A5) formalized.** Because Groundwork's outputs intervene, the world
> model must distinguish `P(y | x)` (observational) from `P(y | do(x))`
> (interventional), and must anticipate Goodhart: once a metric is surfaced, the
> behavior generating it changes. Tier-5 updates are thus not free observations but
> *controlled perturbations of a system that reacts to being measured* — the deepest
> and most defensible knowledge Groundwork can accumulate, and the one no competitor
> without deployed clients can obtain.

---

## 11. Belief decay and organizational thermodynamics (Construct 8)

Between observations, belief must relax toward ignorance, because the world moves
(A4). We posit a decay dynamics per proposition class:

    dB/dt = −λ_p · ( B_t − Π_p )

where Π_p is the (population-level) prior and λ_p is a class-specific decay rate,
giving each proposition a **half-life** τ_p = ln2 / λ_p. Reporting lines decay over
quarters; this week's workaround decays over weeks; a stated strategic priority
somewhere between. As B relaxes toward Π, second-order uncertainty widens: old
beliefs don't just become wrong, they become *known-to-be-stale*.

> **Consequence (perishability ⇒ the product).** Organizational knowledge is not a
> library; it is a *perishable estimate*. This is a formal argument that Groundwork must
> be continuous, not a one-shot audit — and, incidentally, the epistemic
> justification for a subscription. A competitor selling a static report is selling a
> decaying asset and does not know it.

---

## 12. Organizational memory (Construct 7)

Memory is the persistent, decaying posterior — but stratified into three stores with
different dynamics, by analogy to human memory:

- **Episodic** — specific, timestamped testimonies. High fidelity, fast decay,
  perfect provenance. The audit trail.
- **Semantic** — consolidated beliefs about how the organization works, distilled
  from many episodes. Slower decay. The working model.
- **Meta** — the *learned models themselves*: testimony likelihoods, role biases,
  decay rates, causal priors, consultant reliabilities (§15). **This store does not
  decay; it compounds.**

Consolidation (episodic → semantic) is an explicit operation, and **forgetting is
adaptive**: decay is a feature that prevents stale, over-counted testimony from
dominating the present. A system that cannot forget cannot track a moving target.

---

## 13. Consultant-guided Bayesian updating (Construct 10)

The consultant is neither an oracle (as the incumbent architecture assumes) nor a
mere user. The consultant is a **high-precision, domain-expert, fallible observer**,
and enters the formalism as an observation with its own likelihood
`P(validation | ω, consultant-model)` of high but finite precision. Three roles
follow:

1. **Strong likelihood, not certainty.** A consultant's confirmation sharply
   concentrates belief but never sets it to 1. Contradicting evidence can still
   move it. This deletes "validated ⇒ authoritative truth."
2. **Active-learning oracle under a query budget.** The system does not ask the
   consultant to review everything; it *queries* them where the **value of
   information is highest** — the beliefs whose resolution most changes a pending
   decision (§14). The consultant's scarce attention is spent by the estimator, not
   the interface.
3. **Reliability learning.** The consultant's own calibration is estimated over
   time; a consultant who is systematically wrong about a class of judgments is
   down-weighted on that class. Groundwork learns *how much to trust its expert* — a
   capability no static tool possesses.

---

## 14. Economic decision confidence (Construct 13)

There is no such thing as confidence in the abstract. Confidence is always *relative
to a decision* and its loss function (A6). For a decision d with actions, outcomes,
and costs, define **decision-sufficient belief**: belief about the relevant
propositions is sufficient for d when the *expected value of further information is
less than its cost* — the optimal-stopping criterion of sequential experimental
design.

Groundwork therefore does not report "we are 80% sure." It reports, per decision:

> *"Belief is sufficient to recommend automating invoice reconciliation (the decision
> boundary is far from our credal interval); it is **not** sufficient to recommend
> restructuring the finance department (the boundary lies inside our interval — we
> would need k more independent standpoints, at cost c, to resolve it)."*

This inverts the product. The deliverable is not a graph of beliefs but a set of
**decisions ranked by whether we yet know enough to make them** — and, for those we
don't, the *cheapest path to sufficiency*. It also closes the loop with the interview
engine: the value of the next interview is the reduction it buys in *decision-relevant*
uncertainty, priced against its cost.

---

## 15. Organizational learning: hierarchical cross-client priors (Construct 9)

The slow loop does not learn facts about one client. It learns the **models**: the
testimony likelihoods (how each role distorts), the decay rates, the causal priors,
the consultant reliabilities. And it learns them **hierarchically across all
clients**, treating each engagement as one draw from a population of organizations
(empirical Bayes / hierarchical Bayes).

> **Definition (The population prior).** Π is a distribution over organizational
> world-models and their testimony dynamics, estimated across every engagement
> Groundwork has ever run. Each new client is initialized from Π — and updated back into
> it.

This is the entire defensibility thesis. A competitor can rent the same language
model. They cannot rent Π. Π is the compounded, validation-anchored knowledge of
*how organizations of this kind actually work and how their members actually
distort* — a prior that makes each new engagement's cold-start sharper, each new
interview shorter, each new inference stronger. The data does not compound; beliefs
decay (§11). **Π compounds.** The moat is not information; it is the learned
epistemology itself.

---

## 16. What we delete or reframe from the incumbent architecture

Bluntly, and without defense of prior work:

- **DELETE: evidence ⇒ truth.** The immutable-evidence spine guarantees provenance,
  not veracity. Keep the provenance; delete the presumed veracity. Evidence is
  testimony about (ω, s, c). (§5)
- **DELETE: scalar six-factor confidence.** Replace with (first-order belief,
  second-order stability, credal width), and make it decision-relative. (§4, §14)
- **DELETE: consultant validation ⇒ authoritative truth.** Replace with the
  consultant as a high-precision, calibratable, fallible observer. (§13)
- **REFRAME: the knowledge graph** as a probabilistic belief graph whose edges carry
  posteriors and decay, not asserted relations. (§4)
- **REFRAME: official-vs-discovered drift** as KL divergence between posteriors
  conditioned on different evidence sources — a special case of the coherence field,
  where the interesting object is *why* they diverge. (§8)
- **REFRAME: permanent storage** as decaying memory with adaptive forgetting; static
  storage of belief violates non-stationarity. (§11, §12)
- **ADD:** the testimony likelihood, the standpoint model, belief decay, causal
  upgrading, decision-sufficiency, and the hierarchical population prior — the six
  constructs without which the platform is a database with good manners.

---

## 17. The five-year research agenda (open problems)

These are hard and, in several cases, unsolved anywhere.

1. **Identifiability of (ω, s, c).** Can we separate world, standpoint, and candor
   from testimony alone, or do we need exogenous anchors (documents, observed
   outcomes)? Where is the model unidentifiable, and how do we bound it?
2. **Learning the testimony likelihood at scale.** Estimating role- and
   culture-conditioned distortion functions from validated outcomes is the crux of
   the moat and largely uncharted.
3. **Tractable belief over Ω.** Ω is enormous and structured. What factorizations
   and variational approximations keep inference tractable without amputating the
   causal structure?
4. **Calibrated second-order uncertainty.** Producing credal intervals that a
   consultant can trust — neither overconfident nor uselessly wide — under thin
   evidence.
5. **Causal upgrading from deployment.** Turning client interventions into valid
   `do`-calculus updates under confounding, selection, and Goodhart reactivity.
6. **The reflexivity control problem.** Modeling, and ideally exploiting, the fact
   that surfacing beliefs changes the organization. Can Groundwork recommend
   interventions that are robust to their own announcement?
7. **Decision-sufficiency under vague loss.** Clients often cannot state a loss
   function. How do we elicit "sure enough for what?" when the decision itself is
   fuzzy?
8. **Prior transfer without contamination.** Sharing Π across clients while
   guaranteeing that no client's confidential specifics leak — privacy-preserving
   hierarchical inference.

---

## 18. Conclusion

Groundwork's purpose is to *continuously approach organizational truth* — a target that
is latent, perspectival, non-stationary, reflexive, and reachable only through
fallible testimony. The right foundation is therefore not a store of facts but an
**estimator**: a Bayesian filter over a moving latent process, driven by a *learned
model of how humans testify*, reporting *decision-sufficient* beliefs, and
compounding its power in a **cross-client population prior** that no competitor can
rent.

The incumbent architecture built a beautiful place to keep answers. This paper
argues that Groundwork's real work — and its only durable moat — is the disciplined,
humble, and relentless business of *estimating answers it can never be certain of,
about a world that will not hold still, from people who cannot fully see it and will
not fully say it.* That is a harder problem than storage. It is also the only one
worth owning.
