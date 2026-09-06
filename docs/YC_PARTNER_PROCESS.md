# Groundwork — YC Partner Process (Internal)

> **CONFIDENTIAL · YC INTERNAL · NOT FOR FOUNDERS.** Working notes across the full
> partner process. Candid by design. Reasoned from the company's own materials
> (architecture, application layer, interview engine, epistemology) — not summaries
> of them.

**The partners in the room**
- **Garrett** — managing partner, generalist. Bets on founders and ambition.
- **Michael** — growth/GTM. One question, asked forever: *are you talking to users?*
- **Jared** — B2B/enterprise. Sales motion, procurement, unit economics.
- **Diana** — technical, ex-founder. Is the tech real, can they ship fast.
- **Aria** — deep-tech/contrarian. Defends research moats others dismiss.

**The founders:** two. **Sam** (CEO, ex-eng lead) and **Priya** (CTO, systems/ML).
Both clearly brilliant engineers. No dedicated sales founder — noted immediately.

---

## PHASE 1 — Application review

**What they are:** "AI conducts organizational-discovery interviews of employees and
produces the org intelligence consultants charge millions to gather." Pre-revenue.
Zero paying customers. An extraordinary volume of architecture, an interview-engine
design, and a formal *epistemology* — and, as far as the application shows, **not a
single completed real interview or customer conversation.**

**Immediate strengths**
- Genuinely elite technical/conceptual horsepower. The "testimony is evidence about
  (world, standpoint, candor), not about the world" insight is a real, non-obvious
  idea. Most applicants in this space are wrappers; these founders think three
  layers deeper.
- Crisp, credible **why-now**: LLMs make adaptive interviewing + synthesis newly
  possible.
- Huge market if it works (org transformation / AI-adoption consulting is tens of
  billions).
- The interview engine is the *right* thing to obsess over — they correctly
  identified their own crown jewel.

**Immediate weaknesses**
- **No users. No interviews. No customer conversations.** For a company whose entire
  thesis is about talking to humans, they have talked to zero of the humans who
  would pay them. This is the dominant fact of the application.
- **Overbuilt to an alarming degree:** six bounded contexts, a drift engine, an
  epistemology paper — the artifacts of a team that *builds to avoid selling.*
- **No sales founder, no GTM instinct on display.**
- **The buyer is undecided** (arm consultants vs. replace them) — a strategy-defining
  fork left open.
- **No eval, no metrics** — nowhere do they measure whether the interview *works.*

**Unanswered questions (for the interview)**
1. Have you run *one* real interview with a real employee? What happened?
2. Who is the buyer, and have you spoken to one?
3. Why did you build six contexts and an epistemology before doing that?
4. Can you get honest answers from an employee whose employer bought the tool?
5. Can you delete 80% of what you've built tomorrow morning?

**Decision: INVITE. Unanimous.** Not because it's close — because the founders are
clearly exceptional and the *why-now* is real, and the red flags are precisely the
kind an interview exists to resolve. If they were mediocre we'd pass on the
overbuild alone. They're not, so we need to see whether they're *researchers who
wandered into a startup* or *founders who happened to over-prepare.* That is the
entire question, and only the room answers it.

---

## PHASE 2 — Partner preparation (written independently, before the interview)

**Garrett** — *First impression:* possibly the smartest applicant this batch; also
possibly not a company yet. *Biggest concern:* they love the problem more than the
customer. *Biggest opportunity:* if redirected, elite founders in a generational
market. *Verify:* coachability — will they delete the platform when I tell them to?

**Michael** — *First impression:* textbook "built for two years, talked to no one."
*Biggest concern:* zero user contact is not a gap, it's a *personality*. *Biggest
opportunity:* the interview engine could be a real wedge if they'd ship it.
*Verify:* have they done a single unscalable thing?

