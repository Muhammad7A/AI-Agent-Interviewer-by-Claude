# Ontora MVP — Product Design

> **The whole MVP exists to answer one question:** *Can Ontora help a consultant
> get useful organizational truth faster and more reliably than doing the
> interviews by hand?* Everything that does not serve that question is deleted.
> Text-first. Narrow but sharp. It should not try to look bigger than it is.

---

## 1. Product thesis (the narrative)

A consultant lands a discovery engagement. Today that means two weeks of scheduling,
sitting through 15 interviews, taking messy notes, and synthesizing them into a deck
on a Sunday night — and the quality depends entirely on how good that consultant is
and how honest each employee felt like being.

Ontora replaces the *labor*, not the *judgment*. The consultant defines what they
need to learn and who to ask. Ontora runs thoughtful, adaptive **text** interviews
with each employee — private, unhurried, and often more candid than a face-to-face
because people will type what they won't say aloud. Ontora reads every transcript,
proposes candidate findings — bottlenecks, contradictions, automation
opportunities — and shows the **exact quotes** behind each one and **how many
independent people** said it. The consultant reviews in an afternoon what used to
take a weekend: accept, edit, reject, merge. The output is a clean, evidence-backed
report the consultant presents as their own work — because the judgment *is* theirs.

**AI does the listening and the first draft. The consultant does the thinking and
owns the truth.** That division is the product.

---

## 2. The one thing we're proving (and what we are NOT proving)

We are proving: **time-to-useful-truth beats manual, and the consultant trusts the
result.** We are *not* proving: that Ontora replaces consultants, models the whole
org, detects drift, or learns across clients. Those are later. If the core loop
doesn't beat a legal pad and a smart associate, nothing downstream matters.

---

## 3. The four roles and the trust architecture

Trust is the entire risk, so we design roles around *who trusts what*.

