"""The safety-gate fuzz audit, run bounded so it can live in CI.

The audit itself is the test: it generates thousands of near-miss inputs and asserts
properties that must hold for all of them. A few seeds are pinned here; the deeper
sweep (`python -m ai_engine.fuzz --cases 1500 --seed N`) is for local runs.
"""
import unittest

from ai_engine.fuzz import run_fuzz
from ai_engine.fuzz.mutations import (
    COSMETIC_MUTATORS,
    SEMANTIC_MUTATORS,
    is_contiguous_sublist,
    normalized_words,
)


class MutationSanityTest(unittest.TestCase):
    """The mutators themselves must do what the audit assumes."""

    SAMPLE = "I keep a private spreadsheet instead of the official tool"

    def test_cosmetic_mutations_preserve_the_words(self):
        # This is the assumption that makes "must still ground" a valid assertion.
        base = normalized_words(self.SAMPLE)
        for name, mutate in COSMETIC_MUTATORS:
            with self.subTest(mutator=name):
                mutated = normalized_words(mutate(self.SAMPLE))
                if name in ("strip_trailing_punct", "add_trailing_period"):
                    self.assertEqual(mutated[: len(base)], base)
                else:
                    self.assertEqual(mutated, base)

    def test_semantic_mutations_change_the_words(self):
        import random

        rng = random.Random(0)
        base = normalized_words(self.SAMPLE)
        for name, mutate in SEMANTIC_MUTATORS:
            with self.subTest(mutator=name):
                out = mutate(self.SAMPLE, rng)
                if out is None:
                    continue  # inapplicable to this sample
                self.assertNotEqual(normalized_words(out), base)

    def test_contiguous_sublist_helper(self):
        self.assertTrue(is_contiguous_sublist(["b", "c"], ["a", "b", "c", "d"]))
        self.assertFalse(is_contiguous_sublist(["b", "d"], ["a", "b", "c", "d"]))
        self.assertFalse(is_contiguous_sublist([], ["a"]))


class SafetyGateAuditTest(unittest.TestCase):
    def _assert_clean(self, seed: int, cases: int = 200):
        report = run_fuzz(cases=cases, seed=seed, org_size=5)
        self.assertGreater(report.total_checked, 200, "audit did not exercise the gates")
        if report.violations:
            detail = "\n".join(
                f"  {v.severity} {v.prop}: {v.detail} | {v.original!r} -> {v.mutated!r}"
                for v in report.violations[:10]
            )
            self.fail(f"{len(report.violations)} property violation(s):\n{detail}")

    def test_audit_is_clean_on_pinned_seeds(self):
        for seed in (0, 1, 2, 3, 4):
            with self.subTest(seed=seed):
                self._assert_clean(seed)

    def test_audit_covers_every_property(self):
        report = run_fuzz(cases=200, seed=0, org_size=5)
        for prop in (
            "grounding_accepts_cosmetic",
            "grounding_rejects_semantic",
            "grounding_rejects_interviewer_quote",
            "evidence_offsets_are_faithful",
            "entailment_accepts_faithful",
            "entailment_rejects_escalation",
            "entailment_rejects_negation",
            "entailment_rejects_number_change",
            "gates_never_crash",
        ):
            with self.subTest(prop=prop):
                self.assertGreater(report.checked.get(prop, 0), 0,
                                   f"{prop} was never exercised")

    def test_audit_detects_a_deliberately_broken_gate(self):
        # A meta-test: if the fuzzer cannot catch a gate that accepts everything,
        # a green audit would mean nothing.
        import ai_engine.fuzz.runner as runner

        original = runner.ground_proposal

        def always_accept(proposal, transcript):
            segment = next(s for s in transcript.segments)
            from ai_engine.evidence.model import Claim, ClaimType, GroundedEvidence
            from ai_engine.transcript.model import EvidenceRef, Speaker
            claim = Claim(
                id="clm-bad", claim_type=ClaimType.OBSERVATION,
                statement=proposal.statement,
                evidence=(GroundedEvidence(
                    EvidenceRef(segment.id, 0, len(segment.text)), proposal.quote, "exact"),),
                speaker=Speaker.SUBJECT, tier=2)
            return claim, "grounded"

        runner.ground_proposal = always_accept
        try:
            report = run_fuzz(cases=60, seed=0, org_size=4)
        finally:
            runner.ground_proposal = original
        self.assertFalse(report.passed, "fuzzer failed to catch a gate that accepts all")
        self.assertTrue(any(v.severity == "false_accept" for v in report.violations))


if __name__ == "__main__":
    unittest.main()