**Jared** — *First impression:* the tech is impressive and irrelevant until someone
pays. *Biggest concern:* enterprise procurement + no revenue = death-valley shape.
*Biggest opportunity:* AI-transformation discovery is a live, budgeted pain.
*Verify:* is there one buyer with a credit card and a burning need?

**Diana** — *First impression:* they can obviously build; the question is whether they
can *stop* building. *Biggest concern:* no evaluation of whether the interview
actually elicits truth. *Biggest opportunity:* rare depth of thought about the
actual hard problem. *Verify:* do they have any signal the AI interview beats a
survey?

**Aria** — *First impression:* everyone will pattern-match "overbuilt, reject" and
miss that the epistemic insight is a genuine deep-tech seed. *Biggest concern:* the
insight is real but might be 5 years early. *Biggest opportunity:* the compounding
cross-client prior — if legal — is a defensible moat almost no one could build.
*Verify:* is the moat real or a beautiful idea?

*(Michael and Aria already disagree on whether the depth is an asset or a symptom.
Good.)*

---

## PHASE 3 — Founder interview (≈100 questions, compressed; every weak answer pushed)

### Founders
1. **Who are you and why you two?** *Sam:* eng lead, spent years watching consultants
   waste weeks on discovery. *Priya:* built ML systems; obsessed with the testimony
   problem. — *Garrett:* fine, but where's your salesperson? *Sam:* we planned to
   hire GTM later. — *Michael:* "later" is the most expensive word you'll say today.
2. **What's your unfair insight?** *Priya:* that an interview transcript isn't truth —
   it's truth filtered through what a person sees and what they'll say; the value is
   in modeling that filter. — *Diana:* strong. Best answer so far.
3. **What have you built vs. learned?** *Sam:* a full domain architecture and an
   epistemic framework. — *Michael:* that's all *build*. What have you *learned* from
   a customer? *Sam:* …we've had informal chats with a couple of consultant friends.
   — *Michael:* so, nothing. Moving on.
4. **Have you two shipped anything to a real user before?** *Priya:* internal tools at
   scale. — *Diana:* internal ≠ customers. Noted.
5. **Who owns the customer relationship between you?** *(pause)* *Sam:* both of us. —
   *Jared:* "both" means "neither."

### Customer discovery
6. **How many potential customers have you interviewed?** *Sam:* maybe five, casually.
   — *Michael:* five casual chats and six bounded contexts. Does that ratio bother
   you? *Sam:* …yes. It should have been reversed.
7. **What did those five say?** *Sam:* they liked the idea. — *Michael:* everyone
   likes ideas. Did any say "I'll pay"? *Sam:* no. — *Michael:* then you learned
   nothing.
8. **Have you run one full AI interview with a real employee?** *Priya:* not
   end-to-end yet. — *Diana:* so the crown jewel is untested. *Priya:* correct.
9. **Why not?** *Priya:* we wanted the foundation right first. — *Garrett:* that's the
   whole diagnosis in one sentence.
10. **When could you run 20 real interviews?** *Sam:* two weeks. — *Michael:* why
    haven't you already?

### Market
11. **How big, honestly?** *Sam:* org-transformation is $50B+. — *Jared:* that's the
    consulting market, not your serviceable slice. What's *yours*? *Sam:* discovery,
    maybe low single-digit billions. — *Jared:* and shrinking as exhaust-mining eats
    it. *Sam:* …possibly.
12. **Is this a vitamin or painkiller?** *Sam:* painkiller for AI transformation. —
    *Garrett:* only there. Everywhere else it's a vitamin. Agree? *Sam:* agree.
13. **Why now and not three years ago?** *Priya:* models can finally interview
    adaptively and extract structure. — *Diana:* accepted.
14. **Why won't this be a feature of Copilot in 18 months?** *Sam:* interviews capture
    tacit knowledge data can't. — *Michael:* that's a sentence, not a defense. We'll
    return to it.
