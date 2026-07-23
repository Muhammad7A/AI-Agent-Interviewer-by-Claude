"""Transcript immutability + evidence resolution — the provenance guarantee."""
import unittest

from ai_engine.transcript.model import (
    EvidenceRef,
    Speaker,
    Transcript,
    TranscriptFinalizedError,
)


class TranscriptTest(unittest.TestCase):
    def test_segments_are_appended_in_sequence(self):
        t = Transcript()
        s0 = t.append(Speaker.INTERVIEWER, "How does the work get done?")
        s1 = t.append(Speaker.SUBJECT, "I keep a private spreadsheet.")
        self.assertEqual(s0.sequence, 0)
        self.assertEqual(s1.sequence, 1)
        self.assertEqual(len(t.segments), 2)

    def test_finalize_forbids_further_append(self):
        t = Transcript()
        t.append(Speaker.INTERVIEWER, "Hi")
        t.finalize()
        with self.assertRaises(TranscriptFinalizedError):
            t.append(Speaker.SUBJECT, "should fail")

    def test_evidence_ref_resolves_to_exact_span(self):
        t = Transcript()
        seg = t.append(Speaker.SUBJECT, "I keep a private spreadsheet because the dashboard is unusable.")
        # Resolve the span for "private spreadsheet".
        start = seg.text.index("private spreadsheet")
        ref = EvidenceRef(segment_id=seg.id, start=start, end=start + len("private spreadsheet"))
        self.assertEqual(ref.resolve(t), "private spreadsheet")

    def test_out_of_bounds_span_raises(self):
        t = Transcript()
        seg = t.append(Speaker.SUBJECT, "short")
        with self.assertRaises(ValueError):
            seg.span_text(0, 999)


if __name__ == "__main__":
    unittest.main()
