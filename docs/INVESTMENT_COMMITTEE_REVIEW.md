# Ontora — Pre-Seed Investment Committee Review

> Closed-door red team convened before Ontora's first institutional raise. Five
> independent reviewers, no attachment to the project, reputations staked on
> finding the flaws first. This is a transcript, not a brochure. It is not polite.

**The room**
- **Devi** — YC General Partner; funded multiple billion-dollar AI companies. Lens: wedge, distribution, painkiller-vs-vitamin, speed.
- **Reinhardt** — former McKinsey Senior Partner, org transformation. Lens: who actually buys, consulting economics, whether the interview works.
- **Yuki** — Principal Research Scientist, Anthropic; reasoning systems & agents. Lens: what models can actually do, identifiability, eval.
- **Marcus** — CTO, Palantir; enterprise knowledge systems. Lens: deployment reality, data integration, ontologies, why the AI is the easy part.
- **Angela** — CIO, Fortune 500 (100k+ employees). Lens: the buyer/blocker; trust, legal, procurement, employee behavior.

---

## PART I — Fundamental product risk

**Devi:** Start with the only question that matters. Is this a painkiller or a
vitamin? "Understand how your organization really works" is a vitamin. Nobody wires
$400k for enlightenment. What's the bleeding neck?

**Reinhardt:** The bleeding neck is real but narrow. Every transformation begins
with a discovery phase — six to ten weeks of associates interviewing employees. It's
slow, expensive, and inconsistent. *But* — and this is fatal — discovery is the
*cheapest, least defensible* part of my old business. The money is in
implementation and in the trusted relationship. Ontora is automating the loss
leader.

**Devi:** So it's a feature of a consulting engagement, not a company.

**Reinhardt:** Potentially. Unless the wedge is "AI transformation," where the
discovery question — *which processes should we automate* — is genuinely a
painkiller right now, because every CEO has an AI mandate and no idea where to
point it.

**Marcus:** You're both missing the existential threat. The enacted reality of an
organization is already sitting in its digital exhaust — Slack, email, tickets,
calendars, git, CRM, process logs. Celonis mines it. In five years an LLM over that
exhaust reconstructs "how work actually flows" *without interviewing a single
human*. The interview is a 2024 workaround for not having the data pipes. Why does
this company exist once the pipes exist?

**Yuki:** Because exhaust captures *behavior*, not *reason*. Logs tell you the
invoice bounced three times. They don't tell you it bounced because the AP clerk
doesn't trust the new system and secretly keeps a spreadsheet. Tacit knowledge,
workarounds, fear — that lives in people's heads, not in logs. That's the defensible
sliver.

**Marcus:** A sliver. And a shrinking one, because models are getting better at
inferring reason from behavior.

**Angela:** Can I ground this? "Why now" is real — LLMs make the interview and
synthesis newly possible. But "who pays" is unresolved and it's a knife fight. If
you sell to consulting firms, you have channel conflict — you're shrinking their
billable hours. If you sell to me directly, you're now a boutique consultancy
competing with McKinsey on trust, with no brand. Which is it?

**Devi:** That fork — arm the consultants or replace them — is the whole company,
and the deck doesn't pick one. That's a yellow flag on founder clarity.

**Reinhardt:** Could this be unnecessary in five years? Yes, in two ways: exhaust
mining eats the interview, *or* the frontier labs ship an "org copilot" that does
discovery as a side effect. The window is real but it is not wide.

**Verdict, Part I:** Real pain, wrong framing. It's a painkiller *only* under the
narrow "where do we point our AI budget" wedge, and even there it's threatened by
digital-exhaust mining and by the labs. **Severity: medium. Durability: low unless
narrowed.**

---

## PART II — Customer reality

**Angela:** Let me walk you through what actually happens when this lands in my
company, because it's uglier than the deck. Week one, my General Counsel asks:
"You want to record 200 employees describing what's broken, including complaints
about their managers, and store it?" That's a discovery-liability goldmine in
litigation, a GDPR problem in the EU, and in Germany the works council vetoes it
outright. The pilot dies in legal before a single interview.

**Reinhardt:** Assume legal clears it, anonymized and aggregated. Now the employee
behavior problem. I have run thousands of these. People do *not* tell a
corporate-procured AI the truth about their manager. They sandbag. They give the
socially safe answer. A skilled human consultant gets candor through rapport, eye
contact, and a promise the employee believes. An AI has none of those.