15. **Who has this pain most acutely?** *Sam:* mid-market companies mid-AI-mandate
    with no internal strategy team. — *Jared:* better. That's a real segment.

### Product
16. **What is the smallest version that a customer pays for?** *Priya:* interview a
    department, output a ranked list of automation opportunities. — *Garrett:* good.
    *Why haven't you built only that?*
17. **What have you deleted recently?** *Sam:* nothing. — *Michael:* founders who
    can't delete, die.
18. **Walk me through the output an exec sees.** *Sam:* a ranked set of bottlenecks
    and AI opportunities with evidence. — *Jared:* whose evidence? *Sam:* anonymized
    quotes. — *Jared:* so unsourced accusations about named teams. How does an exec
    act? *Sam:* …aggregate patterns. — *Jared:* weak. Fix that or you have no
    product.
19. **What's the wow moment?** *Priya:* "the AI found the workaround your VP hides." —
    *Diana:* if true, that's a great wow. Is it true? *Priya:* we believe so. —
    *Diana:* belief isn't a demo.
20. **Is it better than a good survey plus Celonis?** *Sam:* yes, on tacit knowledge.
    — *Michael:* prove it in your six months or you're dead.

### Technology
21. **Is the interview engine built or designed?** *Priya:* designed, partially
    prototyped. — *Diana:* so it's a doc.
22. **What breaks first technically?** *Priya:* candor detection and confabulation in
    extraction. — *Diana:* honest. Good.
23. **How do you stop the model inventing insights?** *Priya:* evidence anchoring +
    validation. — *Diana:* have you measured the confabulation rate? *Priya:* not
    yet. — *Diana:* that's the number that decides your company and you don't have
    it.
24. **What's genuinely hard that a competitor can't copy in a weekend?** *Priya:* the
    learned testimony model and the cross-client prior. — *Aria:* finally, a moat
    conversation.
25. **Is any of the six-context architecture load-bearing for the MVP?** *Sam:* …no,
    most isn't. — *Garrett:* thank you for the honesty. That's a lot of dead code.

### AI / Research
26. **Is the epistemology needed to ship?** *Priya:* no — it's a five-year agenda. —
    *Michael:* then why is it in your seed application? *Priya:* because it's how we
    think. — *Michael:* it's also how you *avoid customers.*
27. **What in the epistemology is actually usable now?** *Priya:* weight interview
    data by standpoint and candor instead of treating it as fact. — *Aria:* that
    alone could differentiate the extraction. Keep it.
28. **Identifiability — can you separate world from speaker from testimony alone?**
    *Priya:* not without anchors; we'd combine interviews with light document/log
    signals. — *Diana:* which contradicts "interview-first." *Priya:* yes; we'd go
    hybrid. — *Aria:* good, they can update live.
29. **Does "organizational truth" even exist?** *Priya:* partially — some is genuinely
    plural; we model the disagreement, not a single truth. — *Aria:* that's the
    sophisticated answer. *Michael:* it's also a philosophy seminar. Ship something.
30. **What's your eval plan?** *Priya:* blind consultant scoring of extracted
    insights vs. human baseline. — *Diana:* *that* should have been week one.

### Learning loop / moat
31. **What compounds?** *Priya:* validated-outcome data — did the client act, did it
    work — feeding a cross-client prior. — *Aria:* the one durable moat. Everyone
    note it.
32. **Is that prior legal?** *Sam:* with privacy controls. — *Jared:* "with privacy
    controls" won't survive an enterprise infosec review. Have you asked a GC?
    *Sam:* no. — *Jared:* red flag.
33. **How long until the moat exists?** *Priya:* dozens of validated engagements —
    years. — *Michael:* so no moat for years while giants circle.
34. **What stops McKinsey building the prior faster with more data?** *Sam:* channel
    conflict slows them. — *Reinhardt-style pushback from Jared:* conflict slows
    productizing, not internal tooling. Weak.

