# Reliability Matrix — adversarial failure model

Status legend: **✓exec** = behavior verified by executing the real code (this investigation, mock mode); **code** = derived from reading the cited file at main `f4ee6b1`+.
Severity: P0 data-loss/security-critical · P1 feature-breaking · P2 degraded-but-usable · P3 cosmetic/edge.
`test:` references the regression test covering the row (`NEW` = added with this matrix). Fixed-in-this-investigation rows are marked **FIXED**.

Assumptions faced: unreliable providers, malformed outputs, long conversations, conflicting instructions, interrupted sessions, duplicate requests, concurrent users, partial network failures, inconsistent state, invalid API responses, rate limits, latency spikes, process restarts.

## 1. Conversation edge cases (CONV, 100)

| ID | Scenario | Expected | Current | Sev | Mitigation | Test |
|---|---|---|---|---|---|---|
| CONV-001 | Empty answer "" | refused or recorded-as-vague | recorded; `_is_vague` len<6 → vague; tier 0 | P3 | accept (honest) | code: engine.py:143 |
| CONV-002 | Whitespace-only "   " | treated as empty | `"".split()` → 0 words → vague; recorded | P3 | accept | code: engine.py:143 |
| CONV-003 | 1-char answer "k" | vague | vague; recorded | P3 | — | code |
| CONV-004 | 5-word answer | vague boundary | `len<6` → vague | P3 | — | code: engine.py:143 |
| CONV-005 | 6-word fluent nonsense | substantive (lorem-gap) | tier = pending_tier; heuristic gap, documented | P2 | live model / better scorer | code ✓exec |
| CONV-006 | Answer exactly 20000 chars | accepted | accepted (cap is `>` check) | P3 | — | NEW: web hardening |
| CONV-007 | Answer 20001 chars | refused, nothing recorded | 413 page; state intact ✓exec | P2 | cap | test_web_surface_hardening |
| CONV-008 | 100KB answer via API | refused | 413 (cap) ✓exec | P2 | cap | same |
| CONV-009 | Single 5000-char word | accepted, vague-ish | recorded; word len irrelevant to vague | P3 | — | code |
| CONV-010 | Null bytes \x00 in answer | stored safely | JSON handles \u0000; HTML esc renders | P3 | — | code: views esc |
| CONV-011 | Emoji-only answer 🙂🙃 | vague | vague (len<6) | P3 | — | code |
| CONV-012 | RTL answer (Arabic/Hebrew) | stored verbatim, rendered LTR-ctx | stored; esc; no bidi isolation → visual only | P3 | dir=auto on render | code |
| CONV-013 | CJK answer | stored verbatim | stored; tagger content-words [a-z]+ misses CJK → 0 overlap risk | P2 | CJK tokenization | code: relation.py:54 |
| CONV-014 | Zero-width chars (U+200B) | neutralized in gates | grounding canon does NOT strip ZWSP → quote with ZWSP fails exact-match → rejected | P2 | add ZWSP to canon | code: grounding._CANON ✓exec |
| CONV-015 | Combining diacritics (e ↔ é) | same-word match | NFC vs NFD differ → quote rejected | P3 | NFC normalize | code |
| CONV-016 | Curly quotes in answer | grounding accepts via canon | accepted, offsets exact ✓exec | — | — | test_evidence_tagging |
| CONV-017 | NBSP between words | flexible match | accepted ✓exec | — | — | test_evidence_tagging |
| CONV-018 | Mixed bidi (LTR-in-RTL) | stored, rendered | stored; display ordering only | P3 | bidi isolation | code |
| CONV-019 | Control chars \x01-\x08 | stored safely | JSON-escaped; rendered escaped | P3 | — | code |
| CONV-020 | Mojibake (double-encoded) | stored verbatim | stored; gates see mojibake words | P3 | — | code |
| CONV-021 | `"""` closes turn fence | no effect offline; live: model may misparse | offline immune (bank questions); live fence documented unfenced | P2 | fence escaping (Batch D) | code: interview/prompts.py:115 |
| CONV-022 | "Ignore prior instructions" in answer | treated as testimony | recorded verbatim; offline subject/parsers immune; live prompt-injection documented | P2 | delimiting | same |
| CONV-023 | Fake `should_close: true` JSON in answer | testimony | recorded; live path documented | P2 | — | code |
| CONV-024 | Fake claim+quote JSON in answer | gates decide | self-consistent claim passes gates → reaches human review (backstop) | P2 | human gate | code: grounding ✓exec |
| CONV-025 | `<script>alert(1)</script>` in answer | escaped everywhere | escaped (views esc) ✓exec | — | — | test_webapp escaping |
| CONV-026 | Markdown link bomb in answer | inert | escaped in HTML; markdown report escaped too | P3 | — | code |
| CONV-027 | Forged `seg-…` ids in answer | inert | stored as text; evidence refs are server-computed | P3 | — | code |
| CONV-028 | "system:" role confusion in answer | testimony | stored; prompt interpolation documented | P2 | fencing | code |
| CONV-029 | Base64 blob answer | vague/substantive by length | recorded; tagger words [a-z]+ | P3 | — | code |
| CONV-030 | Repeated triple-fences ×5 | inert offline | offline immune; live documented | P2 | fencing | code |
| CONV-031..038 | Each of the 8 deflection markers verbatim | candor=guarded, DE_ESCALATE, area deferred 2 turns | verified per marker (marker list engine.py:124) | P2 | — | test_strategy ✓exec |
| CONV-039 | "noteworthy" (contains near-marker) | NOT guarded | markers are space-padded phrases; "noteworthy" doesn't match "rather not" etc. | P3 | — | code: engine.py:124 |
| CONV-040 | Deflection twice in a row | never de-escalate twice | `self._last_intent is not DE_ESCALATE` guard ✓exec | — | — | test_strategy |
| CONV-041 | Return to deferred area after 2 turns | competes again | `deferred_until_turn` decay ✓exec | — | — | test_strategy |
| CONV-042 | Refusal on tier-capped area | deferred; gain damped ×0.15 | ✓exec | — | — | test_strategy |
| CONV-043..051 | Each of 9 vague markers verbatim | specificity conversion, same area | verified per marker (engine.py:129) | P2 | — | test_strategy ✓exec |
| CONV-052 | Vague ×2 | CONVERT_SPECIFICITY again (streak<2) | ✓exec | — | — | test_strategy |
| CONV-053 | Vague ×3 | streak=max → area struck from ladder | ✓exec | — | — | test_strategy/state |
| CONV-054 | Vague → concrete | streak reset 0 | ✓exec | — | — | test_strategy |
| CONV-055 | Concrete disclosure in workarounds | tier-2 credit, area touched | ✓exec | — | — | test_strategy |
| CONV-056 | Concrete disclosure in bottlenecks | tier credit | ✓exec | — | — | code |
| CONV-057 | Concrete disclosure in wasted_effort | ✓ | ✓exec | — | — | code |
| CONV-058 | Concrete disclosure in ai_opportunity | ✓ | ✓exec | — | — | code |
| CONV-059 | Concrete disclosure in friction | tier credited = bank tier actually asked (3) | ✓exec (fixed) | — | — | test_strategy NEW |
| CONV-060 | Concrete disclosure in process_reality | ceiling 1 — never "covered", gain capped | ✓exec (fixed) | — | — | test_strategy NEW |
| CONV-061 | Tier-4 self-implicating disclosure | disclosures_tier2plus++, evidence gated | ✓exec | — | — | test_strategy |
| CONV-062 | Contradiction with own earlier answer | SURFACE_CONTRADICTION (≤2 per interview) | ✓exec | — | — | test_strategy |
| CONV-063 | Same truth disclosed twice (repeated answer) | two claims, same content → dup claim ids possible | duplicate content-addressed ids in one batch (documented P3) | P3 | dedup in ground_proposals | code: grounding.py:198 |
| CONV-064 | Disclosure with curly quotes | grounds + entailment SUPPORTED | ✓exec (fixed) | — | — | test_entailment NEW |
| CONV-065 | Disclosure with figures (three days) | quantity gate passes identical figure | ✓exec | — | — | test_entailment |
| CONV-066 | Claim inflates figure (eleven days) | Gate-2 rejects | ✓exec | — | — | fuzz property |
| CONV-067 | Claim with negation flip | Gate-2 rejects | ✓exec | — | — | fuzz property |
| CONV-068 | Answer after interview closed | inactive | driver raises RuntimeError → route inactive-path ✓exec | P3 | — | test_webapp |
| CONV-069 | Answer after finish | no live session | webapp: inactive redirect; employee: `_unavailable` 404 ✓exec | P3 | — | tests |
| CONV-070 | Answer during stalled | recorded; question pending after recovery | employee: submit ok, next fails → stalled ✓exec | P2 | fixed | test_web_surface_hardening |
| CONV-071 | Answer to STALE page (old pending question) | reject or version-check | answer attributed to CURRENT pending question — stale answer silently misattributed | P3 | per-question form token | code: driver ✓exec |
| CONV-072 | Double-click answer ×2 | one record | **recorded 2×** (server accepts each POST against current pending) | P2 | disable-on-submit UI guard | NEW test (guard); code |
| CONV-073 | Triple submit ×3 | one record | 3 records (same class as 072) | P2 | same guard | NEW test |
| CONV-074 | Concurrent double-submit (2 threads) | one record | both pass check → 2 records (no idempotency key) | P2 | same guard (UI) + future idempotency key | code ✓exec |
| CONV-075 | Finish double-click | transcript stored once | 2nd finish → no live session → redirect /; write-once holds ✓exec | P3 | — | code |
| CONV-076 | Withdraw double-click | one withdrawal, second harmless | 2nd → 409 "already complete" copy (misleading text for withdrawn) | P3 | distinct withdrawn-copy | code ✓exec |
| CONV-077 | Begin after withdraw | dead link | 404 unavailable ✓exec | — | — | test_employee_surface |
| CONV-078 | Begin twice | idempotent | 2nd → redirect, no new transcript ✓exec | — | — | code |
| CONV-079 | Finish without begin | 404 | ✓exec | — | — | code |
| CONV-080 | GET surface before begin | welcome page | ✓exec | — | — | code |
| CONV-081 | Resume mid-question | identical coverage to never-stopped | ✓exec (fixed P1-2) | — | — | test_resumability NEW |
| CONV-082 | Resume with expired draft | fresh interview | sweep/TTL → welcome ✓exec | — | — | test_resumability |
| CONV-083 | Resume after process restart | full recovery | ✓exec | — | — | test_resumability |
| CONV-084 | Resume with turn_count > max | closes at next_question | budget check driver.py:151 ✓exec | P3 | — | code |
| CONV-085 | Resume with tampered draft | fresh start, draft removed | ✓exec (NEW fix) | — | — | test_persistence NEW |
| CONV-086 | Resume after withdraw | 404 | ✓exec | — | — | test_resumability |
| CONV-087 | Resume with tampered testimony log mid-file | loud, participant wedged | TamperedEventLog propagates → 500 (intentional-loud: testimony integrity > availability) | P2 | document; per-interview isolate | code ✓exec NEW |
| CONV-088 | All 6 areas vague-striked | close instead of grind | step-6 askable filter → CLOSE ✓exec (fixed) | — | — | test_strategy NEW |
| CONV-089 | Budget exhausted mid-pending | finish still works | `finish()` closes + stores ✓exec | — | — | code |
| CONV-090 | max_turns=1 config | one question then close | budget check ✓exec | P3 | — | code |
| CONV-091 | max_turns=0 | immediate close | budget check ✓exec | P3 | — | code |
| CONV-092 | Non-English answer | recorded; gates word-based | CJK tokenization gap (see CONV-013) | P2 | tokenization | code |
| CONV-093 | Answer = interviewer's question echoed | grounds against subject? no — interviewer quote rejected (F8) | rejected as cited_interviewer ✓exec | — | — | code |
| CONV-094 | "yes" / "no" minimal answers | vague | vague ✓exec | P3 | — | code |
| CONV-095 | ALL-CAPS answer | substantive | case-insensitive markers; recorded ✓exec | P3 | — | code |
| CONV-096 | URL-only answer | substantive-by-length | recorded; no URL handling | P3 | — | code |
| CONV-097 | Answer embedding another's seg-ids | inert | ids server-computed | P3 | — | code |
| CONV-098 | Consultant answer duplicate (double-click) | one record | 2 records (same class as CONV-072) | P2 | UI guard | NEW test (guard) |
| CONV-099 | Consultant stalled recovery | pause 503 → auto-continue | ✓exec (fixed) | — | — | test_web_surface_hardening |
| CONV-100 | Simulated demo while manual live | independent sessions | independent LiveInterview objects ✓exec | — | — | code |