**Yuki:** That's the core scientific bet and I agree it's shaky. The interview
engine's whole "candor estimation" assumes you can detect and relieve guardedness
from text. Maybe. But even a *candid* employee only sees their corner. You're
aggregating 200 partial, biased views and calling it truth.

**Devi:** Where do consultants ignore the AI? Everywhere it disagrees with their
gut. A partner walks in with a hypothesis after two conversations. If Ontora's
output matches, it's "confirmation, nice." If it contradicts, it's "the AI doesn't
understand our client." It's unfalsifiable to the user either way.

**Marcus:** And executives distrust the output *structurally*. "An AI interviewed
200 people and concluded finance is your bottleneck." First question: "Who said
that?" You can't tell them — anonymity. So it's an unsourced accusation about a
named department. No exec acts on that. At Palantir we learned: humans trust systems
that let them *drill to the source*. Ontora's central privacy promise destroys its
own credibility with the buyer.

**Angela:** That's the sharpest point made yet. The anonymity that gets employees to
talk is the same anonymity that makes executives dismiss the finding. That tension
may be *unresolvable*.

**Yuki:** It's resolvable statistically — "70% of finance staff, across independent
roles, reported X" is sourceable-in-aggregate without naming names. But it requires
volume and honesty you haven't proven you can get.

**Devi:** Which assumptions break? All the load-bearing ones: employees are honest,
legal allows it, execs trust unsourced aggregates, consultants adopt a tool that
threatens them. Four independent single-points-of-failure. Multiply the
probabilities and you're terrified.

**Verdict, Part II:** The human and legal layer — not the technology — is where this
dies. The anonymity paradox (candor vs. credibility) is a possibly-fatal, and
currently unaddressed, contradiction.

---

## PART III — Attack the Interview Intelligence Engine

**Reinhardt:** Do experienced consultants actually interview the way that engine
describes? No. The document is an engineer's fantasy of how consultants think. Real
senior interviewing is 80% relationship and pattern intuition, 20% technique. The
"threat-adjusted value-of-information per minute" scorer — no human does that, and
modeling it doesn't make the *questions* better, it makes them *optimal for a proxy
objective* that may not be truth.

**Yuki:** I'll pile on, then partially rescue it. "Emotional interpretation from
transcript" — detecting frustration, resignation, pride — is scientifically weak.
Text sentiment is noisy; you'll act on phantom affect. "Candor estimation" is worse
— you're inferring a hidden variable (honesty) with no ground truth to calibrate
against. That's an unfalsifiable knob. **However**: hypothesis-driven interviewing
is genuinely right and is what *good* interviewers do implicitly. Making it explicit
could make a *mediocre* interviewer perform like a good one. That's real value — for
junior consultants and internal teams, not for partners.

**Devi:** So the honest positioning is "we make average interviewers good," not "we
uncover organizational truth." Much smaller, much more credible claim.

**Marcus:** Contradiction handling — the "is it error or genuine variation" call —
is the one part I respect. Distinguishing "someone's wrong" from "this process is
non-standardized" is exactly the insight consultants get paid for. But can a model
reliably make that call, or will it confabulate variation to look insightful?

**Yuki:** Today? It'll over-detect. Models pattern-match to "interesting finding."
The belief-updating framing is mostly window dressing over an LLM's vibes unless you
build real eval — and there's no eval harness anywhere in this project. That's the
tell. Elaborate cognitive architecture, zero measurement.

**Reinhardt:** The uncomfortable question nobody's asked: is a 20-minute AI
interview meaningfully better than a well-designed survey plus existing tools? If
the honest answer is "marginally," there's no company here.

**Verdict, Part III:** The engine's best idea (hypothesis-driven + contradiction
typing) is real but overclaimed. Candor and emotion estimation are unproven and
possibly unfalsifiable. The absence of any evaluation methodology is the most
damning single fact in the whole review.

---

## PART IV — Attack the epistemology

**Devi:** Before Yuki gets excited — the epistemology paper is the reddest flag in
the data room. Founders wrote an academic treatise on "organizational truth" before
signing one customer. That's not depth, it's avoidance. It tells me they'd rather
think than sell.

