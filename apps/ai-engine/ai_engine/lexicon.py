"""Shared lexical primitives for the two semantic gates.

Negation and quantity are the two ways a claim can invert or inflate its source
while still looking like it. Both the entailment gate (``evidence/entailment.py``)
and the relation classifier (``aggregation/relation.py``) need to reason about
them, and both had their own private notion of "content words" that silently
ignored both.

They live here rather than in either module because a cue list that exists twice
drifts: ``relation.py`` knew ``can't`` but not ``cannot``, so
"Finance cannot close the books" and "Finance closes the books, always" were
classified as *agreement* — and that verdict then fed the confidence scorer as an
independent corroborating voice, raising confidence on a flat contradiction.
One concept, one name, one home (Constitution Art. XV).

Nothing here is natural-language understanding. These are deliberately narrow,
deterministic checks that catch the two mechanical inversions; anything subtler
is the job of a real entailment model.
"""
from __future__ import annotations

import re

# --- canonicalization ------------------------------------------------------

# Unicode characters a model commonly substitutes when it echoes a quote:
# curly quotes for straight, en/em dashes for hyphen, exotic spaces. Each maps to
# exactly ONE ascii character so the mapping is length-preserving — which means an
# offset in the canonicalized text is the SAME offset in the original text, so an
# EvidenceRef built from canonicalized grounding still points at real immutable
# source. A rare char that lowercases to more than one char (e.g. "İ") is left
# as-is rather than breaking the length invariant.
_CANON: dict[str, str] = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",  # ' ' ‚ ‛
    "“": '"', "”": '"', "„": '"', "‟": '"',  # " " „ ‟
    "‐": "-", "‑": "-", "‒": "-", "–": "-",   # ‐ ‑ ‒ –
    "—": "-", "―": "-", "−": "-",                   # — ― −
    " ": " ", " ": " ", " ": " ", " ": " ",   # nbsp, thin spaces
    " ": " ", "\t": " ",
}


def canonicalize(text: str) -> str:
    """Lowercase and fold unicode punctuation/spelling variants onto ASCII.

    One home for both gates (Art. XV). Grounding uses it to match quotes that
    were re-emitted with curly quotes or em-dashes; the negation and quantity
    cues below must agree with it, or Gate 2 goes blind to exactly the text
    Gate 1 tolerates: a live subject's "don’t" (curly) read as un-negated while
    the same words in ASCII read as negated — a false accept in the most
    dangerous direction, verified before this was one function.
    """
    out: list[str] = []
    for ch in text:
        mapped = _CANON.get(ch, ch)
        lowered = mapped.lower()
        out.append(lowered if len(lowered) == 1 else mapped)
    return "".join(out)


# --- negation --------------------------------------------------------------

#: Surface cues that flip the polarity of a statement. Entries wrapped in spaces
#: must match as whole words: bare ``"lack"`` would fire inside "black", and bare
#: ``"no"`` inside "normal". The list is matched against space-padded, lowercased
#: text (see :func:`has_negation`).
NEGATION_CUES: tuple[str, ...] = (
    # explicit particles
    " not ", " no ", " nor ", "n't ",
    # contractions that may end a string (so the trailing-space form misses them)
    "isn't", "aren't", "wasn't", "weren't", "don't", "doesn't", "didn't",
    "won't", "wouldn't", "can't", "cannot", "couldn't", "shouldn't",
    "hasn't", "haven't", "hadn't", "ain't",
    # quantifier and adverb negations
    "nobody", "no one", "none", "nothing", "never", "rarely", "hardly",
    "seldom", "barely",
    # lexical negations
    "unable", "without", " lack", "missing", "absent", "fails to",
    "failed to", "no longer", "stopped",
)


def has_negation(text: str) -> bool:
    """Whether ``text`` carries any negation cue.

    Deliberately boolean rather than a count. Counting is fragile — "it's not a
    problem, not even close" carries two cues and a faithful one-cue restatement
    of it is not an inversion — whereas presence-parity catches the case that
    actually matters: one side negates and the other does not.
    """
    padded = " " + canonicalize(text) + " "
    return any(cue in padded for cue in NEGATION_CUES)


def negation_disagrees(a: str, b: str) -> bool:
    """True when exactly one of the two texts is negated."""
    return has_negation(a) != has_negation(b)


