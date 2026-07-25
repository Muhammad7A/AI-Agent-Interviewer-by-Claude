"""Confidence derivation and calibration measurement."""
import unittest

from ai_engine.aggregation.aggregator import aggregate
from ai_engine.aggregation.model import ParticipantFinding
from ai_engine.aggregation.relation import HeuristicRelationChecker
from ai_engine.confidence.calibration import ScoredOutcome, calibrate
from ai_engine.confidence.model import ConfidenceBand
from ai_engine.confidence.scenario import MISTAKEN_IDS, is_veridical, meridian_org
from ai_engine.confidence.scorer import score_member, score_topic
from ai_engine.confidence.study import run_study


def _pf(pid, statement, tier=2, match_kind="exact"):
    return ParticipantFinding(
        participant_id=pid, participant_name=pid, claim_type="friction",
        statement=statement, tier=tier, evidence_quote=statement,
        segment_id=f"seg-{pid}", transcript_id=f"txn-{pid}", match_kind=match_kind,
    )


AGREE_A = "The director's approval decision is what holds everything up."
AGREE_B = "The director's approval decision is the bottleneck holding everything up."
AGREE_C = "The director's approval decision delays everything for days."


class ScorerTest(unittest.TestCase):
    def _topic(self, findings):
        return aggregate(findings, HeuristicRelationChecker()).findings[0]

    def test_corroboration_raises_confidence(self):
        single = self._topic([_pf("A", AGREE_A)])
        trio = self._topic([_pf("A", AGREE_A), _pf("B", AGREE_B), _pf("C", AGREE_C)])
        self.assertLess(score_member(single, 0).value, score_member(trio, 0).value)

    def test_contradiction_lowers_confidence_and_minority_lowest(self):
        topic = self._topic([
            _pf("A", "We follow the official process exactly as we're supposed to.", tier=1),
            _pf("B", "Honestly nobody follows the official process; it isn't what we're supposed to do.", tier=1),
            _pf("C", "In practice nobody follows the official process the way we're officially supposed to.", tier=1),
        ])
        scores = score_topic(topic)
        # A is the lone dissenter against two who agree -> lowest confidence.
        self.assertLess(scores[0].value, scores[1].value)
        self.assertLess(scores[0].value, scores[2].value)
        self.assertIs(scores[0].band, ConfidenceBand.LOW)

    def test_higher_tier_raises_confidence(self):
        low = self._topic([_pf("A", AGREE_A, tier=1)])
        high = self._topic([_pf("A", AGREE_A, tier=4)])
        self.assertLess(score_member(low, 0).value, score_member(high, 0).value)

    def test_flexible_match_lowers_confidence(self):
        exact = self._topic([_pf("A", AGREE_A, match_kind="exact")])
        flexible = self._topic([_pf("A", AGREE_A, match_kind="flexible")])
        self.assertLess(score_member(flexible, 0).value, score_member(exact, 0).value)

    def test_score_is_explainable_and_sums_to_logit(self):
        topic = self._topic([_pf("A", AGREE_A), _pf("B", AGREE_B)])
        score = score_member(topic, 0)
        self.assertGreater(len(score.contributions), 1)
        self.assertAlmostEqual(
            sum(c.logit_delta for c in score.contributions), score.logit, places=9)
        self.assertIn("corroboration", score.explain())

    def test_value_always_a_probability(self):
        topic = self._topic([_pf("A", AGREE_A)])
        v = score_member(topic, 0).value
        self.assertGreater(v, 0.0)
        self.assertLess(v, 1.0)


class CalibrationMathTest(unittest.TestCase):
    def test_perfect_discrimination_gives_auc_one(self):
        outcomes = [
            ScoredOutcome("t1", 0.9, True), ScoredOutcome("t2", 0.8, True),
            ScoredOutcome("f1", 0.2, False), ScoredOutcome("f2", 0.3, False),
        ]
        self.assertEqual(calibrate(outcomes).auc, 1.0)

    def test_inverted_ranking_gives_auc_zero(self):
        outcomes = [
            ScoredOutcome("t1", 0.1, True), ScoredOutcome("f1", 0.9, False),
        ]
        self.assertEqual(calibrate(outcomes).auc, 0.0)

    def test_auc_is_none_with_one_class(self):
        self.assertIsNone(calibrate([ScoredOutcome("t", 0.9, True)]).auc)

    def test_perfectly_calibrated_has_zero_ece(self):
        # Two bins, each with accuracy equal to its confidence.
        outcomes = ([ScoredOutcome("a", 1.0, True)] * 2
                    + [ScoredOutcome("b", 0.0, False)] * 2)
        report = calibrate(outcomes)
        self.assertAlmostEqual(report.ece, 0.0, places=9)
        self.assertAlmostEqual(report.brier, 0.0, places=9)

    def test_brier_penalises_confident_errors(self):
        confident_wrong = calibrate([ScoredOutcome("x", 0.99, False)]).brier
        humble_wrong = calibrate([ScoredOutcome("x", 0.51, False)]).brier
        self.assertGreater(confident_wrong, humble_wrong)

    def test_empty_is_safe(self):
        self.assertEqual(calibrate([]).n, 0)


class ScenarioTest(unittest.TestCase):
    def test_mistaken_ids_are_not_veridical(self):
        for truth_id in MISTAKEN_IDS:
            self.assertFalse(is_veridical(truth_id))
        self.assertTrue(is_veridical("ben_process"))

    def test_org_has_both_true_and_false_beliefs(self):
        truths = [t for p in meridian_org() for t in p.latent_truths]
        self.assertTrue(any(is_veridical(t.id) for t in truths))
        self.assertTrue(any(not is_veridical(t.id) for t in truths))


class StudyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = run_study()

    def test_study_produces_both_classes(self):
        c = self.study.calibration
        self.assertGreater(c.n, 10)
        self.assertGreater(c.n_correct, 0)
        self.assertLess(c.n_correct, c.n)  # some findings really are false

    def test_confidence_discriminates_truth(self):
        c = self.study.calibration
        self.assertIsNotNone(c.auc)
        self.assertGreater(c.auc, 0.5, "confidence must rank truth above falsehood")

    def test_true_findings_score_higher_on_average(self):
        c = self.study.calibration
        self.assertGreater(c.separation, 0.0)

    def test_every_false_finding_is_below_the_true_ones(self):
        # The strong claim the mock scenario supports: no false finding outranks a
        # true one. If this ever breaks, the scorer regressed.
        true_min = min(r.confidence.value for r in self.study.rows if r.correct)
        false_max = max(r.confidence.value for r in self.study.rows if not r.correct)
        self.assertLess(false_max, true_min)


if __name__ == "__main__":
    unittest.main()