| Role | In the MVP they are… | What earns their trust |
|---|---|---|
| **Consultant / analyst** | The real user. Lives in the console. | Every finding drills to the raw quote; nothing is "true" until they validate it; the AI is visibly a *drafter*, not an oracle. |
| **Company admin / project owner** | Almost nothing. Provides the employee list; authorizes the engagement over email. **No portal.** | A one-page, plain-language description of what will be asked and what will (and won't) be shared. |
| **Employee interviewee** | A guest with a link. Never logs in, never sees the console. | A blunt, honest consent screen: *the external consultant sees your words in confidence; your employer sees only anonymized, aggregated patterns; you can skip anything and stop anytime.* |
| **Executive / decision maker** | Does **not** log in. Reads the exported report. | A decision-first report that leads with actions, shows the evidence, and is honest about what it does *not* yet know. |

**The load-bearing trust decision:** the *external consultant* is the confidential
third party (as in real consulting). The *employer/exec* only ever receives
anonymized aggregates. This is what lets an employee be candid *and* lets an exec
act on the result — it resolves the anonymity paradox by putting a trusted human in
the middle, not by pretending anonymity and credibility can both be absolute.

---

## 4. Target user journey (text flow diagram)

```
CONSULTANT                              EMPLOYEE                         EXECUTIVE
─────────                              ────────                         ─────────
create engagement
  → define focus (what to learn)
  → paste invitee emails + roles
send invitations ───────────────────► receives one link
                                       reads consent / trust screen
                                       completes ~15-min text interview
                                       (AI adapts, hypothesis-led,
                                        can skip / stop)
monitor progress  ◄─── completions ─── thank-you + "what happens next"
  (N of M complete)
[when enough complete]
review candidate findings
  → each: statement · N-of-M · quotes · confidence
  → accept / edit / reject / merge
  → drill to full transcript on any quote
build synthesis
  → Bottlenecks · Contradictions · Opportunities
generate report ──────────────────────────────────────────────────────► reads report
export PDF / share read-only link                                         (actions first,
                                                                           evidence on demand,
                                                                           uncertainty shown)
```

---

## 5. Information architecture & navigation (deliberately tiny)

Two surfaces and one artifact. That's it.

- **Consultant console** — a single left rail with exactly two items: **Engagements**
  and, inside an engagement, three tabs: **Interviews · Findings · Report.** No
  dashboard. No settings page (account is a name + magic-link email). No admin panel.
- **Employee interview** — a standalone, distraction-free chat page reached only by
  invite link. No navigation at all.
- **The report** — an export (PDF) and a read-only shareable link. Not an app.

If a screen isn't Engagements, an engagement's three tabs, the interview, or the
report — it does not exist in the MVP.

---

## 6. Screen inventory

**Consultant console (7 screens)**
1. Engagements list (home)
2. Create engagement
3. Engagement · **Interviews** tab (setup + monitor)
4. Engagement · **Findings** tab (review)
5. Engagement · **Synthesis** view (inside Findings)
6. Engagement · **Report** tab (assemble + export)
7. Transcript reader (a panel, opened from any quote)

**Employee interview (3 screens)**
8. Consent / trust intro
9. The interview (chat)
10. Thank-you / what-happens-next

**Executive artifact (1)**
11. The report (PDF / read-only link)

Eleven surfaces total. Anyone proposing a twelfth must delete one first.

---

## 7. Screen-by-screen behavior (with empty / loading / error states)

**1 · Engagements list.** A simple list: name, client, status ("3 of 9 interviews").
*Empty:* one line — "No engagements yet" — and a single **Create engagement** button.
*Loading:* skeleton rows. *Error:* "Couldn't load your engagements — retry."

**2 · Create engagement.** Four fields, one screen: engagement name, client company,
**focus** (a free-text prompt: "What do you need to learn?" — e.g. *"Where does the
finance team lose time, and what could AI automate?"*), and invitees (paste
emails, optional role label per person). No wizard, no steps. *Error:* inline
validation only ("add at least one invitee").

**3 · Interviews tab.** Top: a **Send invitations** button and a plain progress line
("4 of 9 completed · 2 in progress · 3 not started"). Below: the invitee list with
status and a **Resend** action. Clicking a completed row opens the **Transcript
reader** (screen 7). *Empty (pre-send):* "Ready to invite 9 people. They'll each get
a private link." *Loading:* per-row status shimmer. *Error (send failed):* row-level
"Couldn't send — retry," never a blocking modal.

**4 · Findings tab.** The core screen. A ranked list of AI-proposed findings. Each
card: a one-line **statement**, a **type** chip (Bottleneck / Contradiction /
Opportunity), a strength line (**"7 of 9 people · Medium confidence"**), and 2-3
**evidence quotes** (anonymized) that expand to more. Actions per card: **Accept ·
Edit · Reject · Merge.** A quote links to the full transcript (screen 7). Filter by
type; nothing else. *Empty (not enough interviews):* "Findings unlock after 3
interviews complete — 1 so far." *Loading (analysis running):* see §8. *Error
(analysis failed):* "Analysis didn't finish — re-run" with the partial results still
shown.

**5 · Synthesis view.** The consultant's validated findings, auto-grouped into three
sections — **Bottlenecks · Contradictions · Opportunities** — each item carrying its
evidence and confidence. This is a *reading* view of what they've accepted; editing
happens in Findings. It is the draft of the report.

**6 · Report tab.** A clean document preview assembled from validated findings:
executive summary (top 3-5 + recommended actions), findings with evidence,
contradictions, opportunities, and a short **"What we're confident about / what needs
more discovery"** honesty box. The consultant can edit the prose inline. Buttons:
**Export PDF · Copy share link.** *Empty:* "Validate some findings first — your report
builds itself from what you accept."

**7 · Transcript reader (panel).** Opens over the current screen. The full interview,
with the cited passage highlighted. A confidentiality reminder in the header:
*"Visible to you as the engagement consultant. Not shared with the client."*

**8 · Consent / trust intro (employee).** Plain language, no legalese wall: who's
asking, why, ~15 minutes, *what's shared and what isn't*, "skip anything, stop
anytime," one **Begin** button. This screen wins or loses candor before a word is
typed.

**9 · The interview (chat).** A calm, single-column text conversation. One question
at a time, warm and specific. A quiet progress hint ("about halfway"). A **Skip this
one** affordance always visible. Typing indicator while the AI composes. *If the
respondent is terse or guarded:* the AI softens, reframes, or offers a projective
question — it never nags. *Error (model hiccup):* "One moment —" then retry silently;
never lose the respondent's text.

**10 · Thank-you.** "Thank you — your perspective genuinely matters. Your individual
answers stay confidential; only anonymized patterns are shared." Close.

**11 · The report.** See §12.

---

## 8. Empty / loading / error philosophy (one rule)

Every state must say **what's true, why, and the one next action** — in a sentence.
No spinners without words. No dead ends. The two states that matter most:

- **Analysis running** (after interviews complete): a short, honest progress line —
  *"Reading 9 interviews and drafting findings… this takes a minute or two."* This is
  the moment the consultant decides the product is magic or vaporware; it must feel
  deliberate, not stuck.
- **Not enough data yet:** never show thin, embarrassing findings. Gate the Findings
  tab until N≥3 and say so plainly.

---

## 9. Interview flow (the crown jewel — must feel premium)

This is the one experience that must feel genuinely excellent, because candor is the
whole game.

1. **Consent** (screen 8) — honesty buys openness.
2. **Warm open** — a low-threat "grand tour" question: *"To start — walk me through
   what a normal Tuesday looks like for you."* No interrogation energy.
3. **Adaptive middle** — hypothesis-led (per the Interview Intelligence Engine, used
   as-is): follow friction, ask for the *last specific time* something went wrong,
   quantify lightly, chase workarounds, gently surface espoused-vs-enacted. Skippable
   throughout.
4. **Close** — reflect back one thing ("so the biggest time-sink sounds like X — did
   I get that right?"), invite anything missed, thank them.
5. **~12-18 turns, ~15 minutes.** Text only.

MVP simplifications that are *invisible* to the employee: the "belief state" and
information-gain scoring can be a well-designed prompt with a short running summary,
not a formal engine. It must *feel* adaptive; it need not be optimal.

---

## 10. Consultant review flow (where trust is earned)

The consultant's loop is: **skim → drill → decide → assemble.**

- **Skim** the ranked findings (strongest evidence first).
- **Drill** into quotes; one click to the full transcript. The "7 of 9 people
  independently said this" line is the credibility payoff — surface it prominently.
- **Decide:** Accept / Edit / Reject / Merge. Editing a finding's wording is
  first-class (the consultant makes it *theirs*). Every finding carries a visible
  **AI-proposed → Consultant-validated** state so provenance is never ambiguous.
- **Assemble** happens automatically: accepted findings flow into the Synthesis and
  Report. The consultant never "builds a deck" — they curate, and the document
  writes itself.

Design tension to respect: **do not drown them.** Cap the initial findings list
(e.g. top ~15, ranked), with "show weaker signals" as an opt-in. Review fatigue kills
the time-savings promise.

---

## 11. Executive output flow (the artifact that sells the company)

The exec never logs in. They receive a **report** — PDF or read-only link — that must
look and read like premium consulting output:

- **Leads with decisions:** top 3-5 findings, each with a recommended action.
- **Evidence on demand:** anonymized quotes under each finding; "based on N of M
  interviews."
- **Honest uncertainty:** a short box separating *"confident enough to act"* from
  *"needs more discovery."* This honesty is counterintuitively what makes an exec
  trust the confident parts.
- **A one-line method note:** "AI-conducted interviews, consultant-validated" — so the
  exec knows a human stands behind it.

If this artifact isn't good enough to forward to a CEO, the MVP has failed regardless
of how the app works.

---

## 12. MVP feature list (build these)

1. Magic-link auth for the consultant (no passwords, no roles).
2. Create engagement: name, client, focus prompt, pasted invitee list.
3. Email invitations + one manual **Resend**.
4. Employee consent screen + adaptive **text** interview + thank-you.
5. Per-interview transcript storage + a transcript reader.
6. Analysis: per-interview extraction → cross-interview aggregation into ranked
   candidate findings (Bottleneck / Contradiction / Opportunity), each with quotes,
   an N-of-M count, and a simple High/Medium/Low confidence.
7. Findings review: Accept / Edit / Reject / Merge + evidence drill-down + AI→Human
   provenance.
8. Auto-assembled Synthesis + editable Report + PDF export + read-only share link.

That is the entire product. Eight things.

---

## 13. Non-goals (do NOT build)

- No knowledge graph, org model, drift, or official-vs-discovered anything in the UI.
- No dashboards, charts, or analytics views.
- No admin portal, no company-side login, no employee accounts.
- No settings, permissions, or roles beyond "the consultant."
- No integrations (HR, Slack, SSO, calendar).
- No voice, no video, no multi-language (English only).
- No scheduling/reminder campaigns (one manual resend is enough).
- No billing, no team collaboration, no real-time multiplayer.
- No cross-client learning, no confidence math beyond corroboration counts.
- No mobile-optimized console (desktop only; the *interview* must work on mobile).

---

## 14. What should be FAKE or MANUAL (not automated) in the MVP

- **Cross-interview fusion** is a single LLM pass over all transcripts. It looks
  automated; it's one prompt.
- **Company authorization / admin** is an email and a PDF, not a portal.
- **The invitee list** is pasted by the consultant (given to them by the client). No
  HR sync.
- **Confidence** is corroboration count + consultant judgment, not the 6-factor model.
- **"Improves over time" / the cross-client prior** — absent. Do not fake it in copy
  either; don't promise learning we haven't built.
- **Report styling** is one good template, not a builder.
- **Even the whole console can wait:** in week 1-2, run interviews via hand-generated
  links and review findings in a shared doc. Prove the value core before the CRUD.

---

## 15. What must feel PREMIUM even in the MVP (spend the polish here)

1. **The employee interview** — tone, pacing, feeling heard. This is where candor is
   born; a form-like experience kills the company.
2. **The evidence drill-down** — quote → transcript in one click. The consultant's
   "I can trust this" moment.
3. **The "N of M independent people" credibility line** — the single most persuasive
   pixel in the product.
4. **The exported report** — it's the thing shown to the buyer. It must look like
   $50k of consulting, not a SaaS export.

Everything else can be plain, gray, and utilitarian. Concentrate all craft on these
four.

---

## 16. Success metrics (does Ontora deserve to exist?)

**Primary (the thesis):**
- **Time-to-useful-truth vs. manual** — consultant's self-reported hours saved on a
  real engagement. Target: ≥50% less than their manual baseline.
- **Usefulness & novelty** — for each finding: "useful? true? would you have found it
  yourself?" We want a healthy share of *"useful AND I might have missed it."*

**Trust / quality:**
- **Findings acceptance rate** — accepted / proposed. Healthy band ~40-70%. Too high =
  not challenging; too low = noise.
- **Confabulation rate** — findings rejected as unsupported by their own quotes. Must
  be low; this is the trust ceiling.

**Employee side (candor proxy):**
- **Interview completion rate** (target high; drop-off = distrust or fatigue).
- **Candor signal** — consultant judgment: "did employees reveal things a survey
  wouldn't?"

**The ultimate:**
- **Did an executive act on, or pay for, the report?** One real yes is worth more than
  all the above.

---

## 17. Failure modes & UX blind spots (brutally)

- **Guarded/terse employees → shallow transcripts → weak findings.** The interview
  must degrade gracefully and the analysis must *refuse to manufacture depth* from
  thin input. Blind spot: a beautiful UI over empty answers.
- **Review fatigue.** Too many candidate findings and the time-savings evaporate. Rank
  hard, cap the list.
- **Anonymity confusion.** If the employee is unsure who sees their words, they clam
  up. The consent screen is a product-critical surface, not boilerplate.
- **Overconfident reports on thin evidence.** With N=5, everything is anecdotal.
  Uncertainty must be honest or the first exec who gets burned kills the referral.
- **Contradiction over-detection.** The model will invent "tensions" to look smart.
  Bias the analysis toward *precision over recall* on contradictions.
- **Consultant rejects everything.** Even then the product must have saved them time
  (transcripts + first-draft synthesis). If it doesn't, the thesis fails.
- **Low N from ignored invites.** Email deliverability and a lukewarm client contact
  can starve the whole engagement. The invite copy and the client's framing matter as
  much as the app.
- **The "so what" gap.** Findings that are true but not *actionable* ("communication
  could be better") are worthless. The analysis must push toward specific, leverable
  findings, or the report reads like a horoscope.

---

## 18. Priority order for building (learn fastest, in order)

**Build the value core before the wrapper.** Riskiest, most-important first.

1. **The interview** (weeks 1-2) — a single chat page + the adaptive prompt. Test on
   ~10 real employees *before building anything else.* If transcripts are shallow,
   stop; nothing downstream can save it. *(This is the YC memo's E1.)*
2. **Extraction + synthesis** (week 2-3) — transcripts → ranked findings with quotes
   and N-of-M. Test confabulation against a consultant's own read. *(E2/E3.)*
3. **Findings review UI** (week 3-4) — accept/edit/reject/merge + evidence drill. The
   trust surface.
4. **Engagement setup + invites** (week 4-5) — the CRUD wrapper. Fine to fake with
   hand-made links until now.
5. **Report assembly + export** (week 5-6) — the artifact that sells.

If forced to cut: keep 1-3, hand-run 4, and deliver 5 as a hand-formatted doc. The
irreducible core is **interview → findings → evidence-backed review.** That trio, and
only that trio, answers whether Ontora deserves to exist.

---

## 19. The principle to hold

The temptation will be to make the console look like a real product — dashboards,
charts, an org map, an admin area. **Resist all of it.** The best version of this MVP
is one consultant saying, after one real engagement: *"That saved me a week, and two
of those findings I'd have missed."* Everything in this document exists to make that
sentence possible, and everything not in this document exists to prevent it.
