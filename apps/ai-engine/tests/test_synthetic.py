"""The synthetic organization generator (research program Q16 infrastructure).

The most important tests here are the *vocabulary contract* ones. A generated org is
worthless if its text doesn't flow through the real downstream mechanisms — and
those failures are silent: a planted contradiction that the relation checker never
detects, or two unrelated topics that accidentally merge, would make the benchmark
measure nothing while still reporting a number.
"""
import unittest

from ai_engine.aggregation.aggregator import _cluster
from ai_engine.aggregation.model import Relation
from ai_engine.aggregation.relation import HeuristicRelationChecker, content_words, overlap_coefficient
from ai_engine.synthetic import OrgSpec, generate_org
from ai_engine.synthetic.topics import BIAS_CORES, TOPIC_TEMPLATES


class VocabularyContractTest(unittest.TestCase):
    """Generated text must behave correctly in clustering and relation detection."""

    def setUp(self):
        self.checker = HeuristicRelationChecker()

    def test_every_planted_contradiction_is_actually_detected(self):
        # A planted contradiction the checker cannot see is a benchmark that
        # measures nothing. This caught a real bug: cores without a polarity cue.
        for t in TOPIC_TEMPLATES:
            if not t.can_contradict:
                continue
            affirm = t.statement(t.variants[0], deny=False)
            deny = t.statement(t.variants[1], deny=True)
            with self.subTest(topic=t.key):
                self.assertIs(self.checker.classify(affirm, deny), Relation.CONFLICT)

    def test_two_holders_of_one_topic_register_agreement(self):
        for t in TOPIC_TEMPLATES:
            a = t.statement(t.variants[0], deny=False)
            b = t.statement(t.variants[1], deny=False)
            with self.subTest(topic=t.key):
                self.assertIs(self.checker.classify(a, b), Relation.AGREE)

    def test_distinct_topics_do_not_cluster_together(self):
        # If two different topics merge, corroboration is fabricated out of nothing.
        templates = list(TOPIC_TEMPLATES)
        for i in range(len(templates)):
            for j in range(i + 1, len(templates)):
                a = templates[i].statement(templates[i].variants[0])
                b = templates[j].statement(templates[j].variants[0])
                wa, wb = content_words(a), content_words(b)
                shared = wa & wb
                clusters = len(shared) >= 2 and overlap_coefficient(wa, wb) >= 0.34
                with self.subTest(a=templates[i].key, b=templates[j].key):
                    self.assertFalse(clusters, f"{templates[i].key} merged with {templates[j].key}")

    def test_distinct_bias_cores_do_not_cluster(self):
        # The bug this testbed found: shared bias cores made independent
        # bias-holders corroborate each other into a high-confidence falsehood.
        for i in range(len(BIAS_CORES)):
            for j in range(i + 1, len(BIAS_CORES)):
                wa, wb = content_words(BIAS_CORES[i]), content_words(BIAS_CORES[j])
                clusters = len(wa & wb) >= 2 and overlap_coefficient(wa, wb) >= 0.34
                with self.subTest(i=i, j=j):
                    self.assertFalse(clusters)

    def test_topics_actually_cluster_when_they_should(self):
        # Sanity: the clustering machinery does group same-topic statements.
        t = TOPIC_TEMPLATES[0]
        from ai_engine.aggregation.model import ParticipantFinding

        def pf(pid, text):
            return ParticipantFinding(
                participant_id=pid, participant_name=pid, claim_type="friction",
                statement=text, tier=2, evidence_quote=text,
                segment_id=f"seg-{pid}", transcript_id=f"txn-{pid}")

        findings = [pf("A", t.statement(t.variants[0])), pf("B", t.statement(t.variants[1]))]
        self.assertEqual(len(_cluster(findings)), 1)


class DeterminismTest(unittest.TestCase):
    def test_same_seed_is_identical(self):
        a = generate_org(OrgSpec(size=10, seed=11))
        b = generate_org(OrgSpec(size=10, seed=11))
        self.assertEqual([t.statement for t in a.gold_truths()],
                         [t.statement for t in b.gold_truths()])
        self.assertEqual(a.mistaken_ids, b.mistaken_ids)

    def test_different_seed_differs(self):
        a = generate_org(OrgSpec(size=10, seed=11))
        b = generate_org(OrgSpec(size=10, seed=12))
        self.assertNotEqual([t.statement for t in a.gold_truths()],
                            [t.statement for t in b.gold_truths()])


