"""The privacy firewall (Constitution Article X).

The important tests here are the two hard invariants, asserted over a whole
generated organization rather than a hand-picked example:

  * no real employee name appears anywhere in an employer-facing release, and
  * no verbatim phrase from any employee's testimony appears in one either.

The second matters more than it looks. A verbatim quote is a fingerprint: "I use my
personal ChatGPT to draft the summaries" identifies its author to their own manager
even with the name stripped. Redaction that removes only names is not redaction.
"""
import re
import unittest

from ai_engine.aggregation.aggregator import aggregate
from ai_engine.aggregation.model import ParticipantFinding, participant_finding_from_claim
from ai_engine.aggregation.relation import HeuristicRelationChecker
from ai_engine.evidence.tagger import EvidenceTagger
from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.privacy import (
    Audience,
    Pseudonymizer,
    ReleasePolicy,
    release,
    render_release_report,
)
from ai_engine.privacy.identity import PSEUDONYM_PREFIX, new_engagement_salt
from ai_engine.subjects.simulated import SimulatedInterviewee
from ai_engine.synthetic import OrgSpec, generate_org
from ai_engine.transcript.model import Speaker


def _pf(pid, statement, tier=3, quote=None):
    return ParticipantFinding(
        participant_id=pid, participant_name=pid, claim_type="friction",
        statement=statement, tier=tier, evidence_quote=quote or statement,
        segment_id=f"seg-{pid}", transcript_id=f"txn-{pid}")


class PseudonymizerTest(unittest.TestCase):
    def test_stable_within_an_engagement(self):
        p = Pseudonymizer("salt-a")
        self.assertEqual(p.pseudonym("Dana"), p.pseudonym("Dana"))

    def test_distinct_people_get_distinct_pseudonyms(self):
        p = Pseudonymizer("salt-a")
        self.assertNotEqual(p.pseudonym("Dana"), p.pseudonym("Eli"))

    def test_not_linkable_across_engagements(self):
        # Two clients' datasets must not be joinable on pseudonyms.
        self.assertNotEqual(
            Pseudonymizer("salt-a").pseudonym("Dana"),
            Pseudonymizer("salt-b").pseudonym("Dana"),
        )

    def test_pseudonym_does_not_leak_the_name(self):
        p = Pseudonymizer("salt-a")
        pseudo = p.pseudonym("Dana")
        self.assertTrue(pseudo.startswith(PSEUDONYM_PREFIX))
        self.assertNotIn("dana", pseudo.lower())

    def test_key_maps_back_only_for_the_holder(self):
        p = Pseudonymizer("salt-a")
        pseudo = p.pseudonym("Dana")
        self.assertEqual(p.key[pseudo], "Dana")

    def test_key_file_is_marked_restricted(self, ):
        import json
        import tempfile
        from pathlib import Path

        p = Pseudonymizer("salt-a")
        p.pseudonym("Dana")
        with tempfile.TemporaryDirectory() as tmp:
            path = p.write_key(Path(tmp) / "key.json")
            payload = json.loads(path.read_text())
        self.assertIn("RESTRICTED", payload["warning"])
        self.assertIn("never be shared with the employer", payload["warning"])

    def test_salts_are_unique(self):
        self.assertNotEqual(new_engagement_salt(), new_engagement_salt())


class ReleasePolicyTest(unittest.TestCase):
    def test_employer_policy_is_strict_by_default(self):
        pol = ReleasePolicy.for_employer()
        self.assertIs(pol.audience, Audience.EMPLOYER)
        self.assertTrue(pol.aggregate_only)
        self.assertTrue(pol.suppress_below_k)
        self.assertFalse(pol.reveal_contradiction_sides)
        self.assertGreaterEqual(pol.k_anonymity, 3)

    def test_consultant_policy_is_inside_the_firewall(self):
        pol = ReleasePolicy.for_consultant()
        self.assertFalse(pol.aggregate_only)
        self.assertTrue(pol.reveal_contradiction_sides)

    def test_an_employer_policy_cannot_be_constructed_weakened(self):
        # The employer defaults are a guarantee, not a preference: no caller gets
        # to build an employer-shaped policy with the firewall dialed down.
        weakenings = [
            {"aggregate_only": False},
            {"verbatim_max_tier": 4},
            {"attribute_max_tier": 3},
            {"reveal_contradiction_sides": True},
            {"reveal_per_member_confidence": True},
            {"suppress_below_k": False},
            {"k_anonymity": 1},
        ]
        for kwargs in weakenings:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    ReleasePolicy(audience=Audience.EMPLOYER, **kwargs)

    def test_consultant_policy_may_use_the_full_ladder(self):
        pol = ReleasePolicy.for_consultant()
        self.assertEqual(pol.verbatim_max_tier, 4)


