"""A calibration study organization: six employees, some of them wrong.

Calibration needs both positives and negatives. A scenario where everyone is
right is useless — confidence would have nothing to discriminate. So this org
contains **mistaken beliefs**: things a participant sincerely asserts that are not
actually true of the organization.

  * ``VERIDICAL`` truths are actually true of Meridian.
  * ``MISTAKEN`` beliefs are sincerely held and will be reported as findings, but
    are false — either a minority view contradicted by better-informed colleagues
    (Ana on process) or an unfounded attribution of blame (Dev, Eve).

This gives the calibration study a labelled outcome per finding without any
hand-waving: a finding is correct iff it maps to a VERIDICAL truth.

Keywords are tuned to the offline interviewer's question ladder so every truth is
actually elicited in mock mode; a live model would reach them by natural probing.
"""
from __future__ import annotations

from ..subjects.simulated import LatentTruth, Persona

# Truth ids that are sincerely believed but FALSE of the organization.
MISTAKEN_IDS: frozenset[str] = frozenset({
    "ana_process_mistaken",
    "dev_blame_mistaken",
    "eve_blame_mistaken",
})


def is_veridical(truth_id: str) -> bool:
    return truth_id not in MISTAKEN_IDS


# --- shared question-ladder slots -----------------------------------------
_SLOT_APPROVAL = ["decision", "made"]           # "...or a decision someone made?"
_SLOT_PROCESS = ["supposed", "officially"]      # "...how it's officially supposed to work?"
_SLOT_REWORK = ["redundant", "redone"]          # "...felt redundant or got redone?"
_SLOT_QUEUE = ["stall", "pile"]                 # "...stall or pile up waiting?"
_SLOT_TOOL = ["instead", "workarounds"]         # "...do instead — any workarounds?"
_SLOT_REPEAT = ["repetitive", "rules-based"]    # "...most repetitive or rules-based?"
_SLOT_HONEST = ["honest", "differently"]        # "...your own honest version?"


def meridian_org(candor: str = "open") -> list[Persona]:
    """Six employees of Meridian Logistics. 18 findings, 3 of them false."""
    ana = Persona(
        name="Ana", role="Dispatcher", candor=candor,
        background="Runs the dispatch desk. Loyal and by-the-book — and therefore "
                   "wrong about how closely others follow the process.",
        latent_truths=[
            LatentTruth("ana_approval", 3, ["friction"], _SLOT_APPROVAL,
                        "The director's approval decision is what holds everything up."),
            # MISTAKEN: contradicted by two better-placed colleagues.
            LatentTruth("ana_process_mistaken", 1, ["process_reality"], _SLOT_PROCESS,
                        "We follow the official process exactly as we're supposed to."),
            LatentTruth("ana_queue", 2, ["bottlenecks"], _SLOT_QUEUE,
                        "Jobs stall and pile up waiting on the paperwork."),
        ],
    )
    ben = Persona(
        name="Ben", role="Operations Analyst", candor=candor,
        background="Sees the whole flow end to end. Blunt and well-informed.",
        latent_truths=[
            LatentTruth("ben_approval", 3, ["friction"], _SLOT_APPROVAL,
                        "The director's approval decision is the bottleneck that stalls everything."),
            LatentTruth("ben_process", 1, ["process_reality"], _SLOT_PROCESS,
                        "Honestly nobody follows the official process; it isn't what we're supposed to do."),
            LatentTruth("ben_rework", 2, ["wasted_effort"], _SLOT_REWORK,
                        "The weekly reconciliation is redundant work that gets redone every week."),
        ],
    )
    cleo = Persona(
        name="Cleo", role="Coordinator", candor=candor,
        background="Coordinates between teams. Pragmatic.",
        latent_truths=[
            LatentTruth("cleo_approval", 3, ["friction"], _SLOT_APPROVAL,
                        "The director's approval decision delays everything for days."),
            LatentTruth("cleo_tool", 2, ["workarounds"], _SLOT_TOOL,
                        "I keep a private tracker instead of the official tool because it is unusable."),
            LatentTruth("cleo_repeat", 2, ["ai_opportunity"], _SLOT_REPEAT,
                        "Most of my week is repetitive rules-based copying between systems."),
        ],
    )
    dev = Persona(
        name="Dev", role="Support Lead", candor=candor,
        background="Leads the support queue. Protective of his team, quick to blame others.",
        latent_truths=[
            LatentTruth("dev_rework", 2, ["wasted_effort"], _SLOT_REWORK,
                        "The customer summaries are redundant work that gets redone every week."),
            LatentTruth("dev_queue", 2, ["bottlenecks"], _SLOT_QUEUE,
                        "Escalations stall and pile up waiting on engineering."),
            # MISTAKEN: an unfounded attribution, uncorroborated by anyone.
            LatentTruth("dev_blame_mistaken", 1, ["friction"], _SLOT_HONEST,
                        "Honestly I work differently because the night shift does not care."),
        ],
    )
    eve = Persona(
        name="Eve", role="Planner", candor=candor,
        background="Plans capacity. Capable but cynical about leadership.",
        latent_truths=[
            LatentTruth("eve_tool", 2, ["workarounds"], _SLOT_TOOL,
                        "I keep a private spreadsheet instead of the official tool because it is unusable."),
            LatentTruth("eve_repeat", 2, ["ai_opportunity"], _SLOT_REPEAT,
                        "Most of my week is repetitive rules-based scheduling between systems."),
            # MISTAKEN: another unfounded attribution.
            LatentTruth("eve_blame_mistaken", 1, ["friction"], _SLOT_HONEST,
                        "Honestly I work differently because management keeps the roadmap secret."),
        ],
    )
    finn = Persona(
        name="Finn", role="Warehouse Lead", candor=candor,
        background="Runs the floor. Sees what actually happens versus what's written down.",
        latent_truths=[
            LatentTruth("finn_process", 1, ["process_reality"], _SLOT_PROCESS,
                        "In practice nobody follows the official process the way we're officially supposed to."),
            LatentTruth("finn_rework", 2, ["wasted_effort"], _SLOT_REWORK,
                        "The stock count is redundant work that gets redone every week."),
            LatentTruth("finn_queue", 2, ["bottlenecks"], _SLOT_QUEUE,
                        "Pallets stall and pile up waiting on the gate."),
        ],
    )
    return [ana, ben, cleo, dev, eve, finn]


def gold_truths(personas: list[Persona]) -> list[LatentTruth]:
    """Every latent truth in the org — the key the study labels findings against."""
    return [t for p in personas for t in p.latent_truths]
