"""Regression tests for the shared negation and quantity lexicon.

Every case here was a real false verdict before ``ai_engine/lexicon.py`` existed.
The cue lists are load-bearing safety logic — a missing entry silently converts a
contradiction into corroboration — so each cue gets its own assertion rather than
being spot-checked in aggregate.
"""
from __future__ import annotations

import unittest

from ai_engine.aggregation.model import Relation
from ai_engine.aggregation.relation import HeuristicRelationChecker
from ai_engine.evidence.entailment import Entailment, HeuristicEntailmentChecker
from ai_engine.lexicon import (
    NEGATION_CUES,
    canonicalize,
    has_negation,
    invents_quantity,
    negation_disagrees,
    quantities,
)


class CanonicalizationTest(unittest.TestCase):
    """One canonicalizer for both gates (Art. XV) — and it must actually fire.

    Grounding matches a curly-apostrophe quote to its ASCII twin; if the negation
    cues below only ever see raw text, Gate 2 goes blind to exactly the text Gate 1
    tolerates: "We don’t have a problem" quoted as "We have a problem" was admitted
    before this was one function.
    """

    def test_folds_typographic_apostrophes_and_case(self):
        self.assertEqual(canonicalize("Don’t"), "don't")
        self.assertEqual(canonicalize("We DON’T — “fine”"), "we don't - \"fine\"")

    def test_is_length_preserving(self):
        # The offset invariant EvidenceRef rests on: an index in the canonicalized
        # text is the same index in the original.
        source = "Don’t ‒ “fine” \u00a0 ok"
        self.assertEqual(len(canonicalize(source)), len(source))

    def test_negation_behind_typographic_apostrophe_is_seen(self):
        self.assertTrue(has_negation("We don’t have a documented process."))
        self.assertTrue(has_negation("The dashboard isn’t accurate."))

    def test_parity_holds_across_apostrophe_styles(self):
        # Same words, different spelling: not a polarity disagreement.
        self.assertFalse(negation_disagrees("We don't have a runbook.",
                                            "We don’t have a runbook."))


class NegationCueTest(unittest.TestCase):
    """Each cue must actually fire, and ordinary prose must not."""

    #: One natural sentence per cue. Kept explicit rather than generated: the point
    #: is that a human read each one and agreed it reads as a negation.
    SENTENCES = {
        " not ": "That is not how it works here.",
        " no ": "There is no documented process.",
        " nor ": "Neither finance nor ops signs off.",
        "n't ": "We don't have a runbook for it.",
        "isn't": "The dashboard isn't accurate.",
        "aren't": "The numbers aren't reconciled.",
        "wasn't": "The step wasn't in the SOP.",
        "weren't": "They weren't told about the change.",
        "don't": "I don't use the official tool.",
        "doesn't": "It doesn't happen that way.",
        "didn't": "Nobody didn't get the memo, apparently.",
        "won't": "The system won't let me submit it.",
        "wouldn't": "My manager wouldn't approve it.",
        "can't": "I can't close the books on time.",
        "cannot": "Finance cannot close the books on time.",
        "couldn't": "We couldn't reconcile the accounts.",
        "shouldn't": "It shouldn't take three days.",
        "hasn't": "The policy hasn't been updated.",
        "haven't": "We haven't seen that form in a year.",
        "hadn't": "They hadn't approved it yet.",
        "ain't": "That ain't the real process.",
        "nobody": "Nobody follows the documented process.",
        "no one": "No one owns that handoff.",
        "none": "None of the steps are automated.",
        "nothing": "Nothing gets escalated properly.",
        "never": "The vendor never misses a deadline.",
        "rarely": "We rarely get sign-off in time.",
        "hardly": "That form is hardly ever used.",
        "seldom": "The committee seldom meets.",
        "barely": "We barely finish before the deadline.",
        "unable": "I am unable to approve above my limit.",
        "without": "It ships without a second review.",
        " lack": "We lack a clear owner for this.",
        "missing": "The approval step is missing entirely.",
        "absent": "The policy is absent from the handbook.",
        "fails to": "The system fails to notify us.",
        "failed to": "Finance failed to reconcile the ledger.",
        "no longer": "That team no longer handles it.",
        "stopped": "We stopped using the portal last year.",
    }

    def test_every_cue_has_a_sentence(self):
        """A new cue without a test case is an untested safety rule."""
        self.assertEqual(
            set(NEGATION_CUES), set(self.SENTENCES),
            "NEGATION_CUES and the test sentences have diverged — add a case for "
            "any new cue, and remove the case for any cue you delete.",
        )

    def test_each_cue_fires(self):
        for cue, sentence in self.SENTENCES.items():
            with self.subTest(cue=cue):
                self.assertTrue(
                    has_negation(sentence), f"cue {cue!r} did not fire on {sentence!r}"
                )

    def test_plain_statements_are_not_negated(self):
        for sentence in (
            "Approvals take three days.",
            "The black box sits in the corner.",   # must not match " lack"
            "That is normal for this team.",       # must not match " no "
            "Finance closes the books on time.",
            "I rebuild the weekly report by hand.",
        ):
            with self.subTest(sentence=sentence):
                self.assertFalse(has_negation(sentence))

    def test_disagreement_is_one_sided_negation(self):
        self.assertTrue(negation_disagrees("It is a problem", "It is not a problem"))
        self.assertFalse(negation_disagrees("It is a problem", "It is a problem"))
        self.assertFalse(
            negation_disagrees("I don't have time", "I never have time"),
            "two differently-worded negations still agree in polarity",
        )


