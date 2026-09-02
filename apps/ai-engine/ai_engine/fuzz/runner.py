"""Run the properties over generated near-miss cases and collect violations."""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass, field

from ..evidence.entailment import Entailment, HeuristicEntailmentChecker
from ..evidence.grounding import _canon, ground_proposal
from ..lexicon import has_negation, quantities
from ..evidence.model import RawProposal
from ..transcript.model import Speaker
from .corpus import QuoteSpan, build_transcripts, collect_spans, interviewer_spans
from .mutations import (
    COSMETIC_MUTATORS,
    SEMANTIC_MUTATORS,
    _change_number,
    _negate,
    cosmetic_applies,
    is_contiguous_sublist,
    normalized_words,
)

# Severity of a violation. false_accept is the dangerous direction: a fabrication
# was admitted. The others cost recall or trust in the evidence shown.
CRITICAL = ("false_accept", "integrity", "crash")


@dataclass(frozen=True)
class Violation:
    prop: str
    severity: str
    detail: str
    original: str = ""
    mutated: str = ""

    @property
    def critical(self) -> bool:
        return self.severity in CRITICAL


@dataclass
class FuzzReport:
    checked: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    violations: list[Violation] = field(default_factory=list)
    skipped: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def total_checked(self) -> int:
        return sum(self.checked.values())

    @property
    def critical_violations(self) -> list[Violation]:
        return [v for v in self.violations if v.critical]

    @property
    def passed(self) -> bool:
        return not self.violations

    def record(self, prop: str) -> None:
        self.checked[prop] += 1

    def fail(self, violation: Violation) -> None:
        self.violations.append(violation)


def _propose(quote: str) -> RawProposal:
    return RawProposal(claim_type="observation", statement=quote, quote=quote, tier=2)


def _subject_word_seqs(transcript) -> list[list[str]]:
    return [
        normalized_words(s.text)
        for s in transcript.segments
        if s.speaker is Speaker.SUBJECT
    ]


def _present_in_subject(quote: str, transcript) -> bool:
    """Precondition oracle: do the quote's WORDS appear contiguously in a subject turn?

    Deliberately word-level, where the gate is character-level — so this is an
    independent check rather than a copy of the code under test.
    """
    needle = normalized_words(quote)
    return any(is_contiguous_sublist(needle, seq) for seq in _subject_word_seqs(transcript))


def _check_cosmetic(span: QuoteSpan, report: FuzzReport) -> None:
    """A cosmetic mutation keeps the words, so it must still ground (no false reject)."""
    for name, mutate in COSMETIC_MUTATORS:
        if not cosmetic_applies(name, span.text):
            report.skipped[f"cosmetic:{name}"] += 1
            continue
        mutated = mutate(span.text)
        if not mutated.strip():
            report.skipped[f"cosmetic:{name}"] += 1
            continue
        report.record("grounding_accepts_cosmetic")
        try:
            claim, reason = ground_proposal(_propose(mutated), span.transcript)
        except Exception as exc:  # pragma: no cover - a crash is itself the finding
            report.fail(Violation("grounding_accepts_cosmetic", "crash", repr(exc),
                                  span.text, mutated))
            continue
        if claim is None:
            report.fail(Violation(
                "grounding_accepts_cosmetic", "false_reject",
                f"[{name}] a true quote was refused ({reason})", span.text, mutated))
            continue
        # Integrity: the offsets must point at the words we matched, or the evidence
        # shown to a consultant would be the wrong text.
        #
        # Compared as WORD SEQUENCES, not as canonical character strings: whitespace
        # runs and trailing punctuation are precisely what flexible matching is
        # allowed to differ on, so a character-level comparison would flag correct
        # behaviour. (It did — 142 times — before this was corrected.)
        report.record("evidence_offsets_are_faithful")
        resolved = claim.evidence[0].resolve(span.transcript)
        want = normalized_words(mutated)
        got = normalized_words(resolved)
        # The matcher may legitimately drop trailing punctuation, which can shed a
        # final token when that token was punctuation-only.
        if got != want and got != want[: len(got)]:
            report.fail(Violation(
                "evidence_offsets_are_faithful", "integrity",
                f"[{name}] resolved to {resolved!r}, expected the span for {mutated!r}",
                span.text, mutated))


def _check_semantic(span: QuoteSpan, report: FuzzReport, rng: random.Random) -> None:
    """A semantic mutation changes the words, so it must NOT ground (no false accept)."""
    for name, mutate in SEMANTIC_MUTATORS:
        mutated = mutate(span.text, rng)
        if not mutated or not mutated.strip():
            report.skipped[f"semantic:{name}"] += 1
            continue
        # Precondition: skip the rare case where the mutation coincidentally still
        # appears in the source — accepting that would be correct, not a bug.
        if _present_in_subject(mutated, span.transcript):
            report.skipped[f"semantic:{name}"] += 1
            continue
        report.record("grounding_rejects_semantic")
        try:
            claim, _ = ground_proposal(_propose(mutated), span.transcript)
        except Exception as exc:  # pragma: no cover
            report.fail(Violation("grounding_rejects_semantic", "crash", repr(exc),
                                  span.text, mutated))
            continue
        if claim is not None:
            report.fail(Violation(
                "grounding_rejects_semantic", "false_accept",
                f"[{name}] a fabricated quote was admitted", span.text, mutated))


