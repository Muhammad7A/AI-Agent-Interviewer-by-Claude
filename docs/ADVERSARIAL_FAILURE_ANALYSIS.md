# Ontora — Adversarial Failure Analysis

> Every meaningful way this company, product, system, and research program can die.
> Reasoned from the whole repository as one object. Not theoretical failures, not
> "the market is competitive." Concrete, specific, ruthless. The goal is to find the
> landmines before the first customer does.

---

## 0. The two meta-patterns that generate most of the risk

Before the list, two shapes that recur everywhere:

- **Conjunctive success.** Ontora's value requires a long chain of *independent*
  things to all be true: employees are candid → the interview elicits truth →
  extraction doesn't confabulate → findings are *decision-useful*, not merely true →
  consultants validate without rubber-stamping → executives act → outcomes are good →
  it's legal → someone pays enough. If each link is 70% likely, the joint is **~6%.**
  The company is an AND of fragile clauses, and most failure modes below are just "one
  clause broke."
- **Demo–production inversion.** Every part of this system looks *best* under exactly
  the conditions production won't have: cooperative role-players, cherry-picked rich
  transcripts, a careful founder-as-consultant, small cherry-picked N, and no legal
  review. The system is engineered to be seductive in a demo and brittle in reality.

Hold these two in mind; they explain why the "silent killers" (§4) are silent.

---

## 1. Failure-mode taxonomy

Six families across the 20 required dimensions.

- **A · Truth-acquisition** — *can we get truth at all?* Interview, cognitive,
  epistemic, employee-candor.
- **B · Truth-delivery** — *does truth become useful?* Product, consultant workflow,
  UX, customer-trust, value-density.
- **C · Commercial** — *does it make money?* GTM, pricing, unit economics, moat,
  competitive.
- **D · Trust & legal** — *will they let us and believe us?* Anonymity, legal/compliance,
  organizational adoption.
- **E · Learning & measurement** — *can we improve and prove it?* Evaluation, learning
  loop, dataset.
- **F · Team** — *will we do the right work?* Founder, execution.

Severity key: **FATAL** (kills the company) · **SEVERE** (can kill; must be actively
managed) · **RECOVERABLE** (painful, survivable). Nature: *structural* (won't yield to
effort) · *research* (genuine scientific uncertainty) · *engineering* (buildable fix) ·
*behavioral* (about the humans).

---

## 2. The top 20 failure modes, ranked by lethality

Ranked by (probability × severity × how-late-you-find-out).

**F1 · Employee candor is structurally, not technically, capped.** — FATAL ·
structural + research
- *What:* Employees won't tell a corporate-procured AI the truth about their managers,
  their workarounds, or the real dysfunction — because attribution risk to their career
  is real and rational, no matter what the prompt says.
- *Why it matters:* It's the first link in the chain. No candor → shallow transcripts →
  nothing downstream can recover.
- *Manifests as:* Polite, socially-safe, generic answers; the juicy truth withheld;
  findings that any survey would have produced.
- *Hard to notice early because:* Friendly design-partner employees (recruited by a
  sponsor, wanting to help) are *more* candid than a random skeptical workforce; early
  pilots overstate candor.
- *Cheapest detection:* Run 15-20 interviews at a *non-friendly* company; blind-compare
  what the AI got vs. an anonymous survey vs. a skilled human interviewer on the same
  people. Measure *hidden-truth recovery*, not answer volume.
- *Mitigation that helps:* Third-party-consultant confidentiality (real), radical
  transparency about what's shared, projective questioning — but the incentive core may
  be unfixable. This is the one to test first and hardest.

**F2 · "Interesting" ≠ "commercially useful."** — FATAL · structural
- *What:* The engine produces findings that are true and even non-obvious but do not
  *change a decision* ("communication could be better," "there's some duplication").
- *Why it matters:* The product can work perfectly and be worthless. Nobody pays for
  true trivia.
- *Manifests as:* Consultants nod, executives say "interesting," nothing changes, no
  renewal.
