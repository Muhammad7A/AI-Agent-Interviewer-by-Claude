"""Build a reproducible corpus of real transcripts and quotable spans.

Quotes are drawn from *real* interview transcripts produced by the synthetic
generator, so the audit stresses the gates with the kind of text they actually see
rather than with lorem ipsum.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from ..interview.engine import InterviewEngine
from ..interview.session import run_interview
from ..lexicon import quantities
from ..persistence.event_log import NullEventLog
from ..subjects.simulated import SimulatedInterviewee
from ..synthetic import OrgSpec, generate_org
from ..transcript.model import Speaker, Transcript


@dataclass(frozen=True)
class QuoteSpan:
    transcript: Transcript
    segment_id: str
    text: str          # an exact substring of the segment
    segment_text: str


def build_transcripts(*, org_size: int = 6, seed: int = 0) -> list[Transcript]:
    org = generate_org(OrgSpec(size=org_size, seed=seed, candor_mix=(
        ("guarded", 0.0), ("neutral", 0.4), ("open", 0.6))))
    transcripts: list[Transcript] = []
    for persona in org.fresh_personas():
        engine = InterviewEngine(llm=None, max_turns=14)
        subject = SimulatedInterviewee(persona, llm=None)
        result = run_interview(engine=engine, subject=subject,
                               event_log=NullEventLog(), max_turns=14)
        transcripts.append(result.transcript)
    return transcripts


def collect_spans(
    transcripts: list[Transcript], rng: random.Random, *, per_segment: int = 3
) -> list[QuoteSpan]:
    """Exact substrings of subject utterances, spanning 2..8 whole words."""
    spans: list[QuoteSpan] = []
    for transcript in transcripts:
        for segment in transcript.segments:
            if segment.speaker is not Speaker.SUBJECT:
                continue
            words = segment.text.split(" ")
            if len(words) < 3:
                continue
            for _ in range(per_segment):
                length = rng.randint(2, min(8, len(words)))
                start = rng.randint(0, len(words) - length)
                text = " ".join(words[start : start + length])
                if not text.strip():
                    continue
                # Guarantee it really is an exact substring before we assert anything.
                if text not in segment.text:
                    continue
                spans.append(QuoteSpan(
                    transcript=transcript,
                    segment_id=segment.id,
                    text=text,
                    segment_text=segment.text,
                ))
            spans.extend(QuoteSpan(
                transcript=transcript,
                segment_id=segment.id,
                text=figure_span,
                segment_text=segment.text,
            ) for figure_span in _spans_around_figures(words, segment.text))
    return spans


def _spans_around_figures(words: list[str], segment_text: str) -> list[str]:
    """A window around EVERY stated figure in ``words``, not just the first.

    Sampling alone could not be relied on to produce a figure at all. Three random
    2–8 word windows per segment will usually miss a figure sitting at the end of a
    long sentence, so the quantity property recorded zero runs and reported as
    healthy — a property that never executes is worse than a missing one, because
    the report reads as coverage. One guaranteed window per figure keeps the
    quantity property honest even as shuffle and subsampling dilute the rest.
    """
    spans: list[str] = []
    for i, word in enumerate(words):
        if not quantities(word):
            continue
        start = max(0, i - 2)
        text = " ".join(words[start : i + 3])
        if text.strip() and text in segment_text and text not in spans:
            spans.append(text)
    return spans


def interviewer_spans(transcripts: list[Transcript], rng: random.Random) -> list[QuoteSpan]:
    """Spans that appear ONLY in interviewer turns — never valid evidence (F8)."""
    spans: list[QuoteSpan] = []
    for transcript in transcripts:
        subject_text = " ".join(
            s.text.lower() for s in transcript.segments if s.speaker is Speaker.SUBJECT
        )
        for segment in transcript.segments:
            if segment.speaker is not Speaker.INTERVIEWER:
                continue
            words = segment.text.split(" ")
            if len(words) < 5:
                continue
            length = rng.randint(4, min(9, len(words)))
            start = rng.randint(0, len(words) - length)
            text = " ".join(words[start : start + length])
            if text.lower() in subject_text:
                continue  # the subject echoed it; not exclusively the interviewer's
            spans.append(QuoteSpan(
                transcript=transcript,
                segment_id=segment.id,
                text=text,
                segment_text=segment.text,
            ))
    return spans
