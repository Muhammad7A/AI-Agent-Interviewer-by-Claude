"""Dataset framework: versioned scenario files the lab runs against.

A dataset is a JSON document with an explicit schema, a version, and a list of
:class:`~ai_engine.lab.schemas.Scenario` records. Datasets are data, not code:
curating a new case means editing JSON, and the loader refuses malformed
records instead of skipping them — a silently-dropped scenario is a hole in
the measurement.
"""
from __future__ import annotations

import json
from pathlib import Path

from .schemas import Scenario

DATASET_SCHEMA = "groundwork.lab.dataset/v1"

#: Scenario kinds. `golden` cases are the curated regression set; `edge` and
#: `adversarial` cases document hostile behavior; `standard` is the bulk.
KINDS = ("golden", "standard", "edge", "adversarial")


def load_dataset(path: Path) -> tuple[str, list[Scenario]]:
    """Load and validate a dataset file. Refuses malformed records loudly."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != DATASET_SCHEMA:
        raise ValueError(
            f"{path.name}: unsupported dataset schema {data.get('schema')!r} "
            f"(expected {DATASET_SCHEMA!r})")
    scenarios: list[Scenario] = []
    seen: set[str] = set()
    for i, record in enumerate(data.get("scenarios", [])):
        try:
            scenario = Scenario.from_dict(record)
        except Exception as exc:
            raise ValueError(
                f"{path.name}: scenario #{i} is malformed: {exc}") from exc
        if scenario.kind not in KINDS:
            raise ValueError(
                f"{path.name}: scenario {scenario.id!r} has unknown kind "
                f"{scenario.kind!r}")
        if scenario.id in seen:
            raise ValueError(f"{path.name}: duplicate scenario id {scenario.id!r}")
        seen.add(scenario.id)
        scenarios.append(scenario)
    return data.get("version", "0"), scenarios


def load_golden() -> tuple[str, list[Scenario]]:
    """The regression-gated scenarios: every `golden` record in the shipped
    dataset. Non-golden records in the same file (edge/adversarial cases with
    documented known-gaps) are measurable via run_suite but never gate CI —
    a known-gap must not fail the build, it must be VISIBLE."""
    _version, scenarios = load_dataset(Path(__file__).parent / "datasets" / "golden.json")
    return _version, [s for s in scenarios if s.kind == "golden"]