- *Hard to notice early because:* Consultants are *polite* — they rate findings "useful"
  to be nice; only decision-tracking reveals the truth, and that's slow.
- *Cheapest detection:* Show real findings to 3 real executives; ask not "is this true?"
  but "would you spend money or change a plan because of this?" Count the yeses.
- *Mitigation:* Bias the whole engine toward *specific, leverable, quantified* findings;
  kill horoscopes at synthesis. But if the *only* findings available are un-actionable,
  no filter helps.

**F3 · The anonymity paradox.** — SEVERE→FATAL · structural
- *What:* Candor requires anonymity; executive credibility requires sourcing. The two
  directly conflict.
- *Why it matters:* Solve for candor and the exec dismisses an "unsourced accusation
  about the finance department"; solve for sourcing and employees clam up.
- *Manifests as:* Either thin data or un-actioned reports; the exec asks "who said
  that?" and there's no acceptable answer.
- *Hard to notice early because:* With cooperative pilots you get *both* enough candor
  *and* enough trust to fake a resolution; the tension only bites with guarded employees
  and skeptical execs.
- *Cheapest detection:* Show an aggregate finding ("7 of 9 in finance, independently") to
  a real exec and measure whether "aggregate + N-of-M" is credible *enough to act* —
  without any names.
- *Mitigation:* The consultant-as-confidential-third-party + statistical aggregate
  sourcing is the only real lever, and it's partial. If N is small (guarded workforce),
  "7 of 9" becomes "3 of 4" and credibility collapses.

**F4 · Confabulation / hallucinated insight.** — SEVERE · engineering (mostly)
- *What:* The model asserts findings the transcript doesn't support — invented
  contradictions, mechanisms, quantities.
- *Why it matters:* One fabricated finding about a *named* department is a
  trust-and-legal grenade; it burns the referral that sells the company.
- *Manifests as:* A confident, well-worded finding whose "evidence" quote doesn't
  actually say it.
- *Hard to notice early because:* It's *plausible* and *fluent*; a rubber-stamping
  consultant (F6) waves it through, and on cherry-picked rich transcripts it's rarer.
- *Cheapest detection:* Blind-score every AI finding for quote→claim entailment on real
  transcripts. Report the confabulation rate. (Eval harness gate: >5% = fail.)
- *Mitigation:* Verbatim-quote-or-delete at synthesis; the low-signal-dud test; a hard
  eval gate. Tractable — but never zero, and the tolerable rate for legal exposure is
  brutally low.

**F5 · Legal / compliance blockade.** — SEVERE→FATAL · structural
- *What:* EU works councils veto employee interviews; GDPR governs the testimony;
  transcripts of employees describing dysfunction are *discoverable in litigation*;
  unsourced criticism of a named manager is *defamation-adjacent*; harassment
  disclosures create duty-of-care.
- *Why it matters:* Kills the EU outright, slows the US, and the GC can block the pilot
  before interview one.
- *Manifests as:* The deal dies in legal review; or worse, a stored transcript surfaces
  in a wrongful-termination suit.
- *Hard to notice early because:* Founder-network pilots skip formal legal review; the
  landmine detonates at the first enterprise procurement, not the first friendly logo.
- *Cheapest detection:* One hour with one real GC and one EU works-council rep. Ask:
  "would you approve this, and what would it take?"
- *Mitigation:* Data-minimization, retention limits, aggregate-only outputs, jurisdiction
  scoping — real but limiting. The discovery-liability problem is *structural*: you're
  manufacturing a corpus of employees describing organizational wrongdoing.

**F6 · Consultant rubber-stamping.** — SEVERE · behavioral
- *What:* To capture the promised time saving, the consultant batch-accepts findings
  without inspecting evidence — and ships the AI's errors as their own judgment.
- *Why it matters:* It converts the AI's confabulations (F4) directly into client-facing
  claims, *and* it means the consultant isn't actually adding the judgment the workflow
  assumes.
- *Manifests as:* High accept rates, near-zero evidence drill-downs, low edit distance —
  which looks like *success* ("the AI is great!") but is *abdication*.