**Yuki:** Disagree on intent, agree on timing. The *ideas* are the best thinking in
the whole project. "Testimony is not evidence about the world, it's evidence about
(world, standpoint, candor)" — that's *correct*, and most people building this
would never see it. Belief decay is genuinely clever. But here's where it collapses:
**identifiability.** You cannot, in general, separate the world ω from the speaker's
distortion (s, c) using testimony alone. It's mathematically under-determined — one
equation, three unknowns. You need exogenous anchors (documents, observed outcomes),
and those are exactly what the "interview-first" thesis refuses to lean on.

**Marcus:** So the theory requires the data integration the product deprioritizes.
That's a self-inflicted contradiction.

**Reinhardt:** The deeper problem is A3 — "there is a real organization." Is there? A
company is partly *constituted* by the conflicting beliefs of its members. There may
be no single ω to recover. Sales and Engineering don't have imperfect views of one
truth; they inhabit different, both-valid realities. Bayesian inference over a
non-existent latent state is elegant nonsense.

**Yuki:** That's the strongest objection in the room. If organizational truth is
irreducibly plural, the whole "converge to ω" program is category error. The
coherence-field idea partially saves it — model the *disagreement* rather than a
consensus ω — but then you've abandoned the realist framing the paper is built on.

**Angela:** And the "population prior Π" — learning across all clients — that's
either the moat or a lawsuit. I will not sign a contract where my org's patterns
train a model that sharpens your work for my competitor. Legal calls that
confidentiality leakage. So the compounding moat may be contractually illegal.

**Yuki:** Differential privacy and hierarchical modeling can bound the leakage
mathematically. But "mathematically bounded" and "survives an enterprise infosec
review" are different universes.

**Devi:** Net: a beautiful theory, partially wrong, partly unprovable, adds nothing
to the next 18 months, and its one true moat may be illegal. Shelve it.

**Yuki:** Shelve building it. *Keep* the testimony-likelihood insight — it should
shape how you weight interview data even in a dumb MVP. Deleting that would be
throwing away the one genuinely differentiated thought.

**Verdict, Part IV:** One profound correct idea (testimony ≠ truth), one likely-fatal
flaw (identifiability), one philosophical crack (plural truth), one legal landmine
(Π). Research agenda, not a product foundation. Do not build it now; do not fully
discard it.

---

## PART V — Attack the architecture (conceptual only)

**Marcus:** Six bounded contexts, a drift engine, an official-org model, probabilistic
identity resolution — before revenue. This is the most over-architected pre-seed
codebase I've seen, and I've seen a lot. The Drift context assumes customers have a
clean "official" model to compare against. They don't. It's dead weight.

**Devi:** Which contexts are unnecessary? Drift, Organization's official catalog,
Insights' synthesis layer, identity resolution. The MVP is: run an interview, store
the transcript, extract a few candidate insights, show a human. That's *one*
context, maybe two.

**Reinhardt:** Careful — someone defend the graph before you delete it. The knowledge
representation is the one piece that could accumulate into something. If you throw
away all structure you're left with a chatbot that summarizes interviews. The
*substrate* — some queryable model of how work connects — is worth keeping thin, not
killing.

**Yuki:** Agreed, but "one graph, universal ontology" is the wrong bet.
Organizations don't share a schema. Marcus lived this.

**Marcus:** We did. At Palantir the entire lesson was: the ontology is *per-customer*,
and the value is in the forward-deployed work of fitting it. Ontora's universal
Workflow/Activity/Handoff schema will shatter on the third customer — a hospital, a
bank, and a game studio do not decompose the same way. Which contexts should merge?
Insights and Drift are the same thing — analysis over a belief model. Knowledge and
Insights largely overlap. You have three or four contexts pretending to be six.

**Angela:** From the buyer's chair, none of this architecture is visible or valued. I
buy an outcome, not an ontology. Every hour spent on context boundaries is an hour
not spent on the thing that determines the sale: does the output change a decision I
make?

**Verdict, Part V:** Delete Drift, official-org, identity resolution, synthesis layer.
Merge Insights into Knowledge into one "analysis" concept. Keep a *thin, per-customer-
flexible* knowledge substrate. The architecture solves problems no customer has.

---

## PART VI — Competitive landscape

**Devi:** Round the room. How does each giant kill or copy this?

**Yuki (labs):** **OpenAI / Anthropic** could build the interview agent in a quarter —
it's a prompt and an eval harness. They *won't* focus on this enterprise niche soon,
so it's not an active threat, but it means the *agent itself is not a moat*. The
model layer is rented by everyone including Ontora.

