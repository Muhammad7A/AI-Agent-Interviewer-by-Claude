"""Reading recorded validation decisions back out of the event log.

Validation is written as append-only ``ClaimValidated`` events (the supervised label
the learning loop depends on). The UI needs the *current* verdict per claim, so this
folds the event stream into a read model: last write wins, and the full history stays
on disk.

This is only possible because claim ids are content-addressed
(``evidence.grounding.claim_id_for``). With random ids, re-tagging a transcript in a
new process would mint new ids and silently orphan every verdict the consultant had
recorded.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .event_log import find_log, read_events


@dataclass(frozen=True)
class RecordedVerdict:
    claim_id: str
    verdict: str
    validator_id: str
    validator_kind: str
    reason: str
    decided_at: str
    new_statement: str | None = None

    @property
    def is_human(self) -> bool:
        return self.validator_kind == "consultant"


def validation_path(data_dir: Path | str, interview_id: str) -> Path | None:
    return find_log(Path(data_dir), interview_id, "validation")


def read_verdicts(
    data_dir: Path | str, interview_id: str, cipher=None
) -> dict[str, RecordedVerdict]:
    """Current verdict per claim id, folded from the append-only event log."""
    path = validation_path(data_dir, interview_id)
    verdicts: dict[str, RecordedVerdict] = {}
    if path is None:
        return verdicts
    for record in read_events(path, cipher):
        if record.get("event") != "ClaimValidated":
            continue
        claim_id = record.get("claim_id")
        if not claim_id:
            continue
        correction = record.get("correction") or {}
        verdicts[claim_id] = RecordedVerdict(
            claim_id=claim_id,
            verdict=str(record.get("verdict", "")),
            validator_id=str(record.get("validator_id", "")),
            validator_kind=str(record.get("validator_kind", "")),
            reason=str(record.get("reason", "")),
            decided_at=str(record.get("decided_at", record.get("occurred_at", ""))),
            new_statement=correction.get("new_statement"),
        )
    return verdicts