- *Hard to notice early because:* It looks identical to a good result. High acceptance
  reads as high quality until a wrong finding blows up in front of a client.
- *Cheapest detection:* Instrument the review: measure accept-without-inspecting rate and
  evidence-open rate. If they accept without opening evidence, that's the failure, even
  if outcomes seem fine.
- *Mitigation:* The editing-by-exception UI must *force* attention on low-confidence /
  contested items and make blind-accept feel wrong — but the incentive (save time) pushes
  the other way. The very feature that saves time (triage) enables the failure.

**F7 · Executive distrust of unsourced aggregate findings.** — SEVERE · structural
- *What:* Execs won't bet a reorg on "an AI interviewed people and concluded X" that they
  can't verify.
- *Why it matters:* No action → no value → no renewal, regardless of accuracy.
- *Manifests as:* "Interesting, we'll consider it," then nothing.
- *Hard to notice early because:* In a demo the exec is impressed by the *artifact*;
  whether they *act* is invisible until weeks later.
- *Cheapest detection:* Decision-impact tracking on 3 real engagements — did one decision
  change?
- *Mitigation:* Evidence drill-down, N-of-M, the honesty box, and the *consultant's*
  personal credibility carrying it. Ontora as the notebook, the consultant as the face.

**F8 · Leading-question confirmation (the engine manufactures its findings).** — SEVERE
· engineering
- *What:* A *hypothesis-driven* interviewer is at high risk of *planting* the answer it
  went looking for; the "finding" is an artifact of the question.
- *Why it matters:* It produces confident, evidenced-looking findings that are actually
  the interviewer's prior reflected back. Worse than confabulation because the quote
  *does* support it — the respondent was led to say it.
- *Manifests as:* Suspiciously clean confirmation of the seeded hypotheses; the belief
  state only ever gains support.
- *Hard to notice early because:* The evidence check passes (the quote is real); only a
  human auditing the *questions* catches it.
- *Cheapest detection:* Score interview transcripts for leading-question rate and
  hypothesis-confirmation-without-disconfirmation. (Eval gate: leading >10% = fail.)
- *Mitigation:* The disconfirmation-preference and self-audit prompts — but a
  hypothesis-driven design is *inherently* prone to this, so it must be measured
  continuously, not assumed away.

**F9 · Conjunctive-success fragility.** — FATAL · structural
- *What:* Too many independent things must all work (see §0).
- *Why it matters:* Even competent execution on every front yields a low joint success
  probability.
- *Manifests as:* "Everything is going fine" on each individual axis, yet the company
  never reaches escape velocity because one weak link caps the whole product.
- *Hard to notice early because:* You test links in isolation (each looks okay) and never
  the full chain end-to-end on a real cold customer.
- *Cheapest detection:* Run *one* full engagement end-to-end at a *non-friendly* company
  and measure the *joint* outcome (did an exec act on a true, legally-clean, candor-
  sourced finding), not the parts.
- *Mitigation:* Narrow the wedge so fewer links must hold at once; kill the links you
  can't make reliable (e.g., drop the ambitious "recover the whole org" for "surface
  friction in one function").

**F10 · Weak value density (verbose, low-yield).** — SEVERE · engineering/product
- *What:* The system produces volume — long interviews, many findings — with little
  decision-useful truth per unit of consultant/exec attention.
- *Why it matters:* It *feels* substantial and *is* empty; it fails the "beats a survey +
  Celonis" bar.
- *Manifests as:* 20 findings, 2 that matter, and the consultant has to dig for the 2.
- *Hard to notice early because:* Length and polish read as thoroughness; nobody measures
  value-per-token in a demo.
- *Cheapest detection:* Value-density metric on real engagements: decision-useful findings
  ÷ (interview minutes + review minutes). Compare to a survey baseline.
- *Mitigation:* Rank hard, cap findings, penalize length in eval — but if the raw signal
  is thin (F1), density can't be manufactured.

