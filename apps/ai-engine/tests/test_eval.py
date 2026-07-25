"""The evaluation harness: matching, scoring, gates, and the suite."""
import unittest

from ai_engine.eval.dataset import default_suite
from ai_engine.eval.gates import evaluate_gates, case_passed
from ai_engine.eval.matching import assign_findings_to_truths, match_score
from ai_engine.eval.metrics import CaseMetrics, score_case
from ai_engine.eval.runner import run_case, run_suite
from ai_engine.evidence.model import Claim, ClaimType, GroundedEvidence
from ai_engine.subjects.simulated import default_persona
from ai_engine.transcript.model import EvidenceRef, Speaker, Transcript


class MatchingTest(unittest.TestCase):
    def test_statement_containment_is_a_strong_match(self):
        truth = default_persona().latent_truths[1]  # the spreadsheet truth
        self.assertGreaterEqual(match_score(truth.statement, truth), 1000)

    def test_unrelated_text_does_not_match(self):
        truth = default_persona().latent_truths[1]
        self.assertLess(match_score("We had a nice team lunch on Friday.", truth), 2)

    def test_greedy_assignment_is_one_to_one(self):
        truths = default_persona().latent_truths
        # Two findings quoting two different truths -> two distinct captures.
        texts = [truths[1].statement, truths[4].statement]
        captured, matched = assign_findings_to_truths(texts, truths)
        self.assertEqual(len(captured), 2)
        self.assertEqual(len(matched), 2)


class GateTest(unittest.TestCase):
    def _metrics(self, **kw):
        base = dict(persona="p", candor="open", is_ceiling=True, achievable=4,
                    elicited=4, claims=4, matched_claims=4, captured=4,
                    tier2plus_claims=4, confabulation_rate=0.0, candor_leak=0)
        base.update(kw)
        return CaseMetrics(**base)

    def test_confabulation_fails_safety_gate(self):
        results = evaluate_gates(self._metrics(confabulation_rate=0.2))
        self.assertFalse(case_passed(results))
        self.assertFalse(next(r for r in results if r.name == "no_confabulation").passed)

    def test_candor_leak_fails_safety_gate(self):
        self.assertFalse(case_passed(evaluate_gates(self._metrics(candor_leak=1))))

    def test_capability_gates_only_apply_at_ceiling(self):
        # A weak non-ceiling case (low recall) still passes — only safety applies.
        weak = self._metrics(is_ceiling=False, captured=0, tier2plus_claims=0,
                             matched_claims=0, claims=0)
        names = {r.name for r in evaluate_gates(weak)}
        self.assertNotIn("recovers_truth", names)
        self.assertTrue(case_passed(evaluate_gates(weak)))

    def test_low_recall_fails_capability_gate_at_ceiling(self):
        weak_ceiling = self._metrics(captured=1, achievable=6)  # 17% recall
        self.assertFalse(case_passed(evaluate_gates(weak_ceiling)))


class ScoreCaseTest(unittest.TestCase):
    def test_scores_a_hand_built_case(self):
        persona = default_persona("open")
        truth = persona.latent_truths[1]  # spreadsheet, tier 2
        t = Transcript()
        t.append(Speaker.INTERVIEWER, "Any workarounds?")
        seg = t.append(Speaker.SUBJECT, truth.statement)
        t.finalize()
        claim = Claim(id="clm-1", claim_type=ClaimType.WORKAROUND, statement="spreadsheet",
                      evidence=(GroundedEvidence(EvidenceRef(seg.id, 0, len(seg.text)),
                                                 seg.text, "exact"),),
                      speaker=Speaker.SUBJECT, tier=2)
        m = score_case(persona="ops", candor="open", is_ceiling=True,
                       gold=persona.latent_truths, transcript=t, claims=[claim],
                       confabulation_rate=0.0)
        self.assertEqual(m.captured, 1)
        self.assertEqual(m.matched_claims, 1)
        self.assertEqual(m.precision, 1.0)
        self.assertEqual(m.candor_leak, 0)


class SuiteTest(unittest.TestCase):
    def test_mock_suite_passes(self):
        self.assertTrue(run_suite().passed)

    def test_candor_curve_is_non_decreasing(self):
        # Measured as the ABSOLUTE number of truths elicited, not as recall.
        # Recall is a ratio whose denominator grows with candor — a guarded persona has
        # one reachable truth, so finding it scores 100% while an open persona finding
        # five of six scores 83%. Comparing those ratios across candor levels compares
        # different denominators and reads a success as a regression.
        suite = run_suite()
        by_persona: dict[str, dict[str, int]] = {}
        for c in suite.cases:
            by_persona.setdefault(c.persona, {})[c.candor] = c.runs[0].elicited
        for persona, curve in by_persona.items():
            with self.subTest(persona=persona):
                self.assertLessEqual(curve["guarded"], curve["neutral"])
                self.assertLessEqual(curve["neutral"], curve["open"])

    def test_more_candor_yields_strictly_more_truth(self):
        # The substantive claim the curve exists to make.
        suite = run_suite()
        for persona in {c.persona for c in suite.cases}:
            cases = {c.candor: c.runs[0] for c in suite.cases if c.persona == persona}
            with self.subTest(persona=persona):
                self.assertGreater(cases["open"].elicited, cases["guarded"].elicited)

    def test_no_case_fabricates(self):
        for c in run_suite().cases:
            self.assertEqual(c.runs[0].confabulation_rate, 0.0)
            self.assertEqual(c.runs[0].candor_leak, 0)

    def test_open_case_recovers_meaningful_truth(self):
        result = run_case(next(c for c in default_suite() if c.name == "ops-analyst/open"))
        self.assertGreaterEqual(result.runs[0].e2e_recall, 0.5)
        self.assertTrue(result.passed)

    def test_repeats_produce_multiple_runs(self):
        result = run_case(next(c for c in default_suite() if c.name == "ops-analyst/open"), repeats=3)
        self.assertEqual(len(result.runs), 3)
        # Mock mode is deterministic, so the spread is zero.
        lo, mean, hi = result.stat(lambda m: m.e2e_recall)
        self.assertEqual(lo, hi)


if __name__ == "__main__":
    unittest.main()