class SpecControlTest(unittest.TestCase):
    def test_size_is_honoured_and_nobody_is_mute(self):
        for size in (4, 12, 25):
            org = generate_org(OrgSpec(size=size, seed=2))
            with self.subTest(size=size):
                self.assertEqual(len(org.personas), size)
                for p in org.personas:
                    self.assertGreater(len(p.latent_truths), 0)

    def test_candor_mix_is_respected(self):
        org = generate_org(OrgSpec(size=20, seed=4,
                                   candor_mix=(("guarded", 0.0), ("neutral", 0.0), ("open", 1.0))))
        self.assertEqual(set(org.candor_counts()), {"open"})

    def test_guarded_employees_withhold_sensitive_truths(self):
        org = generate_org(OrgSpec(size=20, seed=4,
                                   candor_mix=(("guarded", 1.0), ("neutral", 0.0), ("open", 0.0))))
        # Guarded caps at tier 1, so most planted beliefs are unreachable.
        self.assertLess(org.reachable_truths(), org.total_truths)

    def test_zero_contradiction_rate_plants_none(self):
        org = generate_org(OrgSpec(size=15, seed=6, contradiction_rate=0.0))
        self.assertEqual(org.contradictions, [])

    def test_full_contradiction_rate_plants_many(self):
        org = generate_org(OrgSpec(size=20, seed=6, contradiction_rate=1.0))
        self.assertGreater(len(org.contradictions), 1)
        for c in org.contradictions:
            self.assertGreaterEqual(len(c.majority), 1)
            self.assertEqual(len(c.minority), 1)

    def test_minority_correct_makes_the_majority_wrong(self):
        org = generate_org(OrgSpec(size=20, seed=6, contradiction_rate=1.0,
                                   minority_correct_rate=1.0))
        self.assertTrue(org.contradictions)
        for c in org.contradictions:
            self.assertTrue(c.minority_is_correct)
            self.assertEqual(c.wrong_side, c.majority)
        # Every majority holder on those topics is marked mistaken.
        self.assertGreater(org.total_mistaken, 0)

    def test_zero_bias_rate_plants_none(self):
        org = generate_org(OrgSpec(size=12, seed=8, bias_rate=0.0))
        self.assertEqual(org.bias_holders, ())

    def test_bias_is_single_source_by_default(self):
        org = generate_org(OrgSpec(size=20, seed=9, bias_rate=0.5,
                                   correlated_bias_rate=0.0))
        blame = [t.statement for t in org.gold_truths() if "_blame_" in t.id]
        self.assertGreater(len(blame), 1)
        # Strip the prefix; the cores must differ so they cannot corroborate.
        cores = {s.split(", ", 1)[-1] for s in blame}
        self.assertEqual(len(cores), len(blame))

    def test_correlated_bias_shares_one_belief(self):
        org = generate_org(OrgSpec(size=20, seed=9, bias_rate=0.5,
                                   correlated_bias_rate=1.0))
        blame = [t.statement for t in org.gold_truths() if "_blame_" in t.id]
        cores = {s.split(", ", 1)[-1] for s in blame}
        self.assertEqual(len(cores), 1, "correlated bias should share one core")

    def test_ground_truth_is_known_and_mixed(self):
        org = generate_org(OrgSpec(size=16, seed=13, contradiction_rate=1.0))
        self.assertGreater(org.total_truths, 0)
        self.assertGreater(org.total_mistaken, 0)
        self.assertLess(org.total_mistaken, org.total_truths)

    def test_fresh_personas_resets_disclosure_state(self):
        org = generate_org(OrgSpec(size=5, seed=14))
        org.personas[0]._disclosed.add("x")
        self.assertEqual(org.fresh_personas()[0]._disclosed, set())


class PipelineIntegrationTest(unittest.TestCase):
    """Two regimes, asserted separately.

    The generator exists to find the edge of the confidence scorer, and it does: the
    corroboration signal is only valid while the majority is usually right. These
    tests pin BOTH the working regime and the documented failure, so neither can
    regress silently.
    """

    def _study(self, **overrides):
        from ai_engine.confidence.study import run_study, synthetic_study_org

        spec = OrgSpec(size=14, seed=21, contradiction_rate=1.0, bias_rate=0.3,
                       **overrides)
        return run_study(org=synthetic_study_org(spec)).calibration

    def test_generated_org_yields_a_measurable_study(self):
        c = self._study(minority_correct_rate=0.0)
        # Enough findings to be worth measuring, with both classes present.
        self.assertGreater(c.n, 10)
        self.assertGreater(c.n_correct, 0)
        self.assertLess(c.n_correct, c.n)

    def test_benign_regime_confidence_ranks_truth_above_falsehood(self):
        c = self._study(minority_correct_rate=0.0)
        self.assertIsNotNone(c.auc)
        self.assertGreater(c.auc, 0.5)
        self.assertGreater(c.separation, 0.0)

    def test_wrong_majority_inverts_corroboration_confidence(self):
        # THE finding this testbed was built to expose. When the majority is wrong,
        # a corroboration-weighted score is confidently wrong — AUC falls below
        # chance. Documented limitation, not a bug: independent agreement is only
        # evidence when the errors are independent.
        benign = self._study(minority_correct_rate=0.0)
        adversarial = self._study(minority_correct_rate=1.0)
        self.assertLess(adversarial.auc, benign.auc)
        self.assertLess(adversarial.auc, 0.5)

    def test_correlated_bias_also_degrades_confidence(self):
        # A shared misconception corroborates itself. Same failure mode, different
        # cause — and the generator can express it on purpose.
        independent = self._study(minority_correct_rate=0.0, correlated_bias_rate=0.0)
        correlated = self._study(minority_correct_rate=0.0, correlated_bias_rate=1.0)
        self.assertLessEqual(correlated.auc, independent.auc)


if __name__ == "__main__":
    unittest.main()