**F11 · Miscalibrated confidence → false trust.** — SEVERE · engineering
- *What:* "High confidence" findings are wrong at a rate that doesn't match the label.
- *Why it matters:* The triage workflow (F6) *trusts* the labels; miscalibration means
  the consultant skips exactly the findings they should scrutinize. Miscalibration
  amplifies through the whole system.
- *Manifests as:* Confident findings that don't survive scrutiny; the honesty box lies.
- *Hard to notice early because:* Calibration only reveals at scale (small N looks fine);
  a handful of confident-and-right findings in a demo prove nothing.
- *Cheapest detection:* Reliability diagram / ECE against ground truth on synthetic
  scenarios + retrospective outcomes. (Eval gate: ECE >0.15 = fail.)
- *Mitigation:* Calibrate against the synthetic truth set and retrospective outcomes;
  report credal width, not just a band.

**F12 · Digital-exhaust / Microsoft obsolescence.** — SEVERE · competitive-structural
- *What:* The enacted reality of work already lives in Slack/email/tickets/calendars;
  LLMs over that exhaust (or Microsoft over Graph) reconstruct "how work flows" *without
  interviews*.
- *Why it matters:* The interview becomes an expensive, high-friction workaround for
  missing data pipes — and Microsoft has the pipes *and* the distribution.
- *Manifests as:* A well-funded incumbent ships a "good enough" org-intelligence feature
  bundled at ~$0; Ontora's wedge evaporates.
- *Hard to notice early because:* It's a *future* shift; today interviews clearly capture
  tacit knowledge exhaust doesn't. You feel safe right up until you're not.
- *Cheapest detection:* Run the interview *and* a light exhaust analysis on the same org;
  measure how much unique, decision-useful signal the interview adds over exhaust. If
  it's small, the moat is already gone.
- *Mitigation:* Own the *tacit* layer (fear, workarounds, why) exhaust can't reach — and
  hybridize (interview + exhaust) rather than interview-only.

**F13 · GTM: no repeatable acquisition + procurement wall.** — SEVERE · behavioral/
structural
- *What:* Founder network yields 2-3 logos, then a wall of 12-18-month enterprise
  procurement, security, and legal review.
- *Why it matters:* A pre-seed startup can't survive the sales cycle; cash runs out
  before repeatable revenue.
- *Manifests as:* Two warm pilots, then months of "we're evaluating."
- *Hard to notice early because:* The warm pilots feel like traction and mask the absence
  of a repeatable motion.
- *Cheapest detection:* After the warm intros, cold-start *one* net-new logo and time it.
- *Mitigation:* A narrow, fast-lane wedge with a champion who can buy without a
  12-month cycle; land via a friendly consultancy or a burning-need CIO.

**F14 · The moat never compounds.** — SEVERE · structural
- *What:* Model rented, prompt copyable, graph commodity; the only candidate moats
  (validated-outcome data, trust, the cross-client prior Π) are slow, services-heavy,
  and partly illegal.
- *Why it matters:* Without a moat, a giant with distribution wins once the category is
  proven.
- *Manifests as:* Growth, then a fast-follower with more data/distribution eats it.
- *Hard to notice early because:* Moats are invisible until attacked; you feel
  differentiated for two years, then discover you weren't.
- *Cheapest detection:* Ask, brutally, "what do we have after 20 engagements that a
  funded competitor couldn't get in 6 months?" If the honest answer is "nothing yet,"
  that's the finding.
- *Mitigation:* Concentrate on the *validated-outcome dataset* and forward-deployed
  trust — the only moats a giant can't shortcut — and make Π legal (aggregate, DP,
  consented) or abandon it.

**F15 · Founders build instead of sell.** — SEVERE · behavioral
- *What:* Brilliant engineers who respond to every "no" with another abstraction (they
  wrote an epistemology and six contexts before one customer).
- *Why it matters:* The company dies with a beautiful system and no revenue.
- *Manifests as:* A seventh document instead of a fortieth interview.
- *Hard to notice early because:* Output *looks* like progress; the repository grows.
- *Cheapest detection:* Count, this month, real customer conversations vs. artifacts
  produced. If the ratio is inverted, that's the failure.