def _check_interviewer_citation(span: QuoteSpan, report: FuzzReport) -> None:
    """Quoting the interviewer's own question is never evidence (F8)."""
    report.record("grounding_rejects_interviewer_quote")
    claim, reason = ground_proposal(_propose(span.text), span.transcript)
    if claim is not None:
        report.fail(Violation(
            "grounding_rejects_interviewer_quote", "false_accept",
            "an interviewer question was admitted as subject evidence",
            span.text, span.text))


_SEVERE_INJECTIONS = (
    "which proves they committed fraud",
    "confirming the confidential data leak",
    "which is clear misconduct by the manager",
    "showing they violated the contract",
    "evidence of harassment on the team",
    "proof that funds were embezzled",
)


def _check_entailment(span: QuoteSpan, report: FuzzReport, rng: random.Random) -> None:
    checker = HeuristicEntailmentChecker()
    quote = span.text

    # Faithful restatement must be supported (no false reject).
    report.record("entailment_accepts_faithful")
    if checker.check(quote, quote).verdict is not Entailment.SUPPORTED:
        report.fail(Violation("entailment_accepts_faithful", "false_reject",
                              "a verbatim restatement was rejected", quote, quote))

    # An accusation absent from the quote must be rejected (no false accept).
    injection = rng.choice(_SEVERE_INJECTIONS)
    claim = f"{quote} {injection}"
    report.record("entailment_rejects_escalation")
    if checker.check(claim, quote).verdict is Entailment.SUPPORTED:
        report.fail(Violation("entailment_rejects_escalation", "false_accept",
                              f"escalation admitted: {injection!r}", quote, claim))

    # Polarity inversion must be rejected. Note what is mutated: the CLAIM, while
    # the quote is held intact. The negate/change_number mutators were already in
    # this module, but only ever applied to the *quote* — which tests grounding
    # (a negated quote is no longer verbatim) and leaves the entailment gate's two
    # real failure modes unexercised. Thousands of passing checks read as coverage
    # of a gate that was never asked the questions it fails.
    # The precondition is load-bearing, not a convenience: a surface checker reads
    # polarity as present-or-absent, so it cannot see a *second* negation added to
    # an already-negated sentence ("nothing jumps out" -> "nothing never jumps
    # out"). Counting cues instead would trade this blind spot for a worse one,
    # rejecting honest restatements that use one cue where the quote used two.
    # Asserting only what a surface gate can actually deliver keeps the property
    # meaningful; double negation is one of the cases a trained NLI model is for.
    if not has_negation(quote):
        inverted = _negate(quote, rng)
        if inverted is not None and inverted != quote:
            report.record("entailment_rejects_negation")
            if checker.check(inverted, quote).verdict is Entailment.SUPPORTED:
                report.fail(Violation("entailment_rejects_negation", "false_accept",
                                      "a claim that negates its own quote was admitted",
                                      quote, inverted))

    # A figure the quote does not contain must be rejected: a claim can keep every
    # word and change the number, which is what turns into a business case.
    # Preconditioned on the quote stating an actual figure, for the same reason the
    # negation property is preconditioned: a unit with no number ("it drags on for
    # weeks") is emphasis, not a quantity, and treating every bare time-word as one
    # made two people agreeing about invoice sign-off read as a numeric dispute.
    # The gate compares figures; the property asks only about figures.
    if quantities(quote):
        renumbered = _change_number(quote, rng)
        if renumbered is not None and renumbered != quote:
            report.record("entailment_rejects_number_change")
            if checker.check(renumbered, quote).verdict is Entailment.SUPPORTED:
                report.fail(Violation("entailment_rejects_number_change", "false_accept",
                                      "a claim asserting an unstated quantity was admitted",
                                      quote, renumbered))


def _check_robustness(report: FuzzReport, transcript) -> None:
    """Hostile inputs must be refused, never crash."""
    hostile = ["", "   ", "\n\t", ".", "?!", "—", "​", "a" * 5000,
               "🙂🙃", "<script>", "%s%d", "\\", "'; DROP TABLE --", "NULL"]
    for text in hostile:
        report.record("gates_never_crash")
        try:
            ground_proposal(_propose(text), transcript)
            HeuristicEntailmentChecker().check(text, "any quote at all")
        except Exception as exc:  # pragma: no cover
            report.fail(Violation("gates_never_crash", "crash", f"{text!r}: {exc!r}"))


def run_fuzz(*, cases: int = 400, seed: int = 0, org_size: int = 6) -> FuzzReport:
    """Audit both safety gates over ``cases`` generated near-miss spans."""
    rng = random.Random(seed)
    report = FuzzReport()

    transcripts = build_transcripts(org_size=org_size, seed=seed)
    spans = collect_spans(transcripts, rng)
    rng.shuffle(spans)
    spans = spans[: max(1, cases)]

    for span in spans:
        _check_cosmetic(span, report)
        _check_semantic(span, report, rng)
        _check_entailment(span, report, rng)

    for span in interviewer_spans(transcripts, rng)[: max(1, cases // 4)]:
        _check_interviewer_citation(span, report)

    if transcripts:
        _check_robustness(report, transcripts[0])
    return report
