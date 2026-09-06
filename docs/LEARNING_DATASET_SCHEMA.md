# Groundwork Learning Dataset — Schema

> The memory system that makes Groundwork smarter over time. Not storage tech, not UI —
> the *structure of the data* required to learn which questions uncover truth, which
> outputs consultants trust, and which insights create value. Its one load-bearing
> rule: **never collapse the four layers.**

---

## 1. Dataset philosophy

Six commitments, each preventing a way the data would otherwise lie to us.

1. **Four layers, never fused.** *Testimony* (what was said) ≠ *Interpretation* (what
   the AI inferred) ≠ *Validation* (what the consultant judged) ≠ *Outcome* (what the
   business did and what happened). Each is stored separately, with its own provenance
   and truth-status, and references the layer below by identity. Fusing them destroys
   credit assignment — the entire point of the dataset is to trace *this question →
   this inference → this human judgment → this outcome.*
2. **Append-only, event-sourced.** The raw event log is the source of truth; snapshots
   and labels are *derived projections* recomputed as understanding improves. Nothing
   is edited in place. This is what lets us "learn new things later" — a better label
   is a re-derivation over old events, not a migration.
3. **Preserve uncertainty and perspective.** Every interpretation carries confidence
   (with second-order/fragile flags), and every testimony carries the source's
   *standpoint* and estimated *candor*. Truth is not directly observable; the schema
   records the *view*, never a bare "fact."
4. **Provenance on everything.** Every AI record carries `engine_version` (model +
   prompt-suite + policy). Every human record carries the consultant. Every derived
   label carries its derivation-method version. Without this, learning and regression
   detection are impossible.
5. **Privacy is structural, not a policy.** Direct identity lives in a *severable*
   vault; the learning store holds pseudonyms and generalized attributes only. PII
   deletion must never destroy the anonymized learning signal.