- *Mitigation:* Hard external forcing functions (a board, a coach, a co-founder) toward
  customers; delete the platform; first hire commercial, not engineering.

**F16 · Identifiability / plural truth (the deep vision is under-determined).** —
FATAL-to-the-ambitious-version · research
- *What:* You can't separate the world from the speaker's distortion (ω, s, c) from
  testimony alone; and organizational truth may be irreducibly *plural* — no single ω to
  recover.
- *Why it matters:* The grand "recover organizational reality / detect drift" vision may
  be mathematically impossible; only the modest "elicit and surface friction" version
  survives.
- *Manifests as:* Confident single-truth outputs that are actually one standpoint, or a
  drift engine comparing against a phantom.
- *Hard to notice early because:* It's a *research* result, not a bug; the modest version
  works well enough to hide the impossibility of the ambitious one.
- *Cheapest detection:* On a synthetic org with a *known* ω and conflicting standpoints,
  test whether the engine recovers ω or just averages perspectives. Cheap and decisive.
- *Mitigation:* Scope to the identifiable problem (surface friction, model disagreement)
  and *delete* the parts that assume recoverable single truth (Drift, official-vs-
  discovered as fact-vs-fact).

**F17 · Organizational adoption sabotage → low N.** — SEVERE · structural
- *What:* The middle manager whose dysfunction the tool would expose tanks participation
  — tells the team not to bother, doesn't endorse it.
- *Why it matters:* Low N → weak, anecdotal findings → dismissal; and the *most
  dysfunctional* units (highest value) are the ones most motivated to sabotage.
- *Manifests as:* "Low participation," root cause hidden as apathy rather than
  suppression.
- *Hard to notice early because:* It's attributed to generic "engagement" problems, not
  to the political immune response it actually is.
- *Cheapest detection:* Correlate participation rate with the sponsor's level and the
  unit's suspected dysfunction; sabotage shows as suppressed participation exactly where
  the value is.
- *Mitigation:* Top-down sponsorship, credible independence, employee-visible benefit —
  but the incentive to suppress is real and structural.

**F18 · Learning loop trains flattery / never compounds.** — SEVERE · research +
engineering
- *What:* The reward signal (consultant validation) trains the engine to *please
  consultants*, not to be right; and the gold signal (outcomes) is too sparse/delayed to
  train on; credit assignment across question→outcome is too noisy to converge.
- *Why it matters:* The compounding-moat thesis rests entirely on this loop working; if
  it optimizes flattery or never converges, there's no moat.
- *Manifests as:* Rising acceptance rates, falling truth; or simply no measurable
  improvement per version.
- *Hard to notice early because:* It takes many cycles and real outcome data to see; by
  then you've built the whole apparatus.
- *Cheapest detection:* Keep a frozen, consultant-independent ground-truth set; watch
  whether acceptance rises while independent accuracy stalls (the flattery signature).
- *Mitigation:* Anchor to the frozen set; weight sparse outcome signal heavily; accept
  that this is a research bet, not an engineering certainty.

**F19 · Unit economics: the services drag.** — SEVERE · structural
- *What:* Org intelligence can't be sold self-serve; forward-deployed services cap
  margin and growth; per-engagement AI cost (many transcripts × the belief-state loop ×
  the decomposed pipeline) can be non-trivial.
- *Why it matters:* It's a consultancy wearing a SaaS costume — low margin, non-
  recurring, hard to scale, VC-unfriendly.
- *Manifests as:* Every engagement needs a founder in the room; revenue doesn't
  compound.
- *Hard to notice early because:* At 3 forward-deployed logos it feels fine; the drag
  appears when you try to 10x without 10x-ing the team.
- *Cheapest detection:* Measure the human hours *you* spend per engagement; if it's not
  falling engagement over engagement, it doesn't scale.