**Angela (Microsoft):** **Microsoft** is the assassin. They own the workplace — Teams,
Viva, Graph, the org chart, the calendars, the digital exhaust — *and* the
distribution into every enterprise, *and* Copilot. They can surface "how your org
works" from data I already gave them, no interviews, no legal fight, bundled at
$0 marginal price. If org intelligence becomes valuable, Microsoft ships it as a
Viva feature and Ontora evaporates.

**Marcus (Palantir):** **Palantir** copies the substrate and out-deploys them. We have
the FDE muscle, the security clearances, the enterprise trust, and the ontology
tooling. If interviews prove valuable we bolt them onto Foundry. Our moat —
deployment and trust — is the exact moat Ontora *lacks*.

**Reinhardt (the firms):** **McKinsey / Deloitte** won't productize this — channel
conflict — but they'll build good-enough *internal* versions to defend margins, which
removes Ontora's most natural channel. Deloitte especially will slap an LLM on their
methodology and call it proprietary.

**Angela (systems of record):** **Workday / SAP** own the HR and process data and the
procurement relationship. They add "org intelligence" as an upsell to a contract I've
already signed. Distribution and data, again.

**Devi:** So which parts *cannot* be a moat? The model (rented), the interview prompt
(copyable in a weekend), the graph (commodity), the "insights" (any LLM). What's
left as a *possible* moat? Exactly three things: (1) proprietary *validated-outcome*
data — did the client act, did it work — which only accrues with real deployments;
(2) forward-deployed *trust and relationships*, the Palantir moat, which is
services-heavy and slow; (3) the cross-client prior Π, which may be illegal. Every
one of those is expensive, slow, and unproven.

**Marcus:** And every incumbent has a head start on at least one of the three.

**Verdict, Part VI:** The technology is not the moat and everyone at this table can
build the technology. The only candidate moats are slow, services-heavy, and
partially legally blocked. Microsoft is the existential distribution threat.

---

## PART VII — Scientific risk, ranked by existential importance

**Yuki:** Strip the business and rank the unproven science. If any of the top three
is false, there is no company.

1. **[EXISTENTIAL] A 20-minute AI interview elicits truthful, actionable data from a
   self-interested employee.** Everything rests here. Unproven. Possibly false given
   incentives.
2. **[EXISTENTIAL] Extraction converts messy testimony into reliable structured
   insight without confabulation** at a rate consultants trust. Unproven; current
   models over-claim insight.
3. **[EXISTENTIAL] Decision-makers act on AI-derived, aggregate-sourced org
   intelligence.** If they don't, there's no revenue regardless of accuracy.
4. **[HIGH] Organizational truth is singular enough to estimate** (the A3/plural-truth
   problem).
5. **[HIGH] (world, standpoint, candor) is identifiable** from testimony + light
   anchors.
6. **[HIGH] Interview-derived intelligence beats digital-exhaust-derived** enough to
   justify the interview's cost and friction.
7. **[MEDIUM] The cross-client prior Π transfers and compounds** — and legally.
8. **[MEDIUM] Candor and affect are estimable from text** well enough to act on.

**Devi:** Note that 1, 2, and 3 can be tested for under $50k in six weeks. The fact
that the founders built an epistemology and six contexts *instead* of testing 1–3 is
the single most important behavioral data point about this team.

**Verdict, Part VII:** Three existential unknowns, all cheaply testable, none tested.
That inversion is the investment thesis's biggest problem — and its biggest cheap
opportunity.

---

## PART VIII — Business model

**Reinhardt:** The consulting-vs-SaaS question isn't a preference, it's a physics
problem. Org intelligence *cannot* be sold self-serve — no CIO buys "interview my
employees" from a website. So you are services-led whether you like it or not. That
means low margin, slow scale, non-recurring revenue early. VCs hate that shape.

**Devi:** The good version is "services-led SaaS" — use high-touch early engagements
to build the validated-outcome dataset and the product, then productize. Palantir's
arc. But that arc takes a decade and burns capital, and most who try it stay a
consultancy forever.

**Angela:** Pricing has no obvious value metric. Per employee interviewed? Per
engagement? Per seat for consultants? Per decision informed? Nobody knows what this
is worth because nobody's proven it changes an outcome. You can't price a benefit you
haven't demonstrated.

