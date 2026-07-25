"""An explainable confidence score."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConfidenceBand(str, Enum):
    LOW = "low"        # treat as a lead, not a finding
    MEDIUM = "medium"  # worth acting on with corroboration
    HIGH = "high"      # decision-grade, subject to human validation

    @classmethod
    def of(cls, value: float) -> "ConfidenceBand":
        if value >= 0.75:
            return cls.HIGH
        if value >= 0.50:
            return cls.MEDIUM
        return cls.LOW


@dataclass(frozen=True)
class SignalContribution:
    """One named, observable signal and what it added in log-odds."""

    name: str
    detail: str
    logit_delta: float


@dataclass(frozen=True)
class ConfidenceScore:
    value: float                     # probability in [0, 1]
    logit: float
    contributions: tuple[SignalContribution, ...] = field(default_factory=tuple)

    @property
    def band(self) -> ConfidenceBand:
        return ConfidenceBand.of(self.value)

    def explain(self) -> str:
        """Human-readable breakdown — 'why do you believe this at 0.84?'"""
        lines = [f"confidence {self.value:.2f} ({self.band.value})"]
        for c in self.contributions:
            sign = "+" if c.logit_delta >= 0 else "−"
            lines.append(f"  {sign}{abs(c.logit_delta):.2f}  {c.name}: {c.detail}")
        return "\n".join(lines)