- *Mitigation:* Ruthlessly productize the repeatable 80%; keep the AI cost down (minimal
  prompt pipeline, not the advanced one, until proven).

**F20 · Evaluation is unsound (synthetic-to-real gap + LLM-judge circularity).** —
SEVERE · methodological
- *What:* Real interviews have no ground truth, so the eval leans on synthetic (may not
  transfer) and LLM-judges (the interviewer learns to please them) and fallible
  consultants (low inter-rater agreement).
- *Why it matters:* You could pass your own benchmark and still be bad — the worst kind
  of blindness, because it feels like rigor.
- *Manifests as:* Great eval scores, poor real-world engagements.
- *Hard to notice early because:* A passing benchmark *is* the thing that hides it.
- *Cheapest detection:* Correlate benchmark scores against a *handful of real outcomes*;
  if they diverge, the benchmark is measuring the wrong thing.
- *Mitigation:* Human-anchored gates, cross-family judges, a synthetic-vs-real transfer
  check, and never trusting the benchmark over a real burned engagement.

---

## 3. (embedded above) — severity + nature are tagged per item.

---

## 4. Top 10 silent killers (great in demos, dead in production)

1. **Candor looks solved** because pilot employees are friendly (F1).
2. **Extraction looks great** on hand-picked rich transcripts; production is thin and
   messy (F4/F10).
3. **The consultant validates carefully** — because it's the founder; the real consultant
   rubber-stamps (F6).
4. **Confidence looks calibrated** on small cherry-picked N; miscalibration only shows at
   scale (F11).
5. **The report looks like $50k of consulting**; whether the exec *acts* is invisible in a
   demo (F2/F7).
6. **Contradiction detection looks insightful** on a scripted contradiction; over-fires on
   real noise (F4/F8).
7. **"7 of 9 people said this"** is credible with 9 cooperative people; real engagements
   get 4 guarded ones (F3).
8. **The synthetic eval passes**; the synthetic-to-real gap is invisible until deployment
   (F20).
9. **"It improves over time"** — unmeasurable in a demo, may never compound (F18).
10. **The interview feels magical** because the demo employee *wanted* to be interviewed;
    the sabotaging middle manager isn't in the room (F17).

Every one of these makes the *demo* better and the *company* worse. Distrust anything that
only shows up in a demo.

---

## 5. Top 10 cheapest to test in the next 30 days (do these before anything else)

1. **F1 candor** — 15-20 real interviews at a non-friendly org; hidden-truth recovery vs.
   survey vs. human. *The single most important test in the company.*
2. **F4 confabulation** — blind quote→claim entailment scoring on real transcripts.
3. **F2 interesting-vs-useful** — 3 real execs: "would this change a decision?"
4. **F8 leading rate** — score real transcripts for leading + confirmation-without-
   disconfirmation.
5. **F6 rubber-stamping** — instrument 2 real consultants' review; accept-without-
   inspecting rate.
6. **F5 legal** — one GC + one works-council hour.
7. **F7 exec trust** — show an aggregate finding; "would you act without names?"
8. **F10 value density** — decision-useful findings ÷ attention-minutes vs. a survey.
9. **F17 adoption** — measure participation rate and correlate with unit dysfunction.
10. **F12 exhaust delta** — interview vs. light exhaust analysis on the same org; unique
    signal added.

Total cost: a few weeks and a few thousand dollars. Collectively they resolve most of the
existential uncertainty. *Not running them is itself a founder failure (F15).*

---

## 6. Top 10 hardest to detect until too late

1. **Miscalibration at scale** (F11) — fine on small N.
2. **Learning loop training flattery** (F18) — needs many cycles + outcomes.
3. **Candor selection bias** (F1) — you never see what guarded people *didn't* say; the
   false negatives are invisible.
4. **Synthetic-to-real eval gap** (F20) — the passing benchmark hides it.
5. **Cross-client confidentiality breach** (dataset) — surfaces as a lawsuit, not a
   metric.