class ReleaseGateTest(unittest.TestCase):
    def _agg(self, findings):
        return aggregate(findings, HeuristicRelationChecker())

    def test_sub_k_topic_is_suppressed_with_a_reason(self):
        agg = self._agg([_pf("P-1", "The director's approval decision delays every job.")])
        pkg = release(agg, policy=ReleasePolicy.for_employer(k_anonymity=3))
        self.assertEqual(pkg.topics, [])
        self.assertEqual(len(pkg.suppressions), 1)
        self.assertIn("k-anonymity", pkg.suppressions[0].reason)

    def test_suppression_does_not_disclose_the_exact_count(self):
        # The employer already knows the topic exists; the ledger must not also
        # tell them how many people had it — a sub-k size narrows the anonymity
        # set the firewall just refused to name.
        agg_one = self._agg([_pf("P-1", "The director's approval decision delays every job.")])
        pkg = release(agg_one, policy=ReleasePolicy.for_employer(k_anonymity=3))
        detail = pkg.suppressions[0].detail
        self.assertNotIn("1 participant", detail)
        self.assertNotIn("one participant", detail.lower())
        self.assertIn("fewer than", detail)
        rendered = render_release_report(pkg, org_name="X", interview_count=1)
        self.assertNotIn("topic(s) were not released", rendered)
        self.assertNotIn("**withheld:** 1", rendered)

    def test_topic_at_threshold_is_released(self):
        agg = self._agg([
            _pf("P-1", "The director's approval decision delays every job here."),
            _pf("P-2", "The director's approval decision delays every job badly."),
        ])
        pkg = release(agg, policy=ReleasePolicy.for_employer(k_anonymity=2))
        self.assertEqual(len(pkg.topics), 1)

    def test_employer_release_is_aggregate_only(self):
        agg = self._agg([
            _pf("P-1", "The director's approval decision delays every job here."),
            _pf("P-2", "The director's approval decision delays every job badly."),
        ])
        pkg = release(agg, policy=ReleasePolicy.for_employer(k_anonymity=2))
        topic = pkg.topics[0]
        self.assertEqual(len(topic.statements), 1, "per-member detail must not survive")
        self.assertIsNone(topic.statements[0].attributed_to)
        self.assertIsNone(topic.statements[0].quote)

    def test_employer_label_is_not_a_participant_verbatim_statement(self):
        # The aggregation's own label is one member's exact words, so it cannot be
        # reused outside the firewall.
        s1 = "The director's approval decision delays every job here."
        agg = self._agg([_pf("P-1", s1), _pf("P-2", s1.replace("here", "badly"))])
        pkg = release(agg, policy=ReleasePolicy.for_employer(k_anonymity=2))
        self.assertNotIn(s1, pkg.topics[0].label)

    def test_contested_sides_are_withheld_from_the_employer(self):
        agg = self._agg([
            _pf("P-1", "We always follow the official written procedure exactly as intended.", tier=1),
            _pf("P-2", "Nobody will follow the official written procedure as intended.", tier=1),
        ])
        pkg = release(agg, policy=ReleasePolicy.for_employer(k_anonymity=2))
        topic = pkg.topics[0]
        self.assertTrue(topic.contested)
        self.assertIsNotNone(topic.contested_note)
        # The dissenting position itself must not appear.
        self.assertNotIn("Nobody will follow", pkg.all_text())

    def test_consultant_release_keeps_attributed_detail(self):
        agg = self._agg([
            _pf("P-1", "The director's approval decision delays every job here."),
            _pf("P-2", "The director's approval decision delays every job badly."),
        ])
        pkg = release(agg, policy=ReleasePolicy.for_consultant())
        self.assertEqual(len(pkg.topics[0].statements), 2)
        self.assertTrue(any(s.attributed_to for s in pkg.topics[0].statements))
        self.assertTrue(any(s.quote for s in pkg.topics[0].statements))

    def test_release_does_not_mutate_the_aggregation(self):
        agg = self._agg([_pf("P-1", "The director's approval decision delays jobs.")])
        before = agg.findings[0].label
        release(agg, policy=ReleasePolicy.for_employer())
        self.assertEqual(agg.findings[0].label, before)


