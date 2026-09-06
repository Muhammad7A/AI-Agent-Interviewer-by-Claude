# The 30-Day Candor Experiment

**Testing F1 — the top existential risk.** Groundwork only works if real employees
disclose decision-relevant, self-costly truths to an AI interviewer that acts on
behalf of their employer. The adversarial failure analysis argues candor is
*structurally capped*: people won't tell an employer's bot the things that make
the product valuable. This document designs the cheapest experiment that can
confirm or refute that in 30 days — and is built to return a **KILL** verdict if
the risk is real.

> Guiding principle: an experiment that can only conclude "promising" is a failed
> experiment. This one is pre-registered to resolve into GO / PIVOT / KILL.

---

## 1. The one question

> **Under the best trust conditions we can realistically offer, do employees in a
> real organization disclose Tier 2–4 sensitive truths through Groundwork's AI
> interview at a rate high enough — and clean enough — to produce
> decision-grade organizational insight a consultant would stake a recommendation
> on?**

Two words carry the weight:

- **"best trust conditions we can realistically offer"** — we are not testing a
  weak deployment. If candor fails under our *strongest* honest guarantee, it
  fails everywhere. We test the ceiling first.
- **"decision-grade"** — verbosity, sentiment, and generic summaries do not
  count. Only disclosures that change what a consultant recommends count.

---

## 2. Why candor cannot be measured directly (the core problem)

Candor is the disclosure of something the subject had reason to withhold. The
defining feature of the failure mode is that **when someone conceals, you don't
know they concealed.** There is no error signal. So the naïve metric —
"employees said lots of things, therefore candor is high" — is not just weak, it
measures the opposite of what matters (a fluent, agreeable, non-threatening
transcript is exactly what a *guarded* employee produces).

Every design decision below exists to manufacture a truth signal where none
exists naturally. We do it by **triangulating four independent estimators of the
latent truth** and measuring how much of it each channel recovers.

### 2.1 Constructs

| Symbol | Meaning |
|---|---|
| **Latent truth** `T` | What is actually true about the org (partially unknowable) |
| **Disclosure** `D` | What a subject says through a channel |
| **Candor** | `D` *conditional on `T` being costly/sensitive to disclose* |
| **Concealment** | Costly-`T` withheld (false negative) — the primary risk |
| **Confabulation** | `D` asserted with no supporting `T` (false positive) — the secondary risk |

Candor is not verbosity and not sentiment. It is **recovered costly truth.**

### 2.2 The tiers of truth (candor is only meaningful at the top)

Groundwork's commercial value lives in Tiers 2–4. Tier 0–1 disclosure proves
nothing — nobody hides their toolset.

| Tier | Content | Cost to disclose | Commercial value | Example |
|---|---|---|---|---|
| 0 | Neutral facts | none | ~0 | "We use Jira and Slack." |
| 1 | Process reality vs mandate | low | low | "Nobody actually updates the CRM." |
| 2 | Inefficiency / workarounds / shadow IT | medium | high | "I keep a private spreadsheet because the system is unusable." |
| 3 | Managerial / political criticism | high | high | "The real bottleneck is my director's approvals." |
| 4 | Self-implicating admissions | highest | highest | "I'm underutilized." / "We hide slippage from management." |

**All primary metrics are computed on Tier 2–4 items only.** Reporting a blended
"candor score" that includes Tier 0–1 is disqualified as a success theater.

---

## 3. Two staged questions (fail cheap, then fail expensive)

We separate a question about **the setting** from a question about **the
product**, and gate the second on the first.

- **Q1 — Ceiling / setting question:** Do employees disclose Tier 2–4 truths
  through *any* digital, employer-adjacent channel at all? This is about human
  behavior in the deployment context, not the AI. If the answer is no, **Groundwork
  is dead regardless of how good the AI is**, and we learn it in Week 2 for
  almost nothing.
- **Q2 — Channel / product question:** Does the *AI interviewer specifically*
  recover that truth as well as or better than an anonymous survey and a trusted
  human interviewer — cleanly enough (low confabulation) to be decision-grade?

Run Q1 as a gate. Only spend the back half of the month on Q2 if Q1 clears.

---

## 4. Measurement strategy — four independent estimators of the truth

No single method is trustworthy. Convergence across four is the evidence.