class QuantityTest(unittest.TestCase):
    def test_number_binds_to_its_unit(self):
        self.assertEqual(quantities("Approvals take three days"), {"three day"})
        self.assertEqual(quantities("about 4.5 hours"), {"4.5 hour"})
        self.assertEqual(quantities("three business days"), {"three day"})

    def test_bare_numbers_have_no_unit(self):
        self.assertEqual(quantities("I raised 12 tickets"), {"12"})
        self.assertEqual(quantities("no numbers here"), set())

    def test_units_without_a_number_are_not_quantities(self):
        """Vague emphasis is not a figure — this is what stops false conflicts."""
        self.assertEqual(quantities("it drags on for weeks"), set())
        self.assertEqual(quantities("quarter after quarter, nothing changes"), set())

    def test_unit_aliases_normalize(self):
        """Ordinary paraphrase of the same figure must not read as a new figure."""
        self.assertEqual(quantities("2 weekly"), quantities("2 weeks"))
        self.assertEqual(quantities("3 annually"), quantities("3 years"))
        self.assertIsNone(invents_quantity("4 hourly", "4 hours"))

    def test_changed_number_is_detected(self):
        self.assertEqual(
            invents_quantity("Approvals take thirty days", "Approvals take three days"),
            "thirty day",
        )

    def test_changed_unit_is_detected(self):
        """Swapping the unit distorts the figure as much as swapping the number."""
        self.assertEqual(
            invents_quantity("Approvals take three months", "Approvals take three days"),
            "three month",
        )

    def test_summarising_fewer_numbers_is_allowed(self):
        """A claim may mention less than the quote; it may not invent more."""
        self.assertIsNone(
            invents_quantity("Approvals take three days",
                            "Approvals take three days and cost 200 each")
        )


class EntailmentRegressionTest(unittest.TestCase):
    """The four verdicts that were wrong before this change."""

    def setUp(self):
        self.checker = HeuristicEntailmentChecker()

    def assertRejected(self, claim: str, quote: str):
        result = self.checker.check(claim, quote)
        self.assertIs(result.verdict, Entailment.NOT_SUPPORTED,
                      f"admitted {claim!r} against {quote!r}: {result.reason}")

    def test_rejects_negation_inversion(self):
        self.assertRejected(
            "The approval step is a problem.",
            "I don't think the approval step is a problem at all.",
        )

    def test_rejects_inverted_never(self):
        self.assertRejected(
            "The vendor misses deadlines.",
            "The vendor never misses a deadline.",
        )

    def test_rejects_changed_number(self):
        self.assertRejected("Approvals take thirty days.", "Approvals take three days.")

    def test_rejects_invented_cost(self):
        self.assertRejected(
            "Approvals take three days and cost the company $2M annually.",
            "Approvals take three days.",
        )

    def test_still_accepts_faithful_restatement(self):
        result = self.checker.check(
            "I rebuild the weekly report by hand, about four hours every week.",
            "I rebuild the weekly report by hand, about four hours every week.",
        )
        self.assertIs(result.verdict, Entailment.SUPPORTED, result.reason)

    def test_still_accepts_faithful_negative_claim(self):
        """A negated quote supports a negated claim — polarity must match, not vanish."""
        result = self.checker.check(
            "The team does not have a documented process.",
            "We don't have a documented process for any of this.",
        )
        self.assertIs(result.verdict, Entailment.SUPPORTED, result.reason)


class RelationRegressionTest(unittest.TestCase):
    """Contradictions that were being scored as corroboration."""

    def setUp(self):
        self.checker = HeuristicRelationChecker()

    def test_cannot_versus_always_is_a_conflict(self):
        self.assertIs(
            self.checker.classify(
                "Finance cannot close the books on time.",
                "Finance closes the books on time, always.",
            ),
            Relation.CONFLICT,
        )

    def test_one_sided_negation_is_a_conflict(self):
        self.assertIs(
            self.checker.classify(
                "The approval process is followed as documented.",
                "The approval process is not followed as documented.",
            ),
            Relation.CONFLICT,
        )

    def test_different_figures_conflict(self):
        self.assertIs(
            self.checker.classify(
                "Approvals take three days.",
                "Approvals take thirty days.",
            ),
            Relation.CONFLICT,
        )

    def test_identical_statements_still_agree(self):
        self.assertIs(
            self.checker.classify(
                "My manager approves invoices within a day.",
                "My manager approves invoices within a day.",
            ),
            Relation.AGREE,
        )


if __name__ == "__main__":
    unittest.main()
