# Code Walkthrough (for beginners)

*A plain-language guide to what every part of this repository does, how the pieces
fit together, and how to read the code — written for someone who uses AI to code
but hasn't learned programming formally.*

---

## The vocabulary (define the words first)

Think of building software like running a kitchen.

| Term | What it is | Example here |
|---|---|---|
| **Programming language** | The language instructions are written in | **Python** (`.py`, the running program) and **TypeScript** (`.ts`, blueprints only) |
| **Library / package** | Pre-written code you borrow | `anthropic` (talks to the Claude model) — almost everything else uses Python's built-ins |
| **Data type** | *What kind* of value something is | `str` text, `int` whole number, `float` decimal, `bool` yes/no, `list` a collection |
| **Variable** | A labeled box holding a value | `candor = "open"` |
| **Function** | A reusable recipe: inputs → steps → result | written with `def` |
| **Class** | A blueprint for a "thing" that bundles data + recipes | `Transcript`, `Claim` |
| **Object** | One actual thing built from a class | a specific transcript |

**Ingredients = data types. Recipes = functions. Appliances = classes. Store-bought
parts = libraries. The cookbook's language = the programming language.**

---

## The two halves of this repo

1. **`docs/` — the thinking.** ~20 plain-English strategy essays (this file included).
   No code. Read them like articles.
2. **`apps/` and `packages/` — the doing.** The software, which itself splits into:
   - **`apps/ai-engine/ai_engine/`** — the **real, runnable Python program**. *This is
     the machine.* Focus here.
   - **`packages/contracts/`, `apps/core-api/`** — **TypeScript blueprints** (`.ts`):
     precise shapes/rules with no engine behind them yet. Architectural drawings for
     a building not yet built. Beginners can skip these.
   - **`apps/ai-engine/src/**/.gitkeep`** — empty placeholder folders. A `.gitkeep` is
     a dummy file that just makes an empty folder exist. Ignore them.

---

## What the program does, end to end

> Turn a spoken interview into a small set of **true, source-proven, human-approved**
> findings about how an organization really works — and be able to **prove** and
> **grade** that they aren't made up.

The pieces form a relay race. Each stage distrusts the one before it and forces
proof — that chain of distrust *is* the product, because the whole business risk is
an AI confidently inventing things.

```
subjects/  →  interview/  →  transcript/  →  evidence/  →  validation/  →  report/
(who talks)   (what to ask)  (permanent      (claims +     (human         (deliverable)
                             record)         lie-detector) approves)
                                    │
                                    └───────────→  eval/  (grades the run vs known truth)
        persistence/  quietly saves each stage to its own file
```

---

## Folder-by-folder (in data-flow order)

A folder with an `__init__.py` is a Python **package** — a labeled drawer. The
`__init__.py` is the drawer's index; it usually just lists what's inside.

### `llm/` — the phone line to the AI
- **`client.py`** — the one place that knows how to *call the Claude model*. Everything
  else talks to "an AI" through here, so swapping providers is a one-file change. If
  there's no API key, it returns nothing and the program falls back to **mock mode**.

### `subjects/` — who is interviewed
- **`human.py`** — a real person typing at the keyboard.
- **`simulated.py`** — a **fake employee** the computer plays, who secretly *knows* a
  fixed list of true things (each tagged Tier 1 harmless → Tier 4 self-incriminating)
  and has a **candor** dial (`guarded`/`neutral`/`open`). Because we know its truths in
  advance, we can *test* whether the interviewer got them. This is the test rig.
- **`base.py`** — the shared shape both follow ("an interviewee can `answer`").

### `interview/` — the interviewer's brain (the core IP)
- **`prompts.py`** — the English instructions to the AI on *how* to interview.
- **`state.py`** — running memory of which topics are covered and how deep.
- **`turn.py`** — the shape of one exchange + a *defensive parser* that recovers if the
  AI's reply is malformed instead of crashing.
- **`engine.py`** — the "pick the next question" logic (adaptive with a real AI; a fixed
  script without one).
- **`session.py`** — the loop: ask → record → answer → record → repeat until done.

### `transcript/` — the permanent record
- **`model.py`** — a `Transcript` made of `Segment`s. Once written, a segment can **never
  change** (immutable), and each has an address. This is what lets any later claim point
  at an exact sentence. *Annotated line-by-line below.*

### `evidence/` — talk becomes proven claims
- **`tagger.py`** — reads the transcript, proposes claims each with a supporting quote.
- **`grounding.py`** — the **lie-detector**: checks each quote *actually exists* in the
  immutable transcript. Invented or paraphrased quotes get **rejected**. It verifies; it
  doesn't trust. The most important safety idea in the codebase.
- **`model.py`** — a `Claim` is *forbidden to exist without evidence*, and is always
  `proposed` (never "true") until a human approves it.
- **`prompts.py`** — tells the AI to quote word-for-word or drop the claim.

### `validation/` — the human approves
- **`model.py` / `gate.py`** — a consultant **accepts / rejects / edits** each claim. Rules
  enforce that you can't approve without reviewing the evidence, and reject/edit need a
  reason. "AI proposes, human decides," made concrete. Also produces the *learning signal*.

### `report/` — the deliverable
- **`generator.py`** — writes a clean report from **only the approved** findings, each
  showing its exact quote. What a consultant would hand a client.

### `persistence/` — saving data
- **`event_log.py`** — writes to disk, keeping **separate files** for what was said, what
  the AI inferred, and what the human decided — never mixing them.