6. **Slow-burn moat failure** (F14) — you feel differentiated for two years.
7. **Adoption sabotage misattributed to apathy** (F17).
8. **Interesting-but-useless masked by politeness** (F2) — only decision-tracking reveals
   it.
9. **Digital-exhaust obsolescence** (F12) — a competitive shift invisible until it's
   happened.
10. **Discovery-liability corpus** (F5) — harmless until the first lawsuit subpoenas your
    transcripts.

These share a signature: *no cheap in-the-moment signal.* They require ground truth,
time, scale, or an adversary to reveal. Build the instruments to catch them *now* (a
frozen truth set, decision-tracking, retention limits) or you learn them the expensive
way.

---

## 7. Failure modes that justify DELETING major parts of the architecture

- **If F1 (candor) or F2 (usefulness) fail:** delete almost everything speculative — the
  Drift/Assessment context, the Organization official model, identity resolution, the
  Insights synthesis layer, the six-context architecture, and *building* the
  epistemology. Keep a transcript store, a thin insight store, and the AI ports. The
  company would be a *different, smaller* thing, and 60-70% of the repo is dead weight.
- **If F16 (identifiability / plural truth) is confirmed:** delete the knowledge-graph-
  as-recoverable-truth and the official-vs-discovered drift comparison specifically —
  they assume a single recoverable ω that doesn't exist. Keep only elicit-and-surface +
  model-the-disagreement.
- **If F5 (legal) blocks the EU/enterprise:** delete the cross-client prior Π and the
  long-retention learning dataset in their current form; re-scope to aggregate-only,
  short-retention, jurisdiction-limited.

The through-line: the *speculative domain bets* (drift, official model, the ambitious
epistemology) are exactly what these failures delete. They were the over-built parts;
they're the first to go.

---

## 8. Failure modes that justify KEEPING the architecture mostly intact

- **If F1 + F4 + F2 pass** (candor real, low confabulation, findings useful): then the
  *mechanisms* — contracts-first discipline, ports/adapters for AI and storage, tenant
  isolation, evidence-first as a principle, the four-layer learning memory, the
  minimal prompt pipeline — are the right, cheap-to-change foundations. Keep them.
- **If F11 + F20 are manageable** (calibration and eval hold): the eval harness and the
  learning schema are worth their weight; keep and invest.

The mechanisms are sound and cheap to change; it's the *specific domain content* that's
at risk. Nothing in this analysis argues for re-architecting the *how*; it argues for
deleting speculative *what*.

---

## 9. Red-team memo — the true existential risks

Five reviews and one failure analysis now converge on the same small set. Stripped to
the bone, Ontora dies from one of **four** things, and only four:

1. **Candor (F1).** If a corporate-procured AI can't get employees to tell the truth,
   there is no data, no product, no company. *Structural + research. Testable in 30 days.
   Test it first or you're flying blind.*
2. **Usefulness (F2).** If the truth it gets is *interesting but doesn't change
   decisions*, it's true trivia nobody buys. *Structural. Testable with 3 execs.*
3. **Trust + legal (F3/F5/F7).** The anonymity paradox and the legal exposure of a
   corpus of employees describing dysfunction can each independently make the output
   un-actionable or un-deployable. *Structural. Partially testable now.*
4. **The founders (F15).** The single highest-probability cause of death is not any of
   the above — it's that the founders keep building beautiful systems (this document
   included) instead of running the four tests that would tell them whether 1-3 are
   fatal. *Behavioral. The most fixable and the most likely.*

Everything else on the list is severe-but-manageable *given* those four. Confabulation,
calibration, value density, GTM, moat, eval, unit economics — all are real, all are
survivable *if* candor is real, the output is useful, it's legal, and the founders face
the market. They are engineering and go-to-market problems. 1-4 are the existential
ones.

**The verdict is unchanged from every prior review and now over-determined:** the
company's fate is decided by four cheap experiments the founders have not yet run. The
most beautiful architecture in this repository is worth exactly nothing until F1 and F2
come back positive on real, unfriendly humans. **Stop writing. Go get the truth about
whether you can get the truth.**
