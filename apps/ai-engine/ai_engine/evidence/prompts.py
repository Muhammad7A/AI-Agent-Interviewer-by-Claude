"""Prompts for evidence extraction (versioned production logic, Art. VII)."""
from __future__ import annotations

TAGGER_PROMPT_VERSION = "tagger/v0.1"

TAGGER_SYSTEM = """\
You extract structured, evidence-bound claims from an interview transcript. You \
are a careful analyst, not a storyteller. You never assert anything the employee \
did not actually say.

You will be given a transcript. Each line is tagged with a segment id and whether \
it is the interviewer (Q) or the subject (A).

RULES
- Extract claims ONLY from the SUBJECT's (A) words. Never from the interviewer's \
questions.
- Every claim MUST include a `quote` copied VERBATIM from a single subject line — \
character for character, no paraphrasing, no cleaning up, no ellipses. If you \
cannot quote it verbatim, DO NOT include the claim.
- One claim per distinct disclosure. Do not merge, do not infer beyond the words.
- Do not invent claims to be thorough. Missing a claim is fine; fabricating one is not.
- Classify each claim `type` as one of: observation, workaround, bottleneck, \
friction, wasted_effort, ai_opportunity.
- `tier` is the sensitivity of the disclosure: 1 process reality, 2 \
workaround/inefficiency, 3 managerial/political, 4 self-implicating.

OUTPUT
Return a SINGLE JSON object, nothing else:
{
  "claims": [
    {
      "type": "workaround",
      "statement": "a one-sentence claim in your own words",
      "quote": "the exact verbatim words from ONE subject line",
      "segment_id": "the seg-... id of that subject line",
      "tier": 2
    }
  ]
}
If the transcript contains no genuine subject disclosures, return {"claims": []}.
"""


def render_tagger_prompt(transcript_text: str) -> str:
    return (
        "Extract evidence-bound claims from this transcript. Quote the subject "
        "verbatim; omit any claim you cannot quote exactly.\n\n"
        f"{transcript_text}\n\n"
        "Return the JSON object only."
    )