**Angela (procurement):** And the go-to-market reality: enterprise procurement is
12–18 months, security review, legal review, works-council review, a champion who
can get fired for the bet. A pre-seed startup asking employees to confess
organizational dysfunction will not clear my vendor risk process. You'll land two
friendly design partners through the founders' network and then hit a wall of "no."

**Marcus:** The only viable early motion is: one charismatic founder, forward-deployed,
doing the work by hand for three logos who trust them personally, extracting the
pattern. It doesn't scale, but it's the only thing that starts.

**Verdict, Part VIII:** Services-led, low-margin, slow, unclear value metric, brutal
procurement. A fundable shape *only* if the early services deliberately manufacture a
proprietary dataset and a repeatable wedge. Otherwise it's a lifestyle consultancy.

---

## PART IX — Founder risk

**Devi:** Assume the founders are brilliant engineers. That's the problem, not the
comfort. Brilliant engineers building a human-trust-and-distribution business will
make three predictable mistakes.

**Marcus:** One: they'll keep building. They already shipped six contexts and an
epistemology with zero customers. They'll respond to every "no" by adding a feature
instead of changing the pitch.

**Reinhardt:** Two: they'll underestimate that the entire game is *trust and
politics*, not accuracy. They'll believe a better model wins. It doesn't. The CIO's
General Counsel wins. The threatened middle manager who tanks the pilot wins. They
have no instinct for that layer.

**Yuki:** Three: they'll fall in love with the epistemology and the graph — the
intellectually beautiful parts — and starve the ugly, decisive parts: candor
experiments, legal packaging, the sales motion, the eval harness. They'll optimize
what's fun to optimize.

**Angela:** Where are they underestimating reality? Employee behavior, legal
exposure, procurement time, and change-management. All the non-technical
determinants of whether this lives. Where are they overengineering? Everywhere a
customer can't see.

**Devi:** The kind summary: they've proven they can *build* anything and not yet that
they can *sell* or *learn from a customer* anything. Founder-market fit on the
technology is a 10; on the go-to-market it's currently unknown, trending low.

**Verdict, Part IX:** Classic strong-engineer failure mode. The risk isn't
capability; it's spending capability on the wrong surface. Investable *only* with
hard external forcing functions toward customers.

---

## PART X — The final debate

**Devi (facilitator):** Numbers. On the table. No hedging.

| Reviewer | P($10M ARR) | P(unicorn) | P(dies) | Biggest mistake | Strongest advantage |
|---|---|---|---|---|---|
| **Devi (YC GP)** | 30% | 5% | 60% | Building a platform before finding the wedge | Genuine "why now" + rare founder intellect |
| **Reinhardt (McKinsey)** | 25% | 4% | 65% | Automating the loss-leader of consulting | Discovery is a real, hated, repeatable pain |
| **Yuki (Anthropic)** | 35% | 8% | 55% | No eval harness; theory over measurement | The testimony-likelihood insight is truly differentiated |
| **Marcus (Palantir)** | 40% | 10% | 50% | Universal ontology + interview-only | If they earn the FDE/trust motion, it compounds |
| **Angela (CIO)** | 20% | 3% | 70% | Ignoring the anonymity paradox + legal | Executives genuinely want unbiased org truth |

**Reinhardt:** Marcus, why are you the optimist? You just said the ontology shatters.

**Marcus:** Because the *motion* — forward-deployed, trust-first, pattern-extracting —
is a proven path to a hard moat, and these founders are smart enough to run it *if*
someone forces them out of the codebase. The tech is wrong; the shape is
recoverable.

**Angela:** I'm the pessimist because I'm the buyer and I'm telling you: I can't buy
this today. Fix the legal and trust story or the ARR is zero regardless of the AI.

**Yuki:** I'm slightly higher than Devi because the one real idea — weighting
testimony by standpoint and candor rather than treating it as fact — is a genuine
edge if they build eval around it. But only if. Right now it's philosophy.

**Devi:** Everyone's P(dies) is above 50%. That's not a fundable consensus on its
own. The question is whether the *cheap experiments* can move these numbers fast. I
say yes — 1, 2, 3 from Part VII cost $50k and six weeks. That's the entire
investment decision: are we funding six weeks of truth-seeking, or a five-year
platform?

---

## Consensus Investment Memo

