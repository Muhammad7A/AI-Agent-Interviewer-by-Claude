"""The evaluation suite: personas × candor levels, each a case with known truth."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..subjects.simulated import Persona, default_persona, support_lead_persona

# The candor ceiling — the level at which capability gates are judged.
CEILING_CANDOR = "open"


@dataclass
class Case:
    name: str
    persona_factory: Callable[[str], Persona]
    candor: str
    max_turns: int = 14

    @property
    def is_ceiling(self) -> bool:
        return self.candor == CEILING_CANDOR

    def persona(self) -> Persona:
        return self.persona_factory(self.candor)


def default_suite() -> list[Case]:
    """Two personas across the candor sweep (guarded → neutral → open).

    The guarded/neutral cases probe safety and the candor floor; the open cases
    are the ceilings where capability is judged.
    """
    factories: list[tuple[str, Callable[[str], Persona]]] = [
        ("ops-analyst", default_persona),
        ("support-lead", support_lead_persona),
    ]
    cases: list[Case] = []
    for name, factory in factories:
        for candor in ("guarded", "neutral", "open"):
            cases.append(Case(name=f"{name}/{candor}", persona_factory=factory, candor=candor))
    return cases
