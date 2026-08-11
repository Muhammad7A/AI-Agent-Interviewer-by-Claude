"""Mutation generators, split by whether they change the WORDS or only the CHARACTERS.

That split is the whole basis of the audit's rigour: it determines the expected
answer without consulting the code under test.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Callable

# --- word-level normalisation, used for preconditions ----------------------

_PUNCT = re.compile(r"[^\w\s]")


def normalized_words(text: str) -> list[str]:
    """Lowercased word sequence with punctuation dropped."""
    return _PUNCT.sub(" ", text.lower()).split()


def is_contiguous_sublist(needle: list[str], haystack: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    first = needle[0]
    for i in range(len(haystack) - len(needle) + 1):
        if haystack[i] == first and haystack[i : i + len(needle)] == needle:
            return True
    return False


# --- cosmetic mutations: same words, different characters -------------------

CosmeticMutator = Callable[[str], str]


def _curly_quotes(text: str) -> str:
    return text.replace("'", "’").replace('"', "“")


def _unicode_dashes(text: str) -> str:
    return text.replace("-", "—")


def _nbsp(text: str) -> str:
    return text.replace(" ", " ")


def _thin_space(text: str) -> str:
    return text.replace(" ", " ")


def _upper(text: str) -> str:
    return text.upper()


def _lower(text: str) -> str:
    return text.lower()


def _swap_case(text: str) -> str:
    return text.swapcase()


def _expand_whitespace(text: str) -> str:
    return re.sub(r" ", "   ", text)


def _strip_trailing_punct(text: str) -> str:
    return text.rstrip(" .,;:!?\"'")


def _add_trailing_period(text: str) -> str:
    return text + "."


def _pad(text: str) -> str:
    return f"  {text}  "


# Case-changing mutators are only safe on ASCII: uppercasing some non-ASCII
# characters changes the string's LENGTH (e.g. "ß" -> "SS"), which is a genuinely
# different situation from a cosmetic re-spelling and not what this audit covers.
_ASCII_ONLY = {"upper", "lower", "swap_case"}

COSMETIC_MUTATORS: tuple[tuple[str, CosmeticMutator], ...] = (
    ("curly_quotes", _curly_quotes),
    ("unicode_dashes", _unicode_dashes),
    ("nbsp", _nbsp),
    ("thin_space", _thin_space),
    ("upper", _upper),
    ("lower", _lower),
    ("swap_case", _swap_case),
    ("expand_whitespace", _expand_whitespace),
    ("strip_trailing_punct", _strip_trailing_punct),
    ("add_trailing_period", _add_trailing_period),
    ("pad", _pad),
)


def cosmetic_applies(name: str, text: str) -> bool:
    if name in _ASCII_ONLY and not text.isascii():
        return False
    return True


# --- semantic mutations: the words change ----------------------------------

SemanticMutator = Callable[[str, random.Random], "str | None"]

# Replacement words chosen to be plausible but distinct from the corpus vocabulary,
# so a substitution is unlikely to coincidentally reproduce the source.
_REPLACEMENTS = (
    "database", "auditor", "quarterly", "vendor", "hallway", "printer",
    "spreadsheet", "committee", "midnight", "kettle", "forklift", "invoice",
)

_NUMBER_WORDS = {
    "one": "nine", "two": "seven", "three": "eleven", "four": "twelve",
    "five": "twenty", "days": "months", "weeks": "years", "week": "decade",
    "overnight": "annually",
}


def _tokens_with_space(text: str) -> list[str]:
    """Split on spaces, preserving nothing else — so joins are lossless."""
    return text.split(" ")


def _substitute_word(text: str, rng: random.Random) -> str | None:
    parts = _tokens_with_space(text)
    idx = [i for i, p in enumerate(parts) if len(re.sub(r"\W", "", p)) >= 3]
    if not idx:
        return None
    i = rng.choice(idx)
    parts[i] = rng.choice(_REPLACEMENTS)
    return " ".join(parts)


def _delete_middle_word(text: str, rng: random.Random) -> str | None:
    parts = _tokens_with_space(text)
    # Only the middle: deleting a first or last word leaves a string that is still a
    # genuine substring of the source, which would be a correct accept, not a bug.
    if len(parts) < 3:
        return None
    i = rng.randrange(1, len(parts) - 1)
    return " ".join(parts[:i] + parts[i + 1 :])


def _insert_middle_word(text: str, rng: random.Random) -> str | None:
    parts = _tokens_with_space(text)
    if len(parts) < 2:
        return None
    i = rng.randrange(1, len(parts))
    return " ".join(parts[:i] + [rng.choice(_REPLACEMENTS)] + parts[i:])


def _negate(text: str, rng: random.Random) -> str | None:
    parts = _tokens_with_space(text)
    if len(parts) < 2:
        return None
    i = rng.randrange(1, len(parts))
    return " ".join(parts[:i] + [rng.choice(("not", "never", "rarely"))] + parts[i:])


def _swap_adjacent(text: str, rng: random.Random) -> str | None:
    parts = _tokens_with_space(text)
    if len(parts) < 3:
        return None
    candidates = [i for i in range(len(parts) - 1) if parts[i] != parts[i + 1]]
    if not candidates:
        return None
    i = rng.choice(candidates)
    parts[i], parts[i + 1] = parts[i + 1], parts[i]
    return " ".join(parts)


def _change_number(text: str, rng: random.Random) -> str | None:
    parts = _tokens_with_space(text)
    for i, part in enumerate(parts):
        bare = re.sub(r"\W", "", part).lower()
        if bare in _NUMBER_WORDS:
            parts[i] = part.lower().replace(bare, _NUMBER_WORDS[bare])
            return " ".join(parts)
        if bare.isdigit():
            parts[i] = part.replace(bare, str(int(bare) + 7))
            return " ".join(parts)
    return None


SEMANTIC_MUTATORS: tuple[tuple[str, SemanticMutator], ...] = (
    ("substitute_word", _substitute_word),
    ("delete_middle_word", _delete_middle_word),
    ("insert_middle_word", _insert_middle_word),
    ("negate", _negate),
    ("swap_adjacent", _swap_adjacent),
    ("change_number", _change_number),
)


@dataclass(frozen=True)
class Mutation:
    name: str
    kind: str      # "cosmetic" | "semantic"
    original: str
    mutated: str