### Competition
35. **Microsoft ships this in Viva. You're dead?** *Sam:* they won't do interviews;
    they'll mine data. — *Michael:* which you just admitted might be enough. *Sam:*
    …tacit knowledge is our edge. — *Michael:* you keep saying that like a prayer.
36. **Palantir bolts interviews onto Foundry?** *Sam:* they're enterprise-heavy, slow
    on this niche. — *Diana:* they also out-deploy anyone. Real threat.
37. **OpenAI/Anthropic build the agent?** *Priya:* they won't focus on this vertical.
    — *Diana:* correct short-term; means the agent isn't your moat.
38. **What can competitors NOT copy?** *Priya:* the validated-outcome dataset and
    earned trust. — *Garrett:* both slow and services-heavy. You okay being a
    services company for three years? *Sam:* …if that's the path, yes. — *Garrett:*
    good, because it is.

### Sales / GTM / Consulting
39. **Who signs the check?** *Sam:* a CIO or a Head of Transformation. — *Jared:* have
    you met one? *Sam:* no. — *Jared:* how do you know they'll buy? *Sam:* we don't. —
    *Jared:* so your GTM is a hypothesis with zero data.
40. **Arm consultants or replace them?** *Sam:* long-term replace, short-term arm
    internal teams. — *Garrett:* pick ONE for the next six months. *Sam:* arm internal
    transformation teams. — *Garrett:* good, decisive. Hold that.
41. **First ten customers — how, specifically?** *Sam:* founder network, warm intros.
    — *Jared:* fine for two. Then what? *Sam:* …we haven't figured out repeatable
    acquisition. — *Michael:* nobody has at seed; but you haven't done the *two* yet.
42. **What's the sales cycle?** *Jared* (answering himself): 6–18 months, security +
    legal + works council. Do you understand that will bankrupt you if you don't land
    a fast lane? *Sam:* we're learning that now. — *Jared:* in the room. Not great.
43. **What do you do when the middle manager sabotages the pilot to hide their
    dysfunction?** *Sam:* …we hadn't modeled the politics. — *Garrett:* the politics
    *are* the business.
44. **Employees won't trash their boss to a corporate AI. Response?** *Priya:*
    anonymity, aggregate sourcing, projective questions. — *Michael:* and the same
    anonymity makes the exec distrust it. You've built a paradox. *Priya:* we know;
    we'd solve it with aggregate statistical sourcing. — *Diana:* unproven.

### Economics / Scaling / Hiring
45. **What's the value metric — per employee, per engagement, per decision?** *Sam:*
    unclear. — *Jared:* "unclear pricing" at seed is acceptable; "haven't thought
    about it" is not. Which is it? *Sam:* we've thought, not decided.
46. **Gross margin at scale?** *Sam:* SaaS-like eventually, services-heavy now. —
    *Jared:* so blended-ugly for years. Own that.
47. **Default alive on the standard deal?** *Sam:* if we stay small and land 3 design
    partners, yes. — *Garrett:* okay.
48. **First hire after YC?** *Sam:* an ML engineer. — *Michael:* WRONG. Your first
    hire is a customer or a salesperson, not another builder. *Sam:* …you're right.
    — *Michael:* remember you said that.
49. **What would you spend the $500k on?** *Sam:* engineering and pilots. — *Michael:*
    cut engineering to zero new hires. Pilots and travel.
50. **How fast do you ship?** *Priya:* we built a lot fast. — *Diana:* you built the
    *wrong* lot fast. Different skill.

### Execution / failure modes
51. **What's the #1 thing that kills you?** *Sam:* we keep building instead of
    selling. — *Garrett:* self-aware. Does self-aware translate to different
    behavior? *(unanswered — the whole bet)*
52. **#2 killer?** *Priya:* employees won't be honest and execs won't trust it. —
    *Michael:* the paradox again. It may be unsolvable. *Priya:* we think aggregate
    sourcing solves it. *Michael:* "think."