**Recommendation: PASS as pitched. Conditional small check ($250–500k) available
only if the founders contract to the deletions and experiments below and return with
evidence.** This is not encouragement; it is a demand for proof on the three
existential unknowns before another engineer is hired.

### Reasons to invest
- A credible, time-boxed **"why now"**: LLMs make AI-interview + synthesis newly
  possible.
- **Rare founder intellect** and unusual architectural discipline (even if misdirected).
- Discovery for **AI-transformation** is a real, repeatable, currently-hated pain
  with a live budget.
- One **genuinely differentiated idea** (testimony ≠ truth; standpoint/candor
  weighting) that competitors are unlikely to see.
- If the forward-deployed motion works, the **validated-outcome dataset** is a
  defensible, compounding asset few can replicate.

### Reasons not to invest
- **No customer validation** and, worse, effort spent *avoiding* validation (theory
  and architecture over experiments).
- The **anonymity paradox**: the candor that makes data honest makes findings
  unsourceable and therefore un-trusted by buyers — possibly unresolvable.
- **Channel conflict** (consultants) and **unresolved buyer** (arm vs. replace).
- **Microsoft** (and Workday/SAP/Palantir) own the data and the distribution; the
  technology is not a moat and everyone can build it.
- **Legal/works-council/GDPR** exposure that can kill EU and slow the US.
- **Digital-exhaust mining** may obsolete the interview within the window.
- **Services-led, low-margin, 12–18-month procurement** — a hard venture shape.

### Required pivots
1. **Pick the wedge:** "AI-automation-opportunity assessment" for *one* function
   (e.g., finance ops) in *one* industry. Not a platform. A painkiller.
2. **Pick the buyer:** sell direct to enterprises as a services-led product *or* arm
   internal transformation teams — not consulting firms (channel conflict). Decide.
3. **Reframe the claim:** from "we uncover organizational truth" to "we make
   discovery 5× faster and more consistent." Smaller, credible, sellable.
4. **Confront the anonymity paradox head-on** with a statistical-sourcing design
   ("N independent roles reported X"), or the company doesn't ship.
5. **Treat interviews as one signal, not the only one** — combine with light digital
   exhaust to fix identifiability and to survive the exhaust-mining threat.

### Required deletions
- The **Drift/Assessment** context and the **official Organization** model.
- **Identity resolution** and the **synthesis layer** (clusters/bundles/root-cause).
- The **six-context architecture** → collapse to *one* thin analysis substrate.
- **Do not build** the epistemology (keep the testimony-weighting insight as a
  heuristic; shelve the rest as R&D).

### Required experiments (six weeks, <$75k, before any hire)
- **E1 — Candor:** run 20 real employee interviews; measure, against a known-truth
  control, whether the AI elicits anything a survey wouldn't.
- **E2 — Extraction fidelity:** blind-score AI-extracted insights vs. a senior
  consultant's from the same transcripts. Confabulation rate is the kill metric.
- **E3 — Decision impact:** put outputs in front of 3 real executives; measure
  whether *one decision changes*.
- **E4 — Legal viability:** get one real GC and one EU works-council read on the
  deployment model.

### Top 10 assumptions to validate before hiring more engineers
1. Employees give an AI interviewer materially more truth than a good survey. *(E1)*
2. Extraction produces insight consultants trust, with a low confabulation rate. *(E2)*
3. An executive will *act* on aggregate, unsourced AI findings. *(E3)*
4. There is a buyer who will pay, and we know whether it's the enterprise or the
   consultant.
5. The deployment clears legal, privacy, and works-council review. *(E4)*
6. A single narrow wedge (function × industry) exists where willingness-to-pay is
   real.
7. Interview-derived intelligence beats, or usefully complements, digital-exhaust
   intelligence.
8. The findings survive the anonymity paradox (sourceable-in-aggregate, trusted).
9. A repeatable, forward-deployed delivery motion exists that doesn't require a
   founder in every room.
10. Any candidate moat (validated-outcome data, trust, or the prior) can be built
    legally and before Microsoft ships a feature.

**Signed, the committee — unanimous on process, split on outcome.** Fund the six
weeks of truth, not the five-year platform. If E1–E3 come back strong, this is a
different and far more fundable conversation. If they come back weak, no architecture,
epistemology, or founder brilliance will save it — and better to learn that for $75k
than for $7M.