### E1 — Seeded known truths (individual-level recall)
Before fieldwork, work with the design partner's leadership + one trusted
internal champion to enumerate **8–12 sensitive truths already known to be
true** (a known abandoned tool, a known interpersonal conflict, a known
recurring workaround, a known approval bottleneck). These become a **recall
set**: for each channel, does it surface the known truth?
`Seeded recall = surfaced / known`.
*Limitation:* leadership's "known truths" are themselves biased and incomplete;
E1 measures recall against a partial key, so it can prove concealment but not
prove completeness. Treated as necessary-not-sufficient.

### E2 — List experiment + randomized response (ground-truth-free prevalence)
This is the methodological unlock. Using indirect survey techniques we estimate
the **population prevalence of sensitive behaviors without any individual ever
admitting one** — giving a truth anchor immune to social desirability.

- **List (item-count) experiment:** respondents see a list of statements and
  report *how many* apply, not which. A randomized half sees the list plus one
  sensitive item; the prevalence of the sensitive item = difference in group
  means. No individual is ever identifiable as admitting it.
- **Randomized response:** a private coin flip forces a randomized "yes" some of
  the time, so any single "yes" is deniable, but the population rate is
  recoverable.

For 3–5 sensitive **index behaviors** (see Appendix B) this yields `p_true` — a
defensible estimate of how common the behavior actually is. Every channel's
direct-disclosure rate is then benchmarked against `p_true`.

### E3 — Multi-channel differential candor (within-subject)
The same subjects pass through three elicitation channels (order
counterbalanced): **anonymous survey**, **AI interview (Groundwork)**, **trusted
human interview** (external consultant under NDA, employer-blinded). Disclosure
gaps between channels isolate the channel effect. The best non-AI channel is the
*ceiling*; the AI is judged relative to it, not in a vacuum.

### E4 — Behavioral / telemetry corroboration (where lawful & available)
Where the org can lawfully share aggregate system logs (tool-adoption rates,
license utilization, cycle times), compare *claimed* behavior to *actual*
behavior. A gap between "everyone says they use X" and "logs show 12% use X" is
direct evidence of concealment, independent of every self-report.

**The truth estimate for each index behavior is the convergence of E1–E4.** A
channel's candor is how much of that converged truth it recovers.

---

## 5. Experimental design

### 5.1 Setting & sample — a real org, and why it must be
Candor is context-dependent. A paid panel, a friendly advisor, or a synthetic
persona will *over*-disclose (no real skin in the game) and produce a false
positive. We require **one real design-partner company, one department, ~15–40
employees with genuine stakes.** Small n is accepted and compensated for with a
**within-subject** design (every subject is their own control across channels),
which buys statistical power that between-subject small-n cannot.