53. **#3 killer?** *Sam:* Microsoft/exhaust makes interviews unnecessary. — *Diana:*
    plausible.
54. **If you fail, it'll be because…?** *Sam:* we fell in love with the architecture.
    — *Garrett:* you're describing your present tense.
55. **Would you delete the drift engine, the official-org model, the epistemology
    build, tonight, if we asked?** *Sam:* …yes. *Priya:* (hesitates) the epistemology
    hurts to shelve, but yes. — *Aria:* that hesitation is the honest tell. *Garrett:*
    coachable, but the reflex is to keep.
56. **If a customer says "just give me a survey and a dashboard," what do you do?**
    *Sam:* build the survey and learn. — *Michael:* good. That's the right instinct,
    finally.
57. **What will you have proven in 90 days?** *Sam:* that employees give an AI more
    truth than a survey, and that one exec acted on the output. — *Garrett:* that is
    exactly the right 90-day goal. Why isn't it already running?
58–100. *(Rapid fire, compressed — pattern held throughout:)* on **research
depth, cognitive architecture, belief updating, hypothesis-driven interviewing,
contradiction typing** the founders were fluent, precise, occasionally brilliant; on
**users, pricing, procurement, first-ten-customers, the politics of the buyer, the
anonymity paradox, and repeatable acquisition** they were vague, theoretical, and
visibly less energized. The interview's single clearest signal was **not any one
answer — it was the delta in their body language between "explain your epistemology"
(alive) and "describe your last customer conversation" (deflated).**

**Closing question — Garrett:** *If we fund you, what changes Monday?* *Sam:* we stop
building, delete the platform, and run 20 real interviews and 10 buyer conversations
in three weeks. *Priya:* and we shelve the epistemology as R&D. — *Garrett:* if you
mean that, there's a company here. If you drift back to the graph in a month, there
isn't.

---

## PHASE 4 — Private partner discussion (founders gone; no diplomacy)

**Michael:** Pass. This is a research lab cosplaying as a startup. Zero users, six
contexts, an epistemology *paper*. The single best predictor of a founder is what
they *did*, and what they did was avoid customers for months. That's not a gap you
coach out in a batch.

**Aria:** That's lazy pattern-matching and you know it. Once a decade a pair shows up
with an actual novel insight — "testimony isn't truth" is *right* and almost nobody
sees it. You'd have passed on the deep-tech companies that became the biggest wins.

**Michael:** I'd have passed on a thousand "novel insight, no customer" teams that
died, to miss the one. That's the correct trade at seed.

**Diana:** You're both overweighting the interview and underweighting the artifact.
The artifact tells me they can *build anything*. That's rare and bankable. The
problem isn't capability, it's *aim*. Aim is coachable; capability isn't.

**Jared:** Aim is *sometimes* coachable. The concerning thing isn't that they built
the wrong thing — it's *why*. They built the wrong thing because building is where
they feel safe and selling scares them. You don't fix a fear response with a batch.

**Garrett:** Here's the contradiction that decides it for me. They claim to be
customer-obsessed and they've talked to five people casually. They claim to move fast
and they spent months on architecture nobody asked for. Their *stated* values and
their *revealed* behavior are opposite. **The entire investment is a bet on whether
the interview shocked them into changing the revealed behavior.** Sam's Monday answer
was exactly right. Priya's hesitation on the epistemology was exactly wrong.

**Aria:** So fund it and force the redirect. That's literally what the batch is for.

**Michael:** Or they take our money, feel validated, and go build a seventh context.
I've watched it happen a dozen times with the smart ones. The smart ones are the
*worst* at this — they can always justify more building.

**Diana:** Counter: the smart ones are also the only ones who can build the eval and
the hybrid signal fast once redirected. A mediocre team told to "go run 20
interviews and measure confabulation" produces mush. This team produces a real
answer in three weeks.

