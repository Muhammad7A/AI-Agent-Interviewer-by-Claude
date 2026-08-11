"""The generator's inputs (``OrgSpec``) and output (``SyntheticOrg``)."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from ..subjects.simulated import CANDOR_LEVELS, LatentTruth, Persona


@dataclass(frozen=True)
class OrgSpec:
    """Everything controllable about a generated organization."""

    size: int = 12
    seed: int = 0
    name: str = "SynthCo"

    # Proportions over candor levels. Guarded people withhold Tier 2+ truths, so
    # this parameter directly controls how much truth is reachable at all.
    candor_mix: tuple[tuple[str, float], ...] = (
        ("guarded", 0.2), ("neutral", 0.5), ("open", 0.3),
    )

    # How many distinct topics one person can speak to (bounded by slot count).
    topics_per_person: int = 3

    # How many people share a topic — controls corroboration depth. Left as None it
    # is derived from size and topics_per_person, so a bigger org gets deeper
    # corroboration instead of running out of topic capacity and going mute.
    corroboration_range: tuple[int, int] | None = None

    # Fraction of contradiction-capable topics that get a planted disagreement.
    contradiction_rate: float = 0.5

    # Of those contradictions, the fraction where the MINORITY is actually right.
    # This is what stops a vote-counting scorer from acing the benchmark.
    minority_correct_rate: float = 0.25

    # Fraction of participants who also hold an unfounded attribution (always false).
    # Each gets a DISTINCT target, so these stay genuinely single-source.
    bias_rate: float = 0.25

    # Of those bias holders, the fraction who share the SAME false belief — a
    # correlated misconception (rumour, shared blind spot). Turn this up to attack
    # corroboration-based confidence on purpose: independent agreement is only
    # evidence when the errors are independent, and this makes them not be.
    correlated_bias_rate: float = 0.0

    def resolved_corroboration_range(self, topic_count: int) -> tuple[int, int]:
        """The explicit range, or one derived so demand matches topic capacity."""
        if self.corroboration_range is not None:
            lo, hi = self.corroboration_range
            lo, hi = max(1, lo), max(1, hi)
            return (lo, hi) if lo <= hi else (hi, lo)
        topic_count = max(1, topic_count)
        per_topic = max(2, round(self.size * self.topics_per_person / topic_count))
        return max(1, per_topic // 2), per_topic

    def candor_weights(self) -> dict[str, float]:
        weights = {level: 0.0 for level in CANDOR_LEVELS}
        for level, share in self.candor_mix:
            if level in weights:
                weights[level] = max(0.0, share)
        total = sum(weights.values())
        if total <= 0:
            return {"neutral": 1.0, "guarded": 0.0, "open": 0.0}
        return {k: v / total for k, v in weights.items()}


@dataclass(frozen=True)
class PlantedContradiction:
    topic_key: str
    majority: tuple[str, ...]     # participant names on the majority side
    minority: tuple[str, ...]     # participant names on the minority side
    minority_is_correct: bool

    @property
    def correct_side(self) -> tuple[str, ...]:
        return self.minority if self.minority_is_correct else self.majority

    @property
    def wrong_side(self) -> tuple[str, ...]:
        return self.majority if self.minority_is_correct else self.minority


@dataclass
class SyntheticOrg:
    spec: OrgSpec
    personas: list[Persona]
    mistaken_ids: frozenset[str]
    contradictions: list[PlantedContradiction] = field(default_factory=list)
    bias_holders: tuple[str, ...] = ()

    def is_veridical(self, truth_id: str) -> bool:
        return truth_id not in self.mistaken_ids

    def gold_truths(self) -> list[LatentTruth]:
        return [t for p in self.personas for t in p.latent_truths]

    def fresh_personas(self) -> list[Persona]:
        """Deep copies with disclosure state reset, so an org can be re-interviewed."""
        clones = copy.deepcopy(self.personas)
        for persona in clones:
            persona._disclosed = set()
        return clones

    # -- descriptive stats, for the generator's own report card --------------
    @property
    def total_truths(self) -> int:
        return len(self.gold_truths())

    @property
    def total_mistaken(self) -> int:
        return sum(1 for t in self.gold_truths() if t.id in self.mistaken_ids)

    def candor_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for persona in self.personas:
            counts[persona.candor] = counts.get(persona.candor, 0) + 1
        return counts

    def reachable_truths(self) -> int:
        """Truths a persona's candor actually permits them to disclose."""
        from ..subjects.simulated import _CANDOR_TIER_CAP

        return sum(
            1
            for p in self.personas
            for t in p.latent_truths
            if t.tier <= _CANDOR_TIER_CAP.get(p.candor, 3)
        )
