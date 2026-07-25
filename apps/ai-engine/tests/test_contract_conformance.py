"""Cross-language conformance: the Python runtime vs the ratified TypeScript contracts.

The repository holds two models of the same domain. ``packages/contracts`` and
``apps/core-api`` are the *ratified design* (ADRs 0001-0008) and are contracts only —
they have never executed. ``apps/ai-engine/ai_engine`` is the *working product*. They
share no code, and until this test existed they were kept in step by hand, by comment.

That is a semantic duplication (Constitution Art. XV: one concept, one name, one
home) and it drifted in a way that mattered: the Python ``EvidenceRef`` had dropped
``transcriptId``, so a reference could not resolve itself and, after multi-interview
aggregation, could be resolved against the wrong person's transcript.

This test makes drift a build failure. Both directions are checked:

  * a Python field with no counterpart in the contract means the runtime invented a
    concept the design does not know about;
  * a required contract field missing from Python must be a **recorded** omission
    with a stated reason, not an accident.

The thin slice is legitimately allowed to implement less than the ratified design.
The point is that every difference is declared.
"""
from __future__ import annotations

import dataclasses
import re
import unittest
from pathlib import Path

from ai_engine.evidence.model import GroundedEvidence  # noqa: F401  (import sanity)
from ai_engine.transcript.model import EvidenceRef, Transcript, TranscriptSegment

REPO = Path(__file__).resolve().parents[3]
CONTRACTS = REPO / "packages" / "contracts" / "src"
CORE_API = REPO / "apps" / "core-api" / "src"


def _camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def parse_ts_interface(path: Path, name: str) -> dict[str, bool]:
    """Return {snake_case_field: is_optional} for one exported TS interface."""
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"export interface {name}(?:<[^>]*>)?\s*\{{(.*?)\n\}}",
                      source, re.DOTALL)
    if not match:
        raise AssertionError(f"interface {name} not found in {path}")
    fields: dict[str, bool] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        field = re.match(r"(?:readonly\s+)?([A-Za-z_][A-Za-z0-9_]*)(\?)?\s*:", line)
        if field:
            fields[_camel_to_snake(field.group(1))] = bool(field.group(2))
    return fields


def python_fields(cls) -> set[str]:
    return {f.name for f in dataclasses.fields(cls) if not f.name.startswith("_")}


# --- declared, deliberate differences --------------------------------------
# Every entry is a decision with a reason, reviewed here rather than discovered
# later as a bug. Removing an entry should make the test fail.

OMITTED_FROM_PYTHON: dict[str, dict[str, str]] = {
    "TranscriptSegment": {
        "speaker_id": "the thin slice has no Speaker entity; it stores the Speaker "
                      "value directly as `speaker` (see EXTRA_IN_PYTHON)",
        "time_range": "optional in the contract; audio/timecode ingest is not built",
        "introduced_in_version": "transcript versioning is not implemented in the "
                                 "thin slice; transcripts are append-only then final",
    },
    "EvidenceRef": {
        "anchor_type": "only one anchor type exists (TranscriptRef), so the "
                       "discriminant is deferred until a second one appears "
                       "(product before platform, C11)",
        "span": "flattened to `start`/`end` rather than a CharSpan value object",
        "speaker": "derivable from the resolved segment; not denormalised onto the ref",
        "uttered_at": "derivable from the resolved segment; not denormalised onto the ref",
    },
}

EXTRA_IN_PYTHON: dict[str, dict[str, str]] = {
    "TranscriptSegment": {
        "speaker": "holds the Speaker value in place of the contract's `speakerId` "
                   "reference, since there is no Speaker entity to reference",
    },
    "EvidenceRef": {
        "start": "the CharSpan's lower bound, flattened",
        "end": "the CharSpan's upper bound, flattened",
    },
}


