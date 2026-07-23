"""Interviewees: a real human at a terminal, or a simulated persona."""

from .base import Interviewee
from .human import HumanInterviewee
from .simulated import (
    LatentTruth,
    Persona,
    SimulatedInterviewee,
    default_persona,
    support_lead_persona,
)

__all__ = [
    "HumanInterviewee",
    "Interviewee",
    "LatentTruth",
    "Persona",
    "SimulatedInterviewee",
    "default_persona",
    "support_lead_persona",
]