*Honesty caveat, pre-registered:* a company that volunteers for a candor study
is unusually high-trust and self-selects toward a favorable result. Therefore a
**positive result here is an upper bound**, not an expectation. A negative result
here is close to dispositive (if even a friendly org won't talk, hostile ones
certainly won't).

### 5.2 Arms — what we manipulate (the trust guarantee IS the treatment)
The dominant lever on candor is the **confidentiality architecture** (this is the
F3 anonymity-paradox mechanism). We run a within-subject 2-condition contrast on
the AI channel, randomized by index-topic block:

- **Arm A — Confidential-to-consultant, employer-blinded:** raw responses go
  only to the external consultant; employer receives aggregated findings above a
  k-anonymity threshold; explicit written guarantee shown before the interview.
- **Arm B — Attributed / standard SaaS:** responses are associated with the
  employee and visible to the employer, as a naïve deployment would be.

The A–B delta on Tier 2–4 disclosure quantifies **how much candor is bought by
the trust guarantee** — the single most important number for the product's
architecture. (We deliberately do *not* run a fully anonymous no-consultant arm
as primary, because Groundwork's value proposition requires the consultant loop;
but it can be added as a ceiling reference if budget allows.)

### 5.3 Randomization & counterbalancing
- Channel order (survey / AI / human) counterbalanced (Latin square) to net out
  fatigue and priming.
- Index behaviors randomly assigned to Arm A vs Arm B blocks per subject.
- List-experiment control/treatment split randomized at the person level.
- Seeded-truth items distributed so no single interview contains an implausible
  density of them.

---

## 6. Instruments

1. **AI interview protocol (Groundwork).** A 20–25 min structured-but-adaptive
   interview whose probes are explicitly engineered to reach Tiers 2–4:
   hypothesis-driven follow-ups, specificity conversion ("can you give me the
   last concrete instance?"), contradiction surfacing, and safety/candor moves
   (normalization, non-judgment, confidentiality reminders). Draws on the
   existing `INTERVIEW_PROMPT_SUITE`. Every surfaced claim must carry an evidence
   span (for the confabulation audit).
2. **Anonymous survey (mirror).** Item-for-item mirror of the Tier 2–4 targets,
   so survey vs AI is a like-for-like disclosure comparison.
3. **Human benchmark interview.** External consultant, NDA, employer-blinded,
   same target map. This is the *ceiling* channel and the decision-sufficiency
   reference.
4. **List-experiment / randomized-response block.** Embedded in the survey
   instrument (Appendix B).
5. **Perceived-anonymity & trust scale (mediator).** Short validated-style scale
   capturing re-identification fear, perceived data recipient, and felt safety —
   measured *before and after* each channel. This tests the *mechanism*, not just
   the outcome, and predicts whether the A–B delta is causal.
6. **Planted-false-premise items (confabulation control).** A small number of
   subtly false premises introduced to detect whether subjects — or, critically,
   the AI's *synthesis* — fabricate corroboration for things that aren't true.

---

## 7. Metrics

### 7.1 Primary
- **Candor Capture Ratio (CCR):** for each channel `c` and index behavior `i`,
  `CCR(c,i) = p_disclosed(c,i) / p_true(i)` where `p_true` comes from E2/E4.
  Reported per tier; headline is **mean CCR over Tier 2–4**.
- **Candor Gap:** `CCR(AI) − CCR(best non-AI channel)` on Tier 2–4. This is the
  product's core number — does the AI help or suppress?
- **Trust-Lift:** `CCR(Arm A) − CCR(Arm B)` — candor bought by the guarantee.

### 7.2 Secondary
- **Seeded recall** (E1) per channel.
- **Confabulation rate:** share of AI-synthesized findings unsupported by any
  real disclosure or contradicted by the planted-false-premise controls.
- **Perceived-anonymity mediation:** correlation of felt-safety with Tier 2–4
  disclosure; formal mediation of the Arm A→disclosure effect through felt-safety.
- **Participation & opt-in bias:** participation rate; demographic/role skew of
  opt-ins vs the department. (Because the fearful abstain, measured candor is an
  upper bound — report it as such.)

### 7.3 Bridge metric (candor → value, one foot into F2)
- **Decision-sufficiency:** an independent senior consultant, **blind to which
  channel produced which output**, scores each channel's synthesis on: number of
  evidence-backed, Tier 2–4 findings they would stake a recommendation on. The
  AI must **meet or beat the human** here to justify replacing the human.

---

## 8. Pre-registered analysis plan

Pre-registration is non-negotiable because the founders are motivated to see
success (the F18/F15 flattery risk). Locked *before* any data is seen:

- **H1 (setting):** best non-AI channel Tier 2–4 `CCR ≥ 0.50`.
- **H2 (channel):** `CCR(AI) ≥ 0.80 × CCR(best non-AI channel)` on Tier 2–4.
- **H3 (trust mechanism):** Trust-Lift `> 0` and mediated by felt-safety.
- **H4 (cleanliness):** AI confabulation rate `≤ 5%`.
- **H5 (value):** AI decision-sufficiency `≥` human decision-sufficiency.
- **Stats:** within-subject mixed-effects models (subject random effect; channel,
  arm, tier fixed); list-experiment via difference-in-means with design-based SEs;
  mediation via bootstrapped indirect effect. Report effect sizes + intervals,
  not just p-values. n is small — **we pre-commit to interpreting intervals, and
  to treating an underpowered null as inconclusive, not as pass.**
- **Adversarial reviewer:** a skeptic (not the founders) reviews the frozen plan
  and, at unblinding, argues the *kill* case first. Analyst is blind to channel
  labels during coding of transcripts.

---

## 9. Decision rule — GO / PIVOT / KILL

Evaluated in order. This is the deliverable of the whole month.

| Gate | Condition | Verdict |
|---|---|---|
| **G0 Setting (Q1)** | H1 fails — even the best channel recovers <50% of truth on Tier 2–4 | **KILL / category thesis broken.** Employees will not disclose digitally in an employer context. No amount of AI quality fixes this. Stop, or pivot entirely away from AI-led interviews. |
| **G1 Cleanliness** | H4 fails — confabulation >15% | **KILL the autonomous-synthesis thesis.** False confidence is worse than silence (F4/F5 legal). At best, demote AI to evidence-tagging assist under human synthesis. |
| **G2 Channel (Q2)** | H2 fails — `CCR(AI) < 0.5 × ceiling` | **KILL "AI does the interview."** The AI specifically suppresses candor. Pivot to AI-assists-human. |
| **G3 Partial** | H2 in `[0.5, 0.8) ×` ceiling | **PIVOT.** AI adds structure/scale but needs a trust redesign (architecture, framing, sponsorship) before it can lead. Re-run one cycle with the redesign. |
| **G4 Value** | H5 fails — AI value `<` human value | **PIVOT.** Candor may exist but the AI isn't converting it to decision-grade output; problem is synthesis, not elicitation. |
| **GO** | H1, H2, H3, H4, H5 all clear | **GO.** The core existential risk is refuted *for this segment*. Proceed to a second, less-friendly org to test generalization before scaling. |

Note the asymmetry: **KILL is easy to trigger and cheap; GO requires clearing
every gate and is explicitly provisional** (one friendly org ≠ the market).

---

## 10. Threats to validity (the honest section)

| Threat | Direction | Mitigation |
|---|---|---|
| Design-partner friendliness / self-selection | inflates candor → false GO | Treat positive as upper bound; require a second, colder org before scaling; report opt-in skew. |
| Demand / Hawthorne effect | inflates disclosure | Counterbalance channels; embed indirect (list/RR) measures that are immune; keep the study's true hypothesis blind to subjects. |
| Social desirability | suppresses Tier 3–4 | List experiment & randomized response are designed exactly for this; compare against them. |
| Seeded-truth leakage | inflates recall | Compartmentalize the recall set; audit for improbable disclosure density. |
| Consultant-in-the-loop confound (E3 human channel) | favors human | Standardize human protocol; blind decision-sufficiency scorer to channel. |
| Small n / single dept | limits external validity | Within-subject power; explicit provisional GO; pre-committed second-org replication. |
| Analyst motivated reasoning | inflates everything | Pre-registration, blinding, adversarial reviewer arguing KILL first. |
| Legal/ethical exposure from collecting sensitive criticism | real-world harm | See §12; consent + employer data firewall + k-anonymity + legal review are prerequisites, and are themselves the Arm A treatment. |

---

## 11. 30-day operational plan

| Days | Phase | Output |
|---|---|---|
| **1–5** | **Setup.** Recruit design partner + champion; sign data-handling/NDA; legal + consent review; enumerate seeded truths (E1); pick 3–5 index behaviors; construct list/RR blocks; freeze pre-registration; build/adapt AI protocol + mirror survey. | Frozen protocol, signed agreements, instruments. |
| **6–8** | **Pilot (n≈3).** Dry-run all channels; check list-experiment arithmetic, timing, comprehension, evidence-tagging, false-premise controls. | Fixed instruments; no data used in analysis. |
| **9–16** | **Q1 wave — the gate.** Run anonymous survey + list/RR + human benchmark across the sample; pull E4 telemetry. Compute `p_true` and non-AI `CCR`. **Evaluate G0 mid-month.** | Q1 readout. If G0 fails → **stop here, ~55% of budget saved.** |
| **17–24** | **Q2 wave.** Run the AI interviews (Arms A & B, counterbalanced); evidence-tag every claim; run confabulation audit. | AI disclosure + confabulation data. |
| **25–28** | **Analysis.** Fit pre-registered models; blind decision-sufficiency scoring; adversarial reviewer argues KILL. | Metric table vs H1–H5. |
| **29–30** | **Verdict.** Apply §9 decision rule. Write the GO/PIVOT/KILL memo with intervals and caveats. | One-page verdict + full readout. |

---

## 12. Ethics, consent, legal (prerequisite, not afterthought)

Because the study deliberately elicits criticism of managers and self-implicating
admissions, the confidentiality architecture is both an ethical obligation and
the experimental treatment:

- Informed consent stating exactly **who sees raw responses** (consultant only, in
  Arm A) and **what the employer receives** (aggregated above a k-anonymity
  threshold).
- Hard **data firewall** between raw responses and the employer; no attributed
  Tier 3–4 content ever reaches management.
- Right to withdraw; no employment consequence; independent point of contact.
- Legal review of retention, and of any unsourced-accusation exposure (F5).
- **A leak here doesn't just void the study — it is the F3/F5 failure happening
  live.** Running the guarantee cleanly is itself a test of whether Groundwork can
  operate the guarantee at all.

## 13. Cost & team
- **People:** 1 research-literate lead (design/analysis), 1 engineer (protocol +
  evidence tagging + telemetry), 1 external consultant (human benchmark +
  blind scoring), part-time legal review.
- **Money:** dominated by consultant time + a modest participation incentive;
  target a few thousand dollars + ~3 people for one month. This is the cheapest
  possible test of the most expensive possible mistake.

## 14. What a GO does and does NOT prove
- **Does:** in one real, favorable org, employees disclosed Tier 2–4 truth to the
  AI at ≥80% of the human ceiling, cleanly, and the AI's synthesis was
  decision-grade — refuting F1 *for that segment*.
- **Does NOT:** prove it generalizes to hostile cultures, unionized or
  low-trust workforces, adversarial post-layoff climates, or verticals with
  regulatory fear. It does not prove buyers will trust the output (F7) or that
  the economics work (F19). **GO buys the right to run a second, colder
  replication — nothing more.**

## 15. Stopping rules
- Stop and KILL at **G0** mid-month if the setting gate fails.
- Stop immediately if the confidentiality guarantee is breached (ethical + it
  invalidates every downstream disclosure and re-tests as an F3/F5 failure).
- Halt Q2 if the pilot shows the AI cannot reliably attach evidence to claims
  (confabulation is then unmeasurable and the audit is meaningless).

---

## Appendix A — Example seeded truths (E1)
> Co-created with leadership + champion; kept compartmentalized.
1. A named tool was mandated 6 months ago and is effectively abandoned.
2. Two teams both believe they own the same handoff; it silently drops.
3. A weekly report is assembled manually from a shadow spreadsheet.
4. One approval step routinely adds days and everyone routes around it.
5. A "resolved" reorg still has unclear reporting lines in practice.

## Appendix B — Example sensitive index behaviors (E2, Tier 2–4)
> Measured indirectly via list experiment / randomized response to get `p_true`,
> then directly via each channel to get `p_disclosed`.
- "I regularly bypass the officially mandated process/tool for [core task]."
- "In the last month I spent significant time on work I believed was redundant or
  wasted."
- "My team withholds problems or slippage from management."
- "I have presented status as better than it actually was."
- "I am materially under-utilized relative to my role."

## Appendix C — List-experiment construction (sketch)
Control group sees 4 innocuous statements and reports the **count** that apply.
Treatment group sees the same 4 **plus one** sensitive index item and reports the
count. `p_true(sensitive) = mean(treatment) − mean(control)`. No individual is
ever identifiable as endorsing the sensitive item; the population rate is
recovered from the difference of means. Randomized response provides a
convergent second estimate via a private coin flip that injects deniable "yes"
responses at a known rate.

## Appendix D — Example AI probe ladder toward Tier 3–4
1. **Neutral open (T0):** "Walk me through how [process] actually works day to day."
2. **Reality vs mandate (T1):** "Where does the real version differ from how it's
   supposed to work?"
3. **Specificity conversion (T2):** "When was the last time that cost you real
   time — what happened exactly?"
4. **Attribution, safely (T3):** "Was that about the tooling, the process, or a
   decision someone made? No wrong answer — I'm mapping where the friction sits."
5. **Self-implication, normalized (T4):** "Lots of people quietly work around
   this. What's your own workaround, if you have one?"

---

*Bottom line:* this is a 30-day, ~3-person, few-thousand-dollar experiment whose
default posture is skepticism and whose gates are tuned to KILL early and cheap.
If candor is structurally capped, we find out in Week 2 at Gate G0 and save the
company years. If it isn't, we earn the right to ask the next question — for one
friendly org, provisionally, once.