**Jared:** Nobody's addressed that the *business* might be unfundable even if they
execute perfectly. Services-led, 6–18 month procurement, anonymity paradox,
Microsoft downhill with distribution. Suppose they're flawless — is the *shape*ever
venture-scale? I'm not convinced the market lets a startup win here.

**Aria:** The prior is the answer to that. If they accumulate validated-outcome data
across engagements, that's a Palantir-shaped moat no giant can shortcut.

**Jared:** "If." Years away, maybe illegal.

**Garrett:** Everyone's right, which is why it's a real decision. Summarize the
cruxes: (1) coachability — will they actually redirect, (2) the anonymity paradox —
solvable or fatal, (3) shape — venture-scale or lifestyle consultancy. We can't
resolve 2 and 3 today. We *can* structure around 1.

**Michael:** Then the only honest position is conditional. Not a clean yes.

---

## PHASE 5 — Independent investment memos

**Garrett** — *Thesis:* elite founders + generational why-now; the batch installs the
customer discipline they lack. *Biggest risk:* they don't change the revealed
behavior. *Expected outcome:* wide variance — either a real company or a beautiful
zero. *Deal:* standard. *Confidence:* 60% invite-worthy, 45% it works with us.

**Michael** — *Thesis:* none until they show user contact. *Biggest risk:* founder
personality, not fixable in 12 weeks. *Expected outcome:* dies as a research project.
*Deal:* pass, revisit with 5 paying pilots. *Confidence:* 65% they don't redirect.

**Jared** — *Thesis:* real pain, brutal shape; only fundable if a fast-lane buyer
exists. *Biggest risk:* enterprise physics (procurement, legal, margin) plus the
anonymity paradox. *Expected outcome:* base case is a boutique consultancy, not a
rocket. *Deal:* conditional. *Confidence:* 55% it never escapes services.

**Diana** — *Thesis:* rare builders with the wrong aim; aim is the cheap thing to fix.
*Biggest risk:* they never measure whether the interview works. *Expected outcome:*
if they build the eval, they'll know within one batch if it's real — which is exactly
what you want from a seed check. *Deal:* standard, with a hard eval milestone.
*Confidence:* 55%.

**Aria** — *Thesis:* the one genuinely differentiated deep-tech seed in the pile; the
testimony-weighting insight + validated-outcome prior is a decade-defining moat if it
compounds. *Biggest risk:* five years early; moat may be illegal. *Expected outcome:*
low-probability, enormous-magnitude. *Deal:* standard, high conviction on magnitude.
*Confidence:* 35% it works, but the 35% is a unicorn.

---

## PHASE 6 — Competitive thought experiment: if a giant launches it

- **OpenAI launches it.** Groundwork survives *short-term*. OpenAI won't do the
  unglamorous enterprise-vertical, forward-deployed, legal-heavy work; it's a
  platform company, not a discovery-consultancy. But it proves the agent isn't a
  moat. **Survives on focus.**
- **Microsoft launches it (in Viva).** Groundwork is in serious danger. Microsoft has the
  data (Graph), the distribution (every enterprise), and can bundle at zero marginal
  price. Groundwork's only survival is the thing Microsoft won't do: *interview humans for
  tacit knowledge* and *forward-deploy trust.* If tacit-knowledge value is real,
  Groundwork lives in the gap; if data-only is "good enough," Groundwork dies. **Coin flip,
  and it's the existential one.**
- **Palantir launches it.** Dangerous. Same forward-deployed DNA, more trust, more
  security clearance, existing enterprise footprint. Groundwork survives only by being
  faster and cheaper for the mid-market Palantir ignores. **Survives by going
  down-market and fast.**
- **McKinsey launches it (internal).** Doesn't kill Groundwork directly (won't productize
  externally — channel conflict) but *neutralizes the consulting channel* and
  validates the category, inviting others. **Survives, but loses a channel.**