### `eval/` — the report card (the moat)
Grades the whole machine against the fake employee's *known* truths. Uses **pass/fail
gates**, not fuzzy averages. Runs each case several times and reports the spread (a real
AI is random). Files: `matching.py` (does a finding match a known truth?), `metrics.py`
(the math), `gates.py` (thresholds), `dataset.py` (test cases), `runner.py` (runs them),
`report.py` (scorecard + JSON).

### Glue
- **`cli.py`** — the front door; runs when you type `python3 -m ai_engine.cli`.
- **`config.py`** — settings (which model, where to save, is there a key?).
- **`pyproject.toml`** — the program's ID card (`.toml` = a settings format, not code).
- **`tests/`** — small programs that check the real code works (the "47 tests pass").

---

## Reading the code: patterns you'll see everywhere

| You'll see | It means |
|---|---|
| `from ..transcript.model import Transcript` | Borrow the `Transcript` blueprint from another file. Dots = "up a folder." |
| `def answer(self, question: str) -> str:` | A recipe named `answer` taking text, returning text. `: str` / `-> str` are **type hints** — labels, not behavior. |
| `return x` | Hand `x` back as the result. |
| `class Thing:` / `@dataclass` | Define a blueprint. `@dataclass` auto-writes boilerplate for data-holders. |
| `@dataclass(frozen=True)` | Same, but **it can't be changed after creation** — how "immutable" is enforced. |
| `self` | "This particular object" — i.e. "me." |
| `if ...: / else:` | A fork in the road. `raise` = stop on purpose with an error. |
| `for x in things:` | Do something to each item in a list. |
| `str \| None` | "Text, *or* nothing" — this value might be empty. |
| `class Verdict(str, Enum):` | A fixed menu of allowed choices (prevents typos). |
| `f"Turns: {n}"` | Text with a value slotted in; if `n` is 9 → `"Turns: 9"`. |
| `llm=None` everywhere | "If given a real AI use it; if not, fall back to built-in fake behavior." Why it runs offline. |

---

## One file, line by line: `transcript/model.py`

This is the foundation — it enforces that the record can't be tampered with. Here are
the key parts with every line explained.

**A segment (one thing said):**
```python
@dataclass(frozen=True)          # a data-holder blueprint; frozen = unchangeable
class TranscriptSegment:
    id: str                      # a unique address, e.g. "seg-089b50f8cfa3" (text)
    transcript_id: str           # which transcript it belongs to (text)
    sequence: int                # its position: 0, 1, 2, ... (whole number)
    speaker: Speaker             # who said it (interviewer or subject)
    text: str                    # the actual words (text)
    uttered_at: datetime         # when it was said (a timestamp)
```
Because the class is `frozen=True`, once a segment exists, none of these can ever be
altered. That permanence is what makes evidence trustworthy.

**Reading an exact slice of a segment (and refusing a bad request):**
```python
    def span_text(self, start: int, end: int) -> str:      # give me characters start→end
        if start < 0 or end > len(self.text) or start > end:  # if the range is nonsense…
            raise ValueError(...)                              # …stop and complain
        return self.text[start:end]                            # otherwise hand back that slice
```
`self.text[start:end]` is "give me the characters from position `start` up to `end`."
The `if` guards against asking for characters that don't exist.

**A pointer that proves where a claim came from:**
```python
@dataclass(frozen=True)
class EvidenceRef:               # "the proof is at segment X, characters start→end"
    segment_id: str
    start: int
    end: int

    def resolve(self, transcript) -> str:                     # go fetch the real words
        return transcript.segment(self.segment_id).span_text(self.start, self.end)
```
`resolve` is the payoff: given the whole transcript, it looks up the segment and returns
the *exact real text* the claim rests on. If that text isn't there, it fails loudly —
which is exactly how fabrication gets caught.

**The transcript, and why you can't tamper with it:**
```python
    def append(self, speaker, text, uttered_at=None):
        if self.finalized:                                    # once the interview is closed…
            raise TranscriptFinalizedError(...)               # …you cannot add or change anything
        segment = TranscriptSegment(
            id=_new_id("seg"),                                # make a fresh unique address
            sequence=len(self._segments),                     # next position in line
            text=text.strip(),                                # store the words (trimmed)
            ...
        )
        self._segments.append(segment)                        # add it to the record
        return segment
```
The very first check — "if finalized, refuse" — is the whole immutability guarantee in
two lines. After an interview ends, the record is frozen forever.

That single idea (a permanent, addressable record) is what every later stage — evidence,
validation, report, eval — depends on.

---

## How it all integrates

**Product generates a transcript → the tagger proposes claims → the lie-detector proves
or rejects each against the frozen transcript → a human approves → a report is produced →
the eval harness grades the whole thing against known truth.** Every arrow is a checkpoint
that assumes the previous step might be wrong and demands proof. Remove any one checkpoint
and the system could confidently lie — which is the one thing it must never do.

---

## A note on "vibe coding"

Building software by conversing with an AI in plain language — steering by intent and
feedback rather than typing every line. Doing it *well* means:

1. **Design before code.** (We wrote ~20 strategy docs before one line of Python.)
2. **Build thin, runnable slices.** Keep it working; grow it.
3. **Run it and test it.** Verify, don't trust. The eval scorecard and the 47 tests are
   the point.
4. **Keep guardrails.** The lie-detector and the constitution exist because AI-written
   code needs rules it can't quietly break.
5. **Read the shape, spot-check details.** You don't type every line, but you understand
   the structure — which is what reading this document is.

The healthy loop: **describe the goal → let the AI build a small piece → run it → read what
it did → correct → repeat.** The danger is accepting big piles of code you've never run and
can't explain. Reverse-engineering the thing you built — as you're doing now — is the fix.