# --- quantity --------------------------------------------------------------

_NUMBER_WORDS: frozenset[str] = frozenset(
    """zero one two three four five six seven eight nine ten eleven twelve
    thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty
    forty fifty sixty seventy eighty ninety hundred thousand million billion
    dozen""".split()
)
# "half" and "quarter" are deliberately absent. Both double as vague quantifiers
# ("half the team") and, for "quarter", as a time unit — so counting them as
# figures made "quarter after quarter" parse as the quantity "quarter quarter".
# A word that is a figure only sometimes is not usable in a gate that must not
# invent disagreements.

#: Units of magnitude. A quantity is a number *and* its unit: swapping "three days"
#: to "three months" distorts the figure exactly as much as swapping the number,
#: and is the more natural thing for a model to get wrong when summarizing.
#:
#: Restricted to time and duration. Countable nouns ("invoice", "step", "ticket")
#: were here first and were wrong: they occur constantly in ordinary description,
#: so two people agreeing about invoice sign-off registered as a quantity dispute.
#: A unit is only ever consulted when a number is attached to it (see
#: :func:`quantities`), which is what keeps "for weeks" and "quarter after quarter"
#: — vague emphasis, not figures — out of the comparison entirely.
_UNIT_WORDS: frozenset[str] = frozenset(
    "second minute hour day week month quarter year decade".split()
)

#: Adverbial and plural forms normalize onto their base unit so ordinary paraphrase
#: ("every week" / "weekly") is not mistaken for an invented figure.
_UNIT_ALIASES: dict[str, str] = {
    "daily": "day", "weekly": "week", "monthly": "month", "quarterly": "quarter",
    "yearly": "year", "annually": "year", "annual": "year", "hourly": "hour",
    "overnight": "day", "fortnightly": "week", "biweekly": "week",
}


def _normalize_unit(word: str) -> str | None:
    """Map a word onto its base unit, or ``None`` if it is not a unit."""
    if word in _UNIT_ALIASES:
        return _UNIT_ALIASES[word]
    singular = word[:-1] if word.endswith("s") and len(word) > 2 else word
    return singular if singular in _UNIT_WORDS else None

#: Digits, optionally with thousands separators or a decimal part, and optionally
#: carrying a unit-ish suffix ("2m", "40k", "3x"). Percent and currency signs are
#: stripped by the surrounding word-boundary split, so "50%" normalizes to "50".
_DIGIT_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def quantities(text: str) -> set[str]:
    """Every figure in ``text`` — numbers and their units — as a normalized set.

    Both spelled-out and numeric forms are collected, because a claim may render a
    quantity either way. Separators are dropped so "2,000" and "2000" compare
    equal. Units are folded onto a base form so "every week" and "weekly" agree,
    while "days" and "months" stay distinct.

    Magnitude across notations is *not* reconciled — "three" and "3" remain
    different tokens. Treating them as equal needs real parsing, and the safe
    direction for a gate is to flag rather than to assume.
    """
    lowered = canonicalize(text)
    tokens = re.findall(r"\d[\d,]*(?:\.\d+)?|[a-z]+", lowered)
    found: set[str] = set()
    for i, token in enumerate(tokens):
        is_number = token in _NUMBER_WORDS or _DIGIT_RE.fullmatch(token) is not None
        if not is_number:
            continue
        number = token.replace(",", "")
        # Look one token ahead for a unit ("three days", "48 hours"), and two ahead
        # to step over an intervening modifier ("three business days").
        unit = None
        for lookahead in (1, 2):
            if i + lookahead < len(tokens):
                unit = _normalize_unit(tokens[i + lookahead])
                if unit is not None:
                    break
        found.add(f"{number} {unit}" if unit else number)
    return found


def invents_quantity(claim: str, source: str) -> str | None:
    """The first quantity asserted by ``claim`` that ``source`` does not contain.

    Returns ``None`` when every number in the claim is present in the source.
    Extra numbers in the *source* are fine — a claim may summarize part of a
    quote. The dangerous direction is the claim asserting a figure nobody said.
    """
    source_numbers = quantities(source)
    for number in sorted(quantities(claim)):
        if number not in source_numbers:
            return number
    return None
