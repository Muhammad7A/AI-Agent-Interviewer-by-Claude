"""Multi-interview aggregation: clustering, corroboration, contradiction typing."""
import unittest

from ai_engine.aggregation.aggregator import aggregate
from ai_engine.aggregation.model import ParticipantFinding, Relation
from ai_engine.aggregation.relation import HeuristicRelationChecker
from ai_engine.aggregation.scenario import northwind_org
from ai_engine.evidence.tagger import EvidenceTagger
from ai_engine.aggregation.model import participant_finding_from_claim
from ai_engine.interview.engine import InterviewEngine
from ai_engine.interview.session import run_interview
from ai_engine.persistence.event_log import NullEventLog
from ai_engine.subjects.simulated import SimulatedInterviewee


def _pf(pid, statement, quote=None, ctype="friction", tier=3):
    return ParticipantFinding(
        participant_id=pid, participant_name=pid, claim_type=ctype,
        statement=statement, tier=tier,
        evidence_quote=quote or statement, segment_id=f"seg-{pid}", transcript_id=f"txn-{pid}",
    )


class RelationTest(unittest.TestCase):
    def setUp(self):
        self.c = HeuristicRelationChecker()

    def test_conflict_on_opposing_polarity(self):
        self.assertIs(
            self.c.classify("We always follow the official process.",
                            "Nobody follows the official process; it's ignored."),
            Relation.CONFLICT)

    def test_agreement_on_same_claim(self):
        self.assertIs(
            self.c.classify("The director's approval is the bottleneck holding up work.",
                            "The director's approval is the bottleneck that stalls work."),
            Relation.AGREE)

    def test_unrelated_when_no_shared_topic(self):
        self.assertIs(
            self.c.classify("The coffee machine is broken.",
                            "The director's approval is slow."),
            Relation.UNRELATED)


class AggregateTest(unittest.TestCase):
    def test_corroboration_and_contradiction_and_single(self):
        findings = [
            # approval bottleneck — three independent people (corroboration)
            _pf("A", "The director's approval is the bottleneck holding up dispatch."),
            _pf("B", "The director's approval is the bottleneck that stalls the work."),
            _pf("C", "The director's approval bottleneck takes days to clear."),
            # process — two people disagree (conflict)
            _pf("A", "We always follow the official process as we're supposed to.", ctype="observation", tier=1),
            _pf("B", "Nobody follows the official process; it's basically ignored.", ctype="observation", tier=1),
            # one unique finding (single-source)
            _pf("C", "I keep a private tracker instead of the official tool.", ctype="workaround", tier=2),
        ]
        result = aggregate(findings, HeuristicRelationChecker())

        corr = result.corroborated
        self.assertEqual(len(corr), 1)
        self.assertEqual(corr[0].participant_count, 3)

        contested = result.contested
        self.assertEqual(len(contested), 1)
        self.assertTrue(contested[0].has_conflict)

        self.assertEqual(len(result.single_source), 1)

    def test_provenance_survives_aggregation(self):
        findings = [
            _pf("A", "The director's approval is the bottleneck holding up dispatch."),
            _pf("B", "The director's approval is the bottleneck that stalls the work."),
        ]
        result = aggregate(findings, HeuristicRelationChecker())
        member = result.findings[0].members[0]
        self.assertTrue(member.transcript_id.startswith("txn-"))
        self.assertTrue(member.segment_id.startswith("seg-"))


class ScenarioIntegrationTest(unittest.TestCase):
    def test_northwind_yields_corroboration_and_a_conflict(self):
        findings = []
        for persona in northwind_org("open"):
            engine = InterviewEngine(llm=None, max_turns=14)
            subject = SimulatedInterviewee(persona, llm=None)
            result = run_interview(engine=engine, subject=subject,
                                   event_log=NullEventLog(), max_turns=14)
            claims = EvidenceTagger(llm=None).tag(result.transcript).claims
            for claim in claims:
                findings.append(participant_finding_from_claim(
                    claim, result.transcript,
                    participant_id=persona.name, participant_name=persona.name))

        result = aggregate(findings, HeuristicRelationChecker())
        # The approval bottleneck is corroborated by all three.
        self.assertTrue(any(f.participant_count == 3 for f in result.corroborated))
        # The process question is contested.
        self.assertGreaterEqual(len(result.contested), 1)
        # Provenance labels are clean (no "[type]" prefix leaked through).
        self.assertFalseIfPrefix(result)

    def assertFalseIfPrefix(self, result):
        for f in result.findings:
            for m in f.members:
                self.assertFalse(m.statement.startswith("["), m.statement)


if __name__ == "__main__":
    unittest.main()