class HardInvariantTest(unittest.TestCase):
    """The two invariants, over a whole generated organization."""

    @classmethod
    def setUpClass(cls):
        org = generate_org(OrgSpec(size=10, seed=31, contradiction_rate=1.0,
                                   bias_rate=0.3, candor_mix=(("guarded", 0.0),
                                                              ("neutral", 0.4),
                                                              ("open", 0.6))))
        cls.real_names = [p.name for p in org.personas]
        pseudo = Pseudonymizer("fixed-test-salt")
        findings = []
        cls.subject_utterances: list[str] = []
        for persona in org.fresh_personas():
            engine = InterviewEngine(llm=None, max_turns=14)
            subject = SimulatedInterviewee(persona, llm=None)
            result = run_interview(engine=engine, subject=subject,
                                   event_log=NullEventLog(), max_turns=14)
            cls.subject_utterances += [
                s.text for s in result.transcript.segments
                if s.speaker is Speaker.SUBJECT and len(s.text.split()) >= 6
            ]
            alias = pseudo.pseudonym(persona.name)
            for claim in EvidenceTagger(llm=None).tag(result.transcript).claims:
                findings.append(participant_finding_from_claim(
                    claim, result.transcript,
                    participant_id=alias, participant_name=alias))
        cls.aggregation = aggregate(findings, HeuristicRelationChecker())
        cls.employer = release(cls.aggregation,
                               policy=ReleasePolicy.for_employer(k_anonymity=2))
        cls.employer_text = (
            cls.employer.all_text() + "\n"
            + render_release_report(cls.employer, org_name="T", interview_count=10)
        )

    def test_employer_release_is_not_empty(self):
        # A firewall that releases nothing proves nothing.
        self.assertGreater(len(self.employer.topics), 0)

    def test_no_real_employee_name_reaches_the_employer(self):
        for name in self.real_names:
            with self.subTest(name=name):
                self.assertIsNone(
                    re.search(rf"\b{re.escape(name)}\b", self.employer_text),
                    f"real name {name!r} leaked into the employer release")

    def test_no_verbatim_testimony_reaches_the_employer(self):
        # Any run of 5+ consecutive words from a real utterance counts as verbatim.
        haystack = " ".join(self.employer_text.lower().split())
        for utterance in self.subject_utterances:
            words = utterance.lower().split()
            for i in range(len(words) - 4):
                phrase = " ".join(words[i : i + 5])
                phrase = re.sub(r"\s+", " ", phrase)
                with self.subTest(phrase=phrase):
                    self.assertNotIn(phrase, haystack,
                                     f"verbatim phrase leaked: {phrase!r}")

    def test_consultant_view_does_keep_the_detail(self):
        # The firewall must not be so blunt that the consultant loses their tool.
        consultant = release(self.aggregation, policy=ReleasePolicy.for_consultant())
        self.assertTrue(any(s.quote for t in consultant.topics for s in t.statements))

    def test_consultant_view_is_still_pseudonymous(self):
        consultant = release(self.aggregation, policy=ReleasePolicy.for_consultant())
        text = consultant.all_text()
        for name in self.real_names:
            with self.subTest(name=name):
                self.assertIsNone(re.search(rf"\b{re.escape(name)}\b", text))


if __name__ == "__main__":
    unittest.main()
