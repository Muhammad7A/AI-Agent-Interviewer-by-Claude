"""A small demo organization whose interviews deliberately overlap.

Three employees of "Northwind" who, when interviewed, produce findings that:
  * corroborate on one thing (the director's approval bottleneck — all three), and
  * conflict on another (does anyone follow the official process? — Dana says yes,
    Eli says no),
plus one single-source finding (Fern's private tracker workaround).

The keywords are tuned to the mock interviewer's question ladder so the truths get
elicited offline; a live model would elicit them from natural questioning.
"""
from __future__ import annotations

from ..subjects.simulated import LatentTruth, Persona


def northwind_org(candor: str = "open") -> list[Persona]:
    dana = Persona(
        name="Dana",
        role="Dispatcher",
        candor=candor,
        background="Runs the dispatch desk. Loyal, by-the-book.",
        latent_truths=[
            LatentTruth("dana_process", 1, ["process_reality"], ["supposed", "officially"],
                        "We follow the official process exactly as we're supposed to — it works."),
            LatentTruth("dana_approval", 3, ["friction"], ["decision", "made"],
                        "The director's approval is the bottleneck — a slow decision holding up dispatch."),
        ],
    )
    eli = Persona(
        name="Eli",
        role="Operations Analyst",
        candor=candor,
        background="Analyst who sees the whole flow. Blunt.",
        latent_truths=[
            LatentTruth("eli_process", 1, ["process_reality"], ["supposed", "officially"],
                        "Honestly nobody follows the official process; it's basically ignored."),
            LatentTruth("eli_approval", 2, ["bottlenecks"], ["stall", "waiting"],
                        "Everything waits on the director's approval — that approval bottleneck stalls the work."),
        ],
    )
    fern = Persona(
        name="Fern",
        role="Coordinator",
        candor=candor,
        background="Coordinates between teams. Pragmatic.",
        latent_truths=[
            LatentTruth("fern_approval", 3, ["friction"], ["decision", "made"],
                        "The director's approval is the real bottleneck; that decision takes days."),
            LatentTruth("fern_workaround", 2, ["workarounds"], ["instead", "workarounds"],
                        "I keep a private tracker instead of the official tool because it's unusable."),
        ],
    )
    return [dana, eli, fern]