6. **Retention ≠ currency.** Data is retained (for learning); a *belief's influence
   decays* with age (per the epistemology's belief decay). These are different
   mechanisms — a decay weight on labels, not deletion of records.

---

## 2. Core schema (the layered model)

```
SCOPE SPINE
  Organization ──< Engagement ──< Interview ──> (Subject, Consultant)

LAYER 1 · TESTIMONY   (immutable evidence — never edited)
  Turn ──> EvidenceRef        QAPair(question Turn ↔ answer Turn)

LAYER 2 · INTERPRETATION   (AI hypotheses — versioned, uncertain)
  BeliefStateSnapshot · FollowUpDecision · ExtractedClaim ·
  Hypothesis · ContradictionRecord · CandidateInsight

LAYER 3 · VALIDATION   (human judgment — attributed, fallible)
  ValidationEvent · ConsultantEdit · AcceptedInsight · UsefulnessRating

LAYER 4 · OUTCOME   (business reality — sparse, delayed, gold)
  DecisionLink · Outcome · PostEngagementFeedback

DERIVED LABELS   (cross-layer credit assignment — recomputable)
  QuestionValueLabel · HypothesisUtilityLabel · BeliefCalibrationLabel ·
  InsightValueLabel · StrategyOutcomeLabel

CROSS-CUTTING
  Event(log) · EngineVersion · ConsentProfile · IdentityVault(severed) ·
  TransferableAggregate
```

Reference direction is always **downward and backward in time**: interpretation cites
testimony; validation cites interpretation; outcome cites validation; labels join
across all four. No upward edits; corrections are new events.

---

## 3. Entity / field definitions

Compact. `*` = required. Attribute bags (`attrs`) are typed-but-open for
extensibility. PII never appears below layer boundaries — see §8.

### Scope spine
- **Organization** — `org_id*`; industry_bucket, size_band, region_bucket,
  consent_profile_id*, created_at*. *(No name — that's in the vault.)*
- **Engagement** — `engagement_id*`, `org_id*` (FK), focus_text*, status,
  baseline_version, `consultant_id*` (FK), started_at, ended_at, consent_scope*,
  engine_version_at_start.
- **Subject** (pseudonymized employee) — `subject_id*` (pseudonym), scope
  (`engagement`|`org`), role_family, function_bucket, seniority_band, tenure_band,
  standpoint_descriptor, consent_flags*. *(No name/email/exact title.)*
- **Consultant** — `consultant_id*` (pseudonym), experience_band, reliability_profile
  (learned; see labels).
- **Interview** — `interview_id*`, `engagement_id*` (FK), `subject_id*` (FK), mode
  (`text`), started_at, completed_at, status, `engine_version*`, turn_count,
  duration_s, signal_level (`low|med|rich`), candor_final.

### Layer 1 · Testimony (immutable)
- **Turn** — `turn_id*`, `interview_id*` (FK), sequence*, speaker
  (`interviewer|respondent`), text_ref* (→ scrubbed text store), created_at*. **Never
  edited; retractions are new Turns.**
- **QAPair** — `qa_id*`, `interview_id*`, `question_turn_id*` (FK), `answer_turn_id*`
  (FK), `decision_id` (FK → the FollowUpDecision that produced the question).
- **EvidenceRef** — `evidence_id*`, `interview_id*`, `turn_id*` (FK), char_span
  (start,end), speaker_standpoint, uttered_at. *The immutable citation everything
  upstream points to.*

### Layer 2 · Interpretation (AI, versioned)
- **BeliefStateSnapshot** — `snapshot_id*`, `interview_id*`, turn_index*,
  `engine_version*`, created_at*, payload (world_model, hypotheses[], gaps[],
  contradictions[], candor, affect, engagement, coverage, turns_remaining). *One per
  turn → the time series of the AI's mind.*
- **FollowUpDecision** — `decision_id*`, `interview_id*`, turn_index*, `snapshot_id*`
  (FK), target_ref (hypothesis/gap), move_type, policy_invoked
  (`normal|candor|specificity|contradiction|time`), is_disconfirming (bool),
  candidate_moves[] (scored alternatives, for VoI learning), `realized_turn_id*` (FK →
  Turn), `engine_version*`. **The key table for "which questions create value."**
- **ExtractedClaim** — `claim_id*`, `interview_id*`, `source_evidence_id*` (FK),
  subject/predicate/object, target_layer, specificity (`low|med|high`), sourcing
  (`firsthand|hearsay|speculation`), register (`espoused|enacted`),
  extraction_confidence, `engine_version*`.
- **Hypothesis** — `hypothesis_id*`, scope (`interview|engagement`), statement, type,
  support_evidence[] (FKs), against_evidence[] (FKs), confidence (score + factors +
  fragile), value_estimate, status
  (`open|probing|confirmed|refuted|parked`), discriminating_question,
  `engine_version*`, created_at. *State changes recorded as Events (§5).*
- **ContradictionRecord** — `contradiction_id*`, scope, evidence_a* (FK), evidence_b*
  (FK), kind (`conflict|variation|complementary|sourcing|sentiment`), treat_as_finding
  (bool), `engine_version*`.
- **CandidateInsight** (AI-proposed finding) — `insight_id*`, `engagement_id*`,
  interview_ids[], statement, type, supporting_evidence[] (FKs), register,
  ai_confidence (band+score+fragile), n_of_m, decision_relevance_estimate,
  `engine_version*`, created_at. **Still interpretation — not truth.**

### Layer 3 · Validation (human)
- **ValidationEvent** — `validation_id*`, target_type (`candidate_insight|hypothesis|
  claim|contradiction`), `target_id*`, `consultant_id*`, action
  (`accept|edit|reject|merge|split|add`), reason, engine_version_at_review, created_at*.
  **Append-only.**
- **ConsultantEdit** — `edit_id*`, `validation_id*` (FK), `target_id*`, before_text,
  after_text, edit_distance (computed), edit_type (`wording|scope|confidence|evidence`).
- **AcceptedInsight** (human-validated) — `accepted_insight_id*`, `engagement_id*`,
  `source_candidate_insight_id` (FK, nullable if consultant-authored), final_statement,
  final_confidence (consultant-assigned), evidence[] (FKs), `consultant_id*`,
  validated_at. **The AI→human transformation is preserved via the source link.**
- **UsefulnessRating** — `rating_id*`, target_id*, `consultant_id*`, useful (likert),
  would_have_missed (bool — novelty), actionable (likert), created_at.

### Layer 4 · Outcome (business)
- **DecisionLink** — `decision_link_id*`, `accepted_insight_id*` (FK), `engagement_id*`,
  decision_desc, decided_by (pseudonym), action_taken (bool), decided_at.
- **Outcome** — `outcome_id*`, `decision_link_id*` (FK), observed_at (often months
  later), outcome_type (`implemented|abandoned|succeeded|failed|no_effect`),
  impact_measure (qual/quant), attribution_confidence (guards against confounding &
  reflexivity). *The T3 reward signal.*
- **PostEngagementFeedback** — `feedback_id*`, `engagement_id*`, source
  (`consultant|client`), overall_usefulness, time_saved_estimate,
  retrospective_calibration (were confident findings borne out), created_at.

---

## 4. Identifiers & foreign keys

- **PKs** are opaque UUIDs; `subject_id`/`consultant_id`/decided_by are **pseudonyms**
  whose real-identity mapping exists only in the **IdentityVault** (§8), never here.
- **The provenance chain (the spine of all learning):**
  `FollowUpDecision.realized_turn_id → Turn` ·
  `QAPair(question_turn ↔ answer_turn)` ·
  `ExtractedClaim.source_evidence_id → EvidenceRef → Turn` ·
  `CandidateInsight.supporting_evidence[] → EvidenceRef` ·
  `AcceptedInsight.source_candidate_insight_id → CandidateInsight` ·
  `DecisionLink.accepted_insight_id → AcceptedInsight` ·
  `Outcome.decision_link_id → DecisionLink`.
  This unbroken chain — question → evidence → inference → validation → decision →
  outcome — is what makes every "which X caused value?" question answerable.
- `engine_version` is a foreign key to **EngineVersion** on *every* interpretation
  record; `derivation_version` on every label.

---

## 5. Event structures (the source of truth)

Everything is an append-only **Event**; snapshots and labels are projections.

**Event** — `event_id*`, `event_type*`, `entity_type*`, `entity_id*`, `actor*`
(`interviewer_engine|consultant|system|client`), `occurred_at*`, `engine_version`,
`correlation_id*` (interview/engagement), `payload` (typed, versioned per event_type),
`schema_version*`.

Representative event types: `interview.turn.recorded`, `belief.updated`,
`followup.decided`, `claim.extracted`, `hypothesis.created|revised|refuted`,
`contradiction.detected`, `insight.proposed`, `insight.validated|edited|rejected`,
`insight.accepted`, `decision.linked`, `outcome.observed`, `consent.changed`,
`pii.erased`.

Because payloads are versioned and additive (new fields = new `schema_version`, old
readers ignore them), the schema **evolves without migration** — the flexibility the
constraints demand. Deletions (§9) are themselves events (`*.erased` tombstones), so
the log stays internally consistent.

---

## 6. Snapshot structures

Point-in-time projections for efficient replay and time-series learning:
- **BeliefStateSnapshot** (per turn) — replay the AI's evolving mind; supports "which
  beliefs were correct," candor trajectories, information-gain curves.
- **HypothesisTrajectory** — a hypothesis's confidence/status over turns (derived from
  `hypothesis.*` events).
- **EngagementSnapshot** — cohort state at synthesis time (all candidate insights,
  n_of_m, coverage).
All snapshots carry `engine_version` + `as_of` and are re-derivable from the event log
(they are cache, not truth).

---

## 7. Learning labels (derived, recomputable)

Labels are the *training/eval signal* — cross-layer joins, recomputed as validation and
outcome data arrive (so they sharpen over time). Each carries `derivation_version`,
`computed_at`, and a **decay_weight** (older evidence contributes less to current
priors — belief decay, not deletion).

- **QuestionValueLabel** — `label_id`, `decision_id` (FK), value_score (did the elicited
  answer trace to a validated / acted-upon insight?), attributed_from (validation/outcome
  ids). *→ which questions produce value.*
- **HypothesisUtilityLabel** — `hypothesis_id`, was_useful, was_correct,
  calibration_error. *→ which hypotheses helped.*
- **BeliefCalibrationLabel** — `target_id`, stated_confidence, realized_correctness
  (from validation/outcome). *→ feeds ECE / confidence policy.*
- **InsightValueLabel** — `insight_id`, validated, useful, would_have_missed,
  acted_upon, business_value. *→ the full value chain.*
- **StrategyOutcomeLabel** — context (role_family, candor_level, engagement_type) ×
  strategy (policy_invoked, move_type) × result (candor gained, specifics elicited,
  value produced). *→ which strategies work for which employee types.*

These labels answer every question in the brief: *most-valuable questions*
(QuestionValueLabel), *strategy × employee-type* (StrategyOutcomeLabel), *contradiction
patterns → value* (ContradictionRecord.kind × InsightValueLabel), *most informative
employees* (per-Subject aggregates of unique validated findings + candor yield),
*context → candor* (BeliefStateSnapshot.candor × context), *correct beliefs*
(BeliefCalibrationLabel), *useful hypotheses* (HypothesisUtilityLabel), *outputs → action*
(Outcome).

---

## 8. Privacy rules

- **Two-store separation.** **IdentityVault** (names, emails, exact titles, org names,
  decided_by real identity) is access-controlled, minimal, and **severable**. The
  **Learning Store** holds pseudonyms + generalized attributes only. PII never crosses
  the boundary.
- **Pseudonymize at ingestion.** `subject_id` is random; the mapping lives only in the
  vault. Default scope is **engagement-local**; org-level linking requires explicit
  consent and a resolver.
- **Generalize.** Role→family, department→function bucket, exact figures→bands. Reduces
  re-identification before data lands in the learning store.
- **Quotes are re-identifying.** Verbatim text is *engagement-visible* (the consultant
  is the confidential third party) but **not transferable** cross-client unless
  transformed/withheld. `text_ref` resolves to full text only within consented scope.
- **Consent flags** at org/engagement/subject level: (a) within-client learning, (b)
  cross-client aggregate transfer (the Π question), (c) retention window. Defaults:
  within-client = yes; cross-client = **opt-in, aggregate-only**; sensitive/distress
  records = excluded from transfer entirely.
- **Distress/sensitive tags** get stricter access and are quarantined from any learning
  transfer.

---

## 9. Retention & forgetting rules

- **Testimony (scrubbed)** retained for the consented window; the *anonymized* signal
  may persist per contract even after PII erasure.
- **Right-to-erasure:** deleting a person tombstones the vault link (`pii.erased`
  event); the severed learning records survive if anonymized and contractually
  permitted — PII deletion must not destroy learning.
- **Belief decay ≠ deletion.** Labels carry `decay_weight(age, proposition_class)`;
  structural facts decay slowly, operational facts fast (per the epistemology). Priors
  down-weight stale beliefs; the raw records remain for research and re-derivation.
- **Tombstoning, never silent removal** — every deletion is an event, so projections
  stay consistent and audits are possible.

---

## 10. Minimum viable dataset (first 10 customers)

Keep the **layer separation, provenance (`engine_version`), pseudonymization, and the
provenance chain** — these are the irreducible structural bets and cannot be
retrofitted. Drop the machinery you can add later.

**Keep (thin):** Engagement · Interview · Subject(pseudonymized) · Turn + QAPair
(testimony) · one BeliefStateSnapshot blob per interview + FollowUpDecision (even
lightweight) · ExtractedClaim/CandidateInsight with EvidenceRef · ValidationEvent +
ConsultantEdit + AcceptedInsight + UsefulnessRating · a lightweight Outcome +
PostEngagementFeedback · `engine_version` on everything.

**Defer:** full event-sourcing rigor (simple append tables are fine), the derived-label
pipeline (compute QuestionValue/InsightValue *ad hoc* by joining the four layers when
you analyze), cross-client transfer/DP, credal uncertainty richness, cross-engagement
identity resolution.

**Non-negotiable even in MVP:** four layers never fused · pseudonyms from day one ·
`engine_version` stamped · the question→evidence→insight→validation→outcome chain
intact. If you keep only those four, every later learning capability remains derivable.

---

## 11. Long-term scalable schema (research-grade)

Add, in order of leverage:
1. **Full event log as source of truth** + snapshot/label projections; re-derive labels
   retroactively as understanding improves.
2. **Versioned label-derivation pipelines** with `derivation_version` + `decay_weight`,
   feeding the learning loop: QuestionValue → policy refinement; InsightValue → candidate
   scoring; BeliefCalibration → confidence policy; StrategyOutcome → per-employee-type
   strategy selection; HypothesisUtility → sharper priors.
3. **TransferableAggregate + TransferConsent** — the Π moat as first-class data:
   question-effectiveness stats by context, calibration curves, validated dysfunction-
   pattern frequencies — **aggregate-only, DP-bounded, consent-gated, tombstonable**.
   Raw records never leave the tenant.
4. **BenchmarkRun** linkage — tie eval-harness results (golden set, gates, Value
   Density) to `engine_version`, so "is it improving or just more verbose?" is a query,
   not an argument.
5. **Longitudinal metrics** — cold-start efficiency, calibration drift, consultant
   edit-distance trend, FP-rate trend, proximity-to-human-ceiling — all derivable from
   the layered log because nothing was ever fused or overwritten.

**The whole design in one sentence:** an append-only, four-layer, provenance-stamped,
pseudonymized memory whose raw events are never fused and never edited — so that any
future question about *which testimony, filtered through which inference, trusted by
which human, produced which outcome* can be answered by a join, and the population prior
that answer feeds is aggregate, consented, and decaying — which is exactly the shape of
a moat that compounds without leaking.