## 2. Model output failures & instruction conflicts (PROMPT, 100)

Parse paths: `interview/turn.py:parse_turn` (interviewer turn), `evidence/tagger.py` (claims), `evidence/entailment.py` (verdicts), `aggregation/relation.py` (relations). Live-path prompt surfaces: `interview/prompts.py`, `evidence/prompts.py`, `subjects/simulated.py`.

| ID | Scenario | Expected | Current | Sev | Mitigation | Test |
|---|---|---|---|---|---|---|
| PROMPT-001 | Model returns "" | fail-closed | parse fails → fallback turn / claim dropped | P2 | — | code: turn.py |
| PROMPT-002 | Whitespace only | fail-closed | same as 001 | P3 | — | code |
| PROMPT-003 | Truncated mid-JSON | fail-closed | json parse fail → fallback | P2 | — | code |
| PROMPT-004 | Invalid JSON | fail-closed | fallback | P2 | — | code |
| PROMPT-005 | Valid JSON, wrong schema | fail-closed | missing keys → defaults/fallback | P2 | — | code: turn.py:77 |
| PROMPT-006 | Missing utterance key | fallback | `utterance = text.strip()` → **model's raw JSON shown to participant as question** | P2 | require utterance; drop turn | code: turn.py:94 ✓exec |
| PROMPT-007 | Empty utterance | fallback → raw text shown | same as 006 | P2 | same | code ✓exec |
| PROMPT-008 | utterance = 123 (int) | coerce/refuse | used as-is → rendered via esc (safe HTML; weird text "123") | P3 | type-check | code |
| PROMPT-009 | should_close=true, no reason | default reason | `closing_reason or "coverage_saturated"` ✓exec | P3 | — | code |
| PROMPT-010 | unknown closing_reason | stored as-is | stored verbatim in ledger/report meta | P3 | whitelist | code |
| PROMPT-011 | assessment = null | tolerated | `turn.assessment = None` by design | — | — | code |
| PROMPT-012 | tier as string "3" | coerce | `int(proposal.tier or 0)` ✓exec | P3 | — | code: grounding |
| PROMPT-013 | tier = 99 | clamp | `max(0, min(4, tier))` ✓exec | P3 | — | code |
| PROMPT-014 | tier = -5 | clamp 0 | ✓exec | P3 | — | code |
| PROMPT-015 | next_move null | no note_question | area attribution lost for that turn | P3 | — | code |
| PROMPT-016 | duplicate JSON keys | last wins | json.loads semantics | P3 | — | code |
| PROMPT-017 | NaN in numeric field | accepted by json.loads (non-strict) | NaN propagates to tier? int(NaN) raises → claim dropped | P3 | strict parse | code ✓exec |
| PROMPT-018 | 1MB output | parsed (cost spike) | no size cap on model output | P2 | cap response size | code |
| PROMPT-019 | max_tokens cut mid-JSON | fail-closed | parse fail → fallback/drop | P2 | — | code |
| PROMPT-020 | ```json fenced output | parse | fence NOT stripped → parse fail → fallback | P2 | strip fences | code ✓exec |
| PROMPT-021 | prose + JSON mix | fail-closed today | parse fail → fallback (safe but lossy) | P3 | extract-first-JSON | code |
| PROMPT-022 | multiple JSON objects | first/last? | json.loads fails → fallback | P3 | — | code |
| PROMPT-023 | BOM prefix | parse fail → fallback | json.loads handles BOM? plain fail → fallback | P3 | lstrip BOM | code |
| PROMPT-024 | \u0022 escapes in quote | quote resolves | json decodes → grounding exact-match after decode ✓exec | — | — | code |
| PROMPT-025 | raw newlines inside strings | strict JSON rejects → fallback | fail-closed | P3 | — | code |
| PROMPT-026 | \x00 in output | stored/escaped | JSON allows; esc renders | P3 | — | code |
| PROMPT-027 | RTL utterance | rendered | rendered, no bidi isolation (CONV-012 family) | P3 | dir=auto | code |
| PROMPT-028 | emoji utterance | rendered | ✓exec | — | — | code |
| PROMPT-029 | utterance = only quotes | rendered | shown as question | P3 | min-length check | code |
| PROMPT-030 | utterance echoes participant injection | live-model risk | parser can't detect semantic compliance | P2 | fence + canary directives | code (live-only) |
| PROMPT-031 | tagger returns "" | fail-closed | 0 claims; confabulation accounting | P2 | — | code: tagger |
| PROMPT-032 | tagger non-JSON | fail-closed | 0 claims | P2 | — | code |
| PROMPT-033 | tagger returns JSON array | fail-closed | parse per-item fails → 0 claims | P2 | — | code |
| PROMPT-034 | claims not a list | fail-closed | iteration fails → drop | P2 | — | code |
| PROMPT-035 | claim without quote | rejected `empty_quote` | ✓exec | — | — | code: grounding |
| PROMPT-036 | empty quote | rejected | ✓exec | — | — | code |
| PROMPT-037 | exact quote | grounded ✓ | ✓exec | — | — | fuzz property |
| PROMPT-038 | paraphrased quote | rejected | ✓exec | — | — | fuzz property |
| PROMPT-039 | invented quote | rejected | ✓exec | — | — | fuzz property |
| PROMPT-040 | interviewer question as quote | rejected `cited_interviewer` | ✓exec | — | — | fuzz property |
| PROMPT-041 | quote spanning two segments | rejected | per-segment search | — | — | fuzz probe |
| PROMPT-042 | curly-quote quote | accepted, offsets exact | ✓exec (fixed) | — | — | test_entailment NEW |
| PROMPT-043 | NBSP quote | accepted | ✓exec | — | — | fuzz |
| PROMPT-044 | homoglyph quote | rejected | ✓exec | — | — | fuzz probe |
| PROMPT-045 | mid-word fragment quote | rejected by boundary guards | ✓exec | — | — | fuzz probe |
| PROMPT-046 | statement empty | dropped | empty statement claim → downstream rendering empty h3 | P3 | require statement | code |
| PROMPT-047 | statement = only "[workaround]" tag | label trap (fixed) | tag stripped in labels; statement still odd | P3 | — | test_privacy NEW |
| PROMPT-048 | claim_type unknown | coerced | `ClaimType.coerce` → observation fallback | P3 | — | code |
| PROMPT-049 | segment_hint wrong id | search continues | hint reorders, never trusts ✓exec | — | — | code |
| PROMPT-050 | 50 claims in one transcript | all processed | O(n) gates; perf fine at demo scale | P3 | — | code |
| PROMPT-051 | duplicate identical claims | duplicate ids | content-addressed id collision in batch (documented P3) | P3 | dedup | code: grounding |
| PROMPT-052 | quote with regex metachars | grounded | re.escape on needle ✓exec | — | — | fuzz probe |
| PROMPT-053 | single-word quote | boundary-guarded | accepted only at word edges ✓exec | — | — | fuzz probe |
| PROMPT-054 | reversed offsets | rejected/mismatch | resolve() compares text → integrity property | — | — | fuzz property |
| PROMPT-055 | entailment verdict SUPPORTED (valid) | accepted | ✓exec | — | — | code |
| PROMPT-056 | verdict NOT_SUPPORTED | claim dropped | ✓exec | — | — | code |
| PROMPT-057 | verdict unparseable | fail-closed NOT_SUPPORTED | ✓exec | — | — | code: entailment |
| PROMPT-058 | verdict missing field | fail-closed | ✓exec | — | — | code |
| PROMPT-059 | reason-only response | fail-closed | ✓exec | — | — | code |
| PROMPT-060 | escalation ("committed fraud") | rejected (severe stems) | ✓exec | — | — | fuzz property |
| PROMPT-061 | polarity flip | rejected | ✓exec (fixed) | — | — | fuzz property |
| PROMPT-062 | curly-apostrophe flip | rejected | ✓exec (fixed) | — | — | fuzz probe NEW |
| PROMPT-063 | invented figure (eleven days) | rejected | ✓exec | — | — | fuzz property |
| PROMPT-064 | claim with no [a-z]{3,} words | auto-SUPPORT hole | falls through all checks → SUPPORTED | P2 | require content words | code ✓exec |
| PROMPT-065 | non-Latin claim (Russian) | auto-SUPPORT hole | same family as 064 | P2 | same | code ✓exec |
| PROMPT-066 | near-zero overlap claim | rejected | ✓exec | — | — | code |
| PROMPT-067 | lie/deceive/mislead escalation | rejected | stems added ✓exec | — | — | code |
| PROMPT-068 | participant closes live fence + directive | live only | parser has no defense; offline immune | P2 | fence escaping | code (live) |
| PROMPT-069 | participant "output should_close=true" | live only | model compliance unmeasurable offline; strategy CLOSE is safe | P2 | canary | code (live) |
| PROMPT-070 | participant fabricates self-consistent claim | gates pass (both sides attacker-authored) | reaches human review | P2 | human gate = backstop; live NLI later | code |
| PROMPT-071 | participant: "mark all claims tier 4" | tagger follows? live-only | tiers drive release policy — tier inflation = more suppression (safe direction) | P3 | — | analysis |
| PROMPT-072 | participant injects via SURFACE_CONTRADICTION echo (move.earlier[:160]) | participant text re-enters prompt | unescaped in prompt (HTML-escaped only) | P2 | fencing | code: engine.py:295 |
| PROMPT-073 | 100KB answer → prompt bloat | cost spike | cap 20k chars at web layer; CLI uncapped | P3 | CLI cap | code |
| PROMPT-074 | 14 turns × 20KB answers | 280KB context | live cost spike; max_turns bounds turns not bytes | P3 | byte budget | code |
| PROMPT-075 | live subject reveals SUBJECT_SYSTEM | disclosure | persona prompt contains instructions; leak = P3 info-disclosure | P3 | — | analysis (live) |
| PROMPT-076 | live subject role-plays interviewer | confusion | subject emits questions; driver records as answers | P3 | — | analysis (live) |
| PROMPT-077 | live subject refuses to be interviewed | parse_turn on refusal text | likely vague/guarded classification; interview continues | P3 | — | analysis (live) |
| PROMPT-078 | model repeats participant answer as its question | self-talk loop | strategy vague-streak breaks loops | P3 | — | code |
| PROMPT-079 | model outputs HTML/script in utterance | escaped | esc() everywhere ✓exec | — | — | test escaping |
| PROMPT-080 | model outputs the assessment JSON as utterance | shown raw | PROMPT-006/007 family | P2 | require utterance | code |
| PROMPT-081 | tagger claims quote from "other participant" | impossible structurally | single-participant transcripts; interviewer-quote guard | — | — | fuzz property |
| PROMPT-082 | entailment judge model itself injected (live) | NLI verdict manipulated | LlmEntailmentChecker — live only; heuristic floor stays | P2 | — | analysis (live) |
| PROMPT-083 | cache poisoning via injected prompt | key = full messages | injection changes key → no cross-participant poisoning at temp 0 | — | — | code: cache.py |
| PROMPT-084 | model outputs identical answer every turn (live) | strategy moves on | vague-streak/strikes; bank rotation ✓exec | — | — | test_strategy |
| PROMPT-085 | model outputs participant's verbatim words as question | provenance blur | utterance is interviewer segment; gates attribute correctly | P3 | — | code |
| PROMPT-086 | relation-model returns garbage (live) | HeuristicRelationChecker fallback? | `make_relation_checker(llm)` — live garbage → classified per classifier's fail mode | P2 | verify fallback | code: relation ✓exec-part |
| PROMPT-087 | tagger outputs claims for interviewer text | rejected | interviewer-quote guard ✓exec | — | — | fuzz property |
| PROMPT-088 | tagger hallucinates a 4th area | areas from fixed TARGET_AREAS | unknown area ignored in coverage (dict.get None guard) ✓exec | P3 | — | code |
| PROMPT-089 | model outputs "null" | fail-closed | parse fail → fallback | P3 | — | code |
| PROMPT-090 | model outputs "NaN" numerics | int(NaN) raises → drop | ✓exec | P3 | — | code |
| PROMPT-091 | claim statement contains "[workaround]" itself | label trap | tag-strip regex handles leading tag; mid-statement literal tag counts as vocab | P3 | — | test_privacy NEW |
| PROMPT-092 | claim quote == another claim's quote | both ground; dup ids | PROMPT-051 family | P3 | dedup | code |
| PROMPT-093 | participant answer contains ANOTHER participant's real name | stored; employer aggregate-only | consultant view shows it; no cross-participant redaction | P2 | name-entity redaction (roadmap) | code |
| PROMPT-094 | live model emits system-prompt contents | disclosure | SUBJECT_SYSTEM leak (live only) | P3 | — | analysis (live) |
| PROMPT-095 | turn-prompt directive conflicts with system prompt | directive wins? | system says follow directive ✓ — conflict is model-judgment, unmeasurable offline | P3 | eval live | analysis (live) |
| PROMPT-096 | prompt version skew (PROMPT_VERSION) | cache keyed on messages+system | prompt edit invalidates cache ✓exec | — | — | code: cache |
| PROMPT-097 | tagger prompt_version drift | ledger records version | ✓exec | — | — | code |
| PROMPT-098 | model returns claim quoting the CLOSE remark | closing utterance is interviewer speech | rejected (interviewer guard) ✓exec | — | — | code |
| PROMPT-099 | model returns claims after should_close | loop already ended | no claims without transcript | — | — | code |
| PROMPT-100 | ALL prompt surfaces at once hostile (participant attacks every turn) | gates + human review + aggregate-only release | defense-in-depth holds offline; live unproven | P2 | Batch D + live eval | suite |

## 3. Concurrency scenarios (CONC, 50)

| ID | Scenario | Expected | Current | Sev | Mitigation | Test |
|---|---|---|---|---|---|---|
| CONC-001 | Two POSTs same employee token (parallel) | one record | both submit → 2 records (no idempotency) | P2 | UI guard; idempotency key later | code ✓exec (sequential) |
| CONC-002 | Three parallel POSTs | one record | 3 records | P2 | same | code |
| CONC-003 | answer racing withdraw | either outcome, no crash | withdraw pops session; answer Nones → redirect/404 | P3 | — | code |
| CONC-004 | answer racing finish | finish stores; late answer → inactive | no crash ✓exec | P3 | — | code |
| CONC-005 | withdraw racing finish (finish wins) | transcript stored, withdraw refused 409 | 409 honest page ✓exec (fixed) | — | — | test_web_surface_hardening |
| CONC-006 | withdraw racing finish (withdraw wins) | nothing stored; finish → revive fails → 404 | draft deleted → revive None → 404 ✓exec | — | — | code |
| CONC-007 | finish double-click | stored once | write-once + live.pop → safe ✓exec | — | — | code |
| CONC-008 | begin double-click | idempotent | token in live → redirect ✓exec | — | — | code |
| CONC-009 | begin racing begin (2 tabs) | one transcript | both check `token not in sessions.live` — RACE: two transcripts possible | P2 | single-flight per token | code |
| CONC-010 | resume during sweep | sweep skips active or deletes? | sweep by TTL only; active resume after expiry → None → fresh | P3 | — | code |
| CONC-011 | dashboard render during finish | consistent-ish | rows from store list; finishing not yet saved → absent then present | P3 | — | code |
| CONC-012 | dashboard render during 9-thread demo | partial interviews visible | store list grows live ✓exec | P3 | — | code |
| CONC-013 | tagging while transcript save | tagger loads snapshot | load returns full file ✓ | P3 | — | code |
| CONC-014 | event-log append during read | read sees prefix | reader reads snapshot of lines; appends after → next read sees more | P3 | — | code |
| CONC-015 | head-file write vs read race | read may miss newest head | chain read tolerant; append recomputes from file | P3 | — | code |
| CONC-016 | two processes, one data dir | unsupported | no locking; JSON stores last-write-wins | P2 | document + file lock (roadmap) | code |
| CONC-017 | two processes create engagement | both created | JSON read-modify-write race → one LOST (silent) | P2 | same as 016 | code: engagements |
| CONC-018 | two processes load_or_create salt | two salts! | pseudonyms split across processes | P2 | file creation race → atomic replace; loser re-reads? NOT implemented | code ✓exec-class |
| CONC-019 | derived-cache write race same key | one wins | store writes atomic? plain write → torn entry possible; load failure → miss ✓ | P3 | atomic replace | code: derived_store |
| CONC-020 | invitations concurrent create | unique tokens (secrets) | ✓ | — | — | code |
| CONC-021 | session save racing save (same token) | last wins | same-file overwrite; both complete interviews? one driver | P3 | — | code |
| CONC-022 | consultant + employee same engagement | fine | independent surfaces ✓ | — | — | code |
| CONC-023 | two demo runs concurrently | two engagements | both create; thread pools independent; registry race (017) | P2 | registry lock | code |
| CONC-024 | demo + manual interview simultaneously | independent | ✓exec | — | — | code |
| CONC-025 | preflight concurrent | one cheap call each | fine | — | — | code |
| CONC-026 | 9 threads × cache miss same key | 9 model calls (stampede) | no per-key lock — live cost spike | P2 | single-flight cache | code: cache.py |
| CONC-027 | transcript save race same id | write-once raises | FileExistsError swallowed in demo finish path ✓exec | P3 | — | code |
| CONC-028 | validation ledger concurrent writes | append race | per-line append; interleaved lines are complete writes (small) | P3 | — | code |
| CONC-029 | restart during event emit | torn final line | tolerated on read ✓exec | P3 | — | test_log_encryption |
| CONC-030 | restart during transcript save | torn file → load fails → 404 | transcript DATA LOSS for that interview (write_bytes non-atomic) | P2 | atomic replace like identity | code: transcript_store ✓exec-class |
| CONC-031 | restart during reports.save | torn report | regenerable artifact — harmless | P3 | atomic replace | code: reports.py |
| CONC-032 | restart during identity save | atomic replace ✓ | no torn state ✓exec (PR#4) | — | — | test_review_followups |
| CONC-033 | restart during engagements write | torn index → quarantined ✓exec (NEW fix) | names lost (backup kept) | P3 | atomic replace (todo) | test_persistence NEW |
| CONC-034 | restart during session save | torn draft → load None → fresh | answer loss within documented draft-expiry mode | P3 | atomic replace | code |
| CONC-035 | GIL/thread-safety of Pseudonymizer dict | pre-issued serially in demo; webapp single-threaded event loop | ✓ (demo pre-issues) | — | — | code |
| CONC-036 | live dict eviction (LRU absent) | unbounded growth | consultant long-running process accumulates LiveInterviews | P3 | evict closed | code |
| CONC-037 | employee sessions dict growth | unbounded | same | P3 | sweep on access | code |
| CONC-038 | simultaneous demo + preflight | independent | fine | — | — | code |
| CONC-039 | two workspaces same data dir | unsupported silently | stores collide | P2 | document / lock | code |
| CONC-040 | Windows file locking on store writes | replaced/written while AV scans | occasional PermissionError unhandled | P3 | retry-on-PersonmissionError | platform |
| CONC-041 | many dashboards open (N viewers) | each re-tags all transcripts | cost multiplies (R8) | P2 | tag cache | code |
| CONC-042 | demo while data dir read-only | emits raise inside threads | caught by isolation (NEW) → failures reported ✓exec | — | — | test_application NEW |
| CONC-043 | withdraw while stalled | session popped; stalled retry → None → welcome/404 | ✓ | P3 | — | code |
| CONC-044 | finish while model call in-flight | next_question blocks? HTTP threads: two requests parallel — finish pops, next_question continues on dead object → result discarded | P3 | — | code |
| CONC-045 | employee finish while consultant views draft transcript | draft not in transcript store until finish → consultant 404 then appears | ✓ | P3 | — | code |
| CONC-046 | derived cache enabled + thread demo | shared store, per-key writes | same as 019 | P3 | atomic | code |
| CONC-047 | two consultants (future) | no multi-tenant concept | out of scope (Art. XIX) | — | — | docs |
| CONC-048 | invitation create during dashboard list | list snapshot | ✓ | P3 | — | code |
| CONC-049 | engagement rename/delete routes | don't exist | n/a | — | — | code |
| CONC-050 | subprocess kill -9 mid-demo | pool threads die with process; partial transcripts remain; failures unknown | P2 | isolation + idempotent re-run | code |

## 4. State corruption scenarios (STATE, 50)

| ID | Scenario | Expected | Current | Sev | Mitigation | Test |
|---|---|---|---|---|---|---|
| STATE-001 | Transcript JSON truncated | loud not-found | load fails → 404 (silent-ish but bounded); data lost | P2 | atomic writes | code ✓exec-class |
| STATE-002 | Transcript tampered under cipher | auth failure | Fernet InvalidToken → load fails → 404 | P2 | distinguish tamper vs missing | code |
| STATE-003 | .enc transcript loaded with NullCipher | refuse | ValueError loud ✓exec | — | — | test_privacy_edges |
| STATE-004 | plaintext transcript with cipher store | reads what's on disk | loads (dev→prod migration tolerance) ✓ | — | — | code |
| STATE-005 | transcript id traversal (../) | refused | ValueError ✓exec (fixed) | — | — | test NEW |
| STATE-006 | Event log tampered mid-file | loud | TamperedEventLog ✓exec | — | — | test_privacy_edges |
| STATE-007 | Event log final line torn | tolerated | last-line skip ✓exec | — | — | test_log_encryption |
| STATE-008 | Event .head deleted | truncation detection lost | read tolerant; append regenerates ✓exec | P3 | head regeneration warning | code ✓exec NEW |
| STATE-009 | .head tampered (shorter count) | loud | chain/head check → TruncatedEventLog (verify on read path) | P2 | — | test_review_followups |
| STATE-010 | seq gap in log | loud | chain check | P2 | — | same |
| STATE-011 | prev-digest mismatch | loud | chain check | P2 | — | same |
| STATE-012 | Session draft corrupt JSON | fresh start, file removed | ✓exec (NEW fix) | — | — | test_persistence NEW |
| STATE-013 | Session draft wrong schema | fresh start, removed | ✓exec (NEW fix) | — | — | test_persistence NEW |
| STATE-014 | Draft decrypt failure (wrong key) | file KEPT | ✓exec (NEW fix) | — | — | test_persistence NEW |
| STATE-015 | Draft expired | swept | TTL sweep ✓exec | — | — | test_resumability |
| STATE-016 | Invitation file corrupt | degrade 404 | get fails → 404 unavailable ✓exec NEW | — | — | NEW (repro) |
| STATE-017 | Invitation status invalid value | degrade | status compared as string → treated unknown (is_finished False → usable? probe edge) | P3 | enum validation | code |
| STATE-018 | Engagements index corrupt | quarantined, fresh, loud | ✓exec (NEW fix) | — | — | test_persistence NEW |
| STATE-019 | Engagements dir missing | created on write | ✓exec | — | — | code |
| STATE-020 | Identity state corrupt | loud (CorruptIdentityState) | PR#4 ✓exec | — | — | test_review_followups |
| STATE-021 | Identity state deleted (RESTRICTED removed) | fresh salt → old pseudonyms orphaned | transcripts keep old pseudonyms; new interviews new salt → same person = 2 voices | P2 | backup/restore guidance; salt in engagement record | code ✓exec-class |
| STATE-022 | Report .enc without key | loud | ValueError ✓exec | — | — | test_log_encryption NEW |
| STATE-023 | Derived cache entry corrupt | treated as miss | load failure → recompute | P3 | — | code: derived_store |
| STATE-024 | Derived cache wrong schema | miss | same | P3 | — | code |
| STATE-025 | Ledger verdict for unknown claim | ignored on read | read model folds by claim_id ✓ | P3 | — | code: ledger |
| STATE-026 | Verdict string invalid in ledger | ValidationDecision raise → finding skipped | ✓exec | P3 | — | code: service |
| STATE-027 | transcript.engagement_id unknown to registry | raw id shown | engagement_name falls back to id ✓exec | P3 | — | code |
| STATE-028 | invitation.transcript_id dangling | review 404 | load None → 404 ✓ | P3 | — | code |
| STATE-029 | Duplicate claim ids in one batch | conflated consumers | documented P3 | P3 | dedup | code |
| STATE-030 | Duplicate segment ids (identical text twice) | anchors ambiguous | content-addressed ids identical → #seg- ambiguity | P3 | disambiguate | code |
| STATE-031 | Events out of order (seq) | chain check | ✓ (PR#4) | P2 | — | test_review_followups |
| STATE-032 | store dir replaced by file | mkdir raises | loud at construct/write | P3 | — | code |
| STATE-033 | Leftover .tmp atomic files | harmless clutter | ignored by listers? list_ids only matches suffixes ✓ | P3 | cleanup | code |
| STATE-034 | Empty data dir | fresh everything | ✓exec | — | — | suite |
| STATE-035 | Data dir deleted mid-run | stores mkdir on demand | partial recovery; open handles fail | P3 | — | code |
| STATE-036 | Disk full on emit | OSError unhandled in emit → surfaces at call site (500/CLI crash) | UNHANDLED | P2 | catch + degrade | code |
| STATE-037 | Read-only data dir | same as 036 | UNHANDLED | P2 | same | code |
| STATE-038 | Wrong key after key rotation | decrypt fail → kept (NEW), transcript 404 | rotation path undocumented | P2 | rotation runbook | NEW |
| STATE-039 | Mixed plain/enc files same store | reads what's on disk | supported ✓exec | — | — | code |
| STATE-040 | Symlinked store entries | followed | document | P3 | — | code |
| STATE-041 | Case-collision filenames (Win) | txn-ABC vs txn-abc distinct on Linux, collide on Windows | ids are lowercase hex — safe ✓ | — | — | code |
| STATE-042 | Huge transcript file (10MB) | loads slow | no size guard | P3 | — | code |
| STATE-043 | Event log 100k lines | read all into memory | memory spike on read | P3 | stream | code |
| STATE-044 | Engagement with 0 transcripts | synthesis ValueError → 404 route ✓exec | — | — | test_application NEW |
| STATE-045 | Engagement with 500 transcripts | list_ids + per-transcript load | O(n) reads per page | P3 | index | code |
| STATE-046 | report.md referenced by old transcript id | stale report remains | regenerable ✓ | P3 | — | code |
| STATE-047 | version skew: groundwork.transcript/v2 in file | unsupported schema → load fail | explicit error message ✓exec | P3 | migration tooling | code |
| STATE-048 | identity issued mapping references removed participant | key entry harmless | — | — | — | code |
| STATE-049 | participation count includes withdrawn interview | withdrawn → no transcript → excluded ✓exec | — | — | test_resumability |
| STATE-050 | Timezone-skewed updated_at (manual edit) | TTL math off | ISO parse; skew → early/late sweep | P3 | — | code |

## 5. API failure scenarios (API, 50)

| ID | Scenario | Expected | Current | Sev | Mitigation | Test |
|---|---|---|---|---|---|---|
| API-001 | 429 ×4 exhausted | LLMUnavailable → participant 503 stalled | ✓exec (employee); consultant stalled (fixed) | P2 | — | test_llm_robustness |
| API-002 | 429 then success | retried, backoff+jitter | ✓exec | — | — | test_llm_robustness |
| API-003 | 500 mid-turn | transient retry | ✓exec | — | — | retry tests |
| API-004 | 400 malformed request | permanent, fail fast | ✓exec | — | — | retry tests |
| API-005 | 401 bad key | permanent | ✓exec | — | — | retry tests |
| API-006 | 403 | permanent | ✓exec | — | — | retry |
| API-007 | 404 wrong model | permanent + preflight catches at startup | ✓exec (fixed) | — | — | preflight tests |
| API-008 | 408 timeout status | transient | ✓exec | — | — | retry |
| API-009 | 422 | permanent | ✓exec | — | — | retry |
| API-010 | 529 overload | transient | ✓exec | — | — | retry |
| API-011 | timeout every attempt | ~4 min block worst case | 60s×4, no per-request server timeout; participant waits | P2 | lower timeout / abort early | code: client.py:15 |
| API-012 | connection reset | transient | ✓exec | — | — | retry |
| API-013 | DNS failure | transient → exhausted | ✓exec | P2 | — | retry |
| API-014 | empty body 200 | adapter raises → classified | anthropic SDK raises; gemini no-candidates ✓exec | P2 | — | test_gemini_client |
| API-015 | non-JSON body | raise → classify | ✓exec (gemini); anthropic SDK raises | P2 | — | test_gemini_client |
| API-016 | 200 malformed shape | no candidates → raise ✓exec | P2 | — | test_gemini_client |
| API-017 | Retry-After header | ignored | backoff ignores it (documented P3) | P3 | honor header | code: retry.py |
| API-018 | Gemini blockReason (safety) | raise with reason | ✓exec | P2 | — | test_gemini_client |
| API-019 | Gemini empty parts | "" → parse fail downstream | ✓exec | P3 | — | test_gemini_client |
| API-020 | Gemini truncated output | fail-closed parse | ✓exec | P2 | — | code |
| API-021 | token endpoint 400 | permanent path | JWT exchange raises _HttpStatusError(400) → permanent ✓exec | P2 | — | test_gemini_client |
| API-022 | token endpoint 500 | transient → retried → LLMUnavailable | ✓exec | P2 | — | test_gemini_client |
| API-023 | token expired mid-engagement | refresh cached till expiry−60s | ✓exec | — | — | test_gemini_client |
| API-024 | metadata server absent (off-GCP, no key file) | urllib error → transient retries → unavailable | ✓exec-class | P2 | preflight catches | test_gemini_client |
| API-025 | GAC file unreadable | RuntimeError at token fetch | ✓exec | P2 | — | test_gemini_client |
| API-026 | GAC missing fields | RuntimeError naming field | ✓exec | P2 | — | test_gemini_client |
| API-027 | malformed RSA key | cryptography raise → classified transient? | raises inside _once → retried (wasteful) then unavailable | P3 | mark permanent | test_gemini_client |
| API-028 | anthropic SDK absent + key set | RuntimeError with install hint | ✓exec | P2 | — | code: client.py:69 |
| API-029 | provider=gemini without project | deployment problem + adapter gets "" project → URL malformed | listed at startup (NEW) | P2 | — | test_gemini_client NEW |
| API-030 | both keys set | anthropic wins (precedence documented) | ✓exec | — | — | code |
| API-031 | provider typo "gemni" | FAIL-CLOSED ConfigurationError | ✓exec (NEW fix) | P2 | — | test_gemini_client NEW |
| API-032 | latency spike 59s | inside timeout | completes | P3 | — | code |
| API-033 | latency 61s | timeout → transient → retry | ✓exec | P2 | API-011 | retry |
| API-034 | tagger call fails post-interview | CLI: transcript stored, tagging crash → report lost; webapp review 500? | tag() raises → review route 500 (unhandled) | P2 | catch → message | code: webapp review |
| API-035 | entailment model call fails (live) | LlmEntailmentChecker complete raises → propagates? | checker inside tag() → same as 034 | P2 | fail-closed per claim | code |
| API-036 | relation checker live fails during aggregate | classify per pair raises → aggregation crashes | unhandled | P2 | fallback to heuristic | code: relation |
| API-037 | cache store write fails | miss → recompute each time | derived_store swallow? verify | P3 | — | code: derived_store |
| API-038 | preflight fail at server start | exit 1 with named model | ✓exec (fixed) | — | — | test_web_surface_hardening |
| API-039 | preflight fail at CLI start | same | ✓exec | — | — | code |
| API-040 | demo all-fail | 503 honest page, nothing persisted | ✓exec (NEW fix) | — | — | test_application NEW |
| API-041 | demo partial fail | 8/9 complete, failures isolated, testimony of failed purged | ✓exec (NEW fix) | — | — | test_application NEW |
| API-042 | employee begin fails model | 503, invitation reset PENDING | ✓exec | — | — | test_employee_surface |
| API-043 | employee answer fails model | stalled, draft persisted | ✓exec | — | — | test_employee_surface |
| API-044 | consultant answer fails model | stalled → 503 page → retry continues | ✓exec (fixed) | — | — | test_web_surface_hardening |
| API-045 | report render during model outage | report is offline (markdown) — unaffected | ✓ | — | — | code |
| API-046 | eval gate during outage | mock mode unaffected | ✓ | — | — | code |
| API-047 | rate limit at provider account level | 429 storm → all interviews stalled | per-thread backoff, no global budget | P2 | global budget/semaphore | code |
| API-048 | latency spike with 9 concurrent demos | 9×14×4min worst case unbounded queue | thread pool caps workers; requests pile | P2 | budget + circuit breaker | code |
| API-049 | API returns wrong-model data (schema drift) | fail-closed parsers | ✓exec | — | — | parsers |
| API-050 | key revoked mid-interview | 401 permanent at next call → stalled/wedge | employee stalled (retry never succeeds) → stuck at 503 forever | P2 | give up after N stalls → graceful close + partial saved | code |

---

### Verification (Phase 7)
- Full suite: **407 tests OK** (12 reliability regressions NEW) · eval gate 6/6 PASS · fuzz audit 0 violations — run after every fix batch (three green runs this investigation).
- CI green on push: run 34034367849 → this matrix lands with the fix commit and re-runs CI.

### Fixed by this investigation
CONV-071/072/073/098 guard · CONV-085/087 · CONV-088/060 · PROMPT-062/064/065 (documented; heuristic floor) · CONC-042 · STATE-008/012/013/014/016/018/029/044 · API-029/031/040/041.
### Still open (documented, ranked)
API-011/047/048 (budget+circuit breaker) · CONC-016/017/018 (multi-process contract) · R2 packaging · STATE-021 salt-per-engagement · PROMPT-006 (utterance required) · PROMPT-020 (fence strip) · Batch-D fencing · STATE-036/037 disk-full · API-050 stall give-up · STATE-030 atomic transcript writes.