class ContractConformanceTest(unittest.TestCase):
    """Each Python model must conform to its ratified contract, or declare why not."""

    CASES = (
        ("TranscriptSegment", TranscriptSegment,
         CORE_API / "modules/transcript/domain/entities/transcript-segment.ts"),
        ("EvidenceRef", EvidenceRef,
         CONTRACTS / "provenance/evidence-ref.ts"),
    )

    def test_contract_files_are_present(self):
        for name, _cls, path in self.CASES:
            with self.subTest(contract=name):
                self.assertTrue(path.exists(), f"ratified contract missing: {path}")

    def test_no_python_field_is_unknown_to_the_contract(self):
        # A field the design has never heard of means the runtime invented a concept.
        for name, cls, path in self.CASES:
            ts = parse_ts_interface(path, name)
            declared = EXTRA_IN_PYTHON.get(name, {})
            for field in sorted(python_fields(cls)):
                with self.subTest(contract=name, field=field):
                    self.assertTrue(
                        field in ts or field in declared,
                        f"{name}.{field} exists in Python but not in the contract, "
                        f"and is not declared in EXTRA_IN_PYTHON")

    def test_every_required_contract_field_is_present_or_recorded(self):
        for name, cls, path in self.CASES:
            ts = parse_ts_interface(path, name)
            have = python_fields(cls)
            omitted = OMITTED_FROM_PYTHON.get(name, {})
            for field, optional in sorted(ts.items()):
                if optional:
                    continue
                with self.subTest(contract=name, field=field):
                    self.assertTrue(
                        field in have or field in omitted,
                        f"{name}.{field} is required by the contract, absent from "
                        f"Python, and not recorded in OMITTED_FROM_PYTHON")

    def test_declared_differences_are_actually_differences(self):
        # Keeps the allowlists honest: a stale entry (now implemented, or no longer
        # in the contract) must be removed rather than left as noise.
        for name, cls, path in self.CASES:
            ts = parse_ts_interface(path, name)
            have = python_fields(cls)
            for field in OMITTED_FROM_PYTHON.get(name, {}):
                with self.subTest(contract=name, omitted=field):
                    self.assertIn(field, ts, "stale entry: not in the contract")
                    self.assertNotIn(field, have, "stale entry: now implemented")
            for field in EXTRA_IN_PYTHON.get(name, {}):
                with self.subTest(contract=name, extra=field):
                    self.assertIn(field, have, "stale entry: not in Python")

    def test_every_declared_difference_states_a_reason(self):
        for table in (OMITTED_FROM_PYTHON, EXTRA_IN_PYTHON):
            for name, entries in table.items():
                for field, reason in entries.items():
                    with self.subTest(contract=name, field=field):
                        self.assertGreater(len(reason.strip()), 20,
                                           "a declared difference needs a real reason")


class EvidenceRefSelfResolutionTest(unittest.TestCase):
    """The drift this test was built to catch, pinned as behaviour."""

    def _transcript(self, line: str) -> Transcript:
        from ai_engine.transcript.model import Speaker

        t = Transcript()
        t.append(Speaker.INTERVIEWER, "How does the work get done?")
        t.append(Speaker.SUBJECT, line)
        t.finalize()
        return t

    def test_refs_carry_their_transcript(self):
        from ai_engine.evidence.grounding import ground_proposal
        from ai_engine.evidence.model import RawProposal

        t = self._transcript("I keep a private spreadsheet for the weekly numbers.")
        claim, reason = ground_proposal(
            RawProposal("workaround", "x", quote="private spreadsheet", tier=2), t)
        self.assertEqual(reason, "grounded")
        self.assertEqual(claim.evidence[0].ref.transcript_id, t.id)

    def test_resolving_against_the_wrong_transcript_is_refused(self):
        # Before this, the same segment id in another interview would have resolved
        # happily and produced someone else's words as evidence.
        a = self._transcript("I keep a private spreadsheet for the weekly numbers.")
        b = self._transcript("Escalations stall and pile up waiting on engineering.")
        ref = EvidenceRef(segment_id=a.segments[1].id, start=0, end=6,
                          transcript_id=a.id)
        self.assertEqual(ref.resolve(a), a.segments[1].text[:6])
        with self.assertRaises(ValueError):
            ref.resolve(b)


if __name__ == "__main__":
    unittest.main()