**Verdict:** Groundwork survives every giant *except possibly Microsoft*, and only by
owning the two things giants structurally won't: **tacit-knowledge elicitation** and
**forward-deployed trust.** If neither is a real edge, no strategy saves it.

---

## PHASE 7 — Company evolution

**6 months**
- *Best:* deleted the platform; ran 40 real interviews; proved employees give ~2×
  more actionable signal than a survey; one exec acted; two paid pilots. Fundable
  seed→A story.
- *Base:* ran ~15 interviews; mixed candor results; one warm pilot stalled in legal;
  still debating the buyer. Alive, unproven.
- *Worst:* built a seventh context; ran 3 interviews; no pilots; "we're getting the
  foundation right." Default-dead.

**2 years**
- *Best:* forward-deployed with 8–12 mid-market logos; a repeatable AI-opportunity-
  assessment product; early validated-outcome dataset; $2–4M ARR, services-heavy but
  productizing.
- *Base:* a respected boutique doing high-touch discovery for a handful of clients;
  ~$1M revenue; not obviously venture-scale; deciding whether to become a consultancy
  or push product.
- *Worst:* dead, or acqui-hired for the founders.

**5 years**
- *Best:* the system-of-record for "how work actually happens" in the mid-market;
  proprietary validated-outcome prior that makes each engagement cheaper and sharper;
  the interview is one signal in a hybrid intelligence layer; $30–60M ARR; a real
  moat via data + trust. Possible category leader.
- *Base:* a profitable, ~$10–20M, forward-deployed org-intelligence firm — a good
  company, not a fund-returner; perpetually one Microsoft feature from pressure.
- *Worst:* footnote; the insight was right but the incumbents or exhaust-mining took
  the value.

**10 years**
- *Best:* the org-intelligence layer that consultancies and enterprises both run on;
  the compounding prior is a genuine moat; acquired by or competing with a Palantir.
- *Base:* absorbed into a larger platform; the team's testimony-modeling IP lives on
  inside someone else.
- *Worst:* forgotten; a cautionary tale about brilliant founders who out-thought their
  own go-to-market.

---

## PHASE 8 — Six-month experiments, ranked by expected information gain

The metric: how much each result *collapses the variance* on P(company works). Run
top-down; stop funding the next round if the top three come back weak.

1. **E1 · Candor delta (HIGHEST EIG).** Do employees give an AI interviewer
   materially more truthful, actionable signal than a well-designed anonymous survey,
   measured against a known-ground-truth pilot? *Why #1:* if false, there is no
   company, and nothing else matters. Cheapest kill-shot. Binary, load-bearing.
2. **E2 · Decision impact / willingness-to-pay.** Put outputs in front of 5 real
   executives; does *one decision change*, and will *one* sign a paid pilot? *Why #2:*
   collapses the entire demand-side uncertainty; distinguishes "interesting" from
   "revenue."
3. **E3 · Extraction fidelity / confabulation rate.** Blind-score AI-extracted
   insights vs. a senior consultant's from identical transcripts. *Why #3:* the
   trust ceiling; a high confabulation rate caps everything downstream.
4. **E4 · The anonymity-paradox resolution.** Can aggregate statistical sourcing make
   findings *both* candor-preserving *and* exec-credible? *Why #4:* the one
   contradiction that could be structurally fatal; needs an early read.
5. **E5 · Legal/works-council viability.** One real GC + one EU works-council read on
   the deployment. *Why #5:* a hard gate on TAM; cheap to test, expensive to ignore.
6. **E6 · Wedge willingness-to-pay in one segment.** Is there a specific function ×
   industry with a live budget and a fast-lane buyer? *Why #6:* determines whether GTM
   is possible at all before procurement kills them.
7. **E7 · Interview-vs-exhaust complementarity.** Does combining interviews with light
   digital exhaust beat either alone (and fix identifiability)? *Why #7:* determines
   long-run defensibility vs. Microsoft; important but not immediately existential.

*Behavioral meta-experiment (run silently): do the founders actually delete the
platform and go do E1–E2? Their choice in month one is higher-EIG about the
**team** than any of the above.*

---

## PHASE 9 — Final vote

- **Garrett — Accept with conditions.** Elite founders, real why-now; I'll bet on
  redirect, but the conditions are the investment.
- **Michael — Reject.** The revealed behavior is the tell; I don't fund people into a
  personality change. (Willing to be outvoted; will say "I told you so" or "I was
  wrong" honestly.)
- **Jared — Accept with conditions.** Only because E1/E2 are cheap enough that we buy
  a real answer for little money; the business shape still worries me.
- **Diana — Accept with conditions.** Fund the eval, not the vision. If E1/E3 come back
  weak, we don't do the A, no hard feelings.
- **Aria — Accept.** The magnitude case is too rare to pass; I'll wear the downside.

**Tally: 3 Accept-with-conditions, 1 Accept, 1 Reject → ACCEPT WITH CONDITIONS.**

### Consensus memo

**Decision:** Standard deal, **accepted with hard, written conditions.** This is a
bet on two exceptional founders and a real *why-now*, explicitly *not* on the company
as presented. We are funding a redirect and buying a cheap answer to an existential
question.

**Conditions (non-negotiable, reviewed at week 4 and week 8):**
1. **Delete the platform.** Drift, official-org, identity resolution, synthesis layer,
   the six-context architecture → one thin substrate. Shelve the epistemology as R&D.
2. **Run E1 and E2 within 30 days.** 20+ real interviews; 5+ real exec conversations;
   one paid pilot attempted.
3. **First hire is commercial, not engineering.** No new builders until there is a
   paying pilot.
4. **Pick the wedge and the buyer and hold them** (arm internal transformation teams;
   one function × one industry).
5. **Confront the anonymity paradox** with a concrete aggregate-sourcing design before
   Demo Day.

**The dissent, preserved (Michael):** "The smart ones are the best at rationalizing
more building. We will know by week 4 whether this was founder-redirect or
founder-theater. If they show up to office hours with a seventh abstraction instead
of 20 transcripts, we cut losses and treat the check as tuition."

### If this company succeeds, why exactly will it succeed?

Because the founders *stopped out-thinking the customer*, and it turned out the one
non-obvious thing they were right about — **that a well-run AI interview surfaces
tacit, enacted truth that no amount of digital exhaust or survey can reach** — was
true and valuable enough that executives paid to act on it. They used high-touch
early engagements to accumulate a **proprietary validated-outcome dataset** — did the
client act, did it work — and that dataset compounded into a prior no competitor
could rent or shortcut. The moat was never the model or the graph or the
epistemology. **The moat was earned trust plus compounding validated outcomes, built
in a niche the giants were too big to stoop for.** They won because they were finally
as relentless about customers as they had been about architecture.

### If this company fails, what will most likely kill it?

**Most likely (≈50%): the founders themselves.** They drift back to the beautiful,
buildable problem, ship a seventh abstraction instead of a fortieth interview, and
run out of money having perfected a system no one bought. The revealed behavior wins.

**Second (≈30%): the anonymity paradox proves structural.** Employees won't be candid
enough, or the aggregate findings never become credible enough for an executive to
bet a reorg on — and the product is forever "interesting, not trusted."

**Third (≈20%): incumbent obsolescence.** Microsoft/Palantir/exhaust-mining make
interview-derived intelligence a commodity feature before Groundwork's trust-and-data
moat compounds, and distribution beats depth.

*The kindest and most useful thing we can tell ourselves about this deal: the check
is cheap, the founders are elite, and by week 8 the truth will be undeniable in
either direction. We are not buying certainty. We are buying a fast, honest answer —
and betting that if the answer is yes, these two are among the few who could build
it.*
