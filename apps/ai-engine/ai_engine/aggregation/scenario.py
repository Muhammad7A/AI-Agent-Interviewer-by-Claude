"""A demo organization whose interviews deliberately overlap — on purpose.

Nine employees of "Northwind", a logistics company. Interviewed and aggregated,
they are tuned so the two deliverables each do something worth pitching:

  * the **consultant synthesis** (inside the privacy firewall) shows every topic
    with attributed verbatim quotes, and
  * the **employer release** is gated by k-anonymity (k=3): a topic needs three
    distinct participants or it is suppressed into the ledger.

The org is shaped so the employer view is interesting on BOTH sides of that gate.
Two topics clear k: the director's-approval bottleneck (six voices) and weekly
reports rebuilt by hand (three voices). Everything else is withheld *by design* —
the suppression ledger is the pitch moment ("here is what the employer never sees
and why"): VIP customers jumped up the queue, told near-identically by Ines and
Bram, clusters at exactly two voices and dies at the threshold; four more
disclosures stay single-source (Marcus stacking pallets in the fire lane, Priya's
unlogged journal entry for VIP discounts, Theo's shared printer password, Wren
skipping cycle counts). Dana, Eli and Bram still disagree on whether anyone
follows the official process, so the contested topic stays contested.

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
    bram = Persona(
        name="Bram",
        role="Sales Account Exec",
        candor=candor,
        background="Carries a book of key accounts. Charming, protective of his customers.",
        latent_truths=[
            LatentTruth("bram_process", 1, ["process_reality"], ["supposed", "officially"],
                        "Officially there's a handoff process for every deal, but honestly "
                        "nobody follows the official process — everyone just wings it."),
            LatentTruth("bram_vip", 2, ["workarounds"], ["instead", "workaround"],
                        "When a VIP customer complains, I bump their deliveries to the front "
                        "of the queue instead of the official order — VIPs get priority on request."),
        ],
    )
    ines = Persona(
        name="Ines",
        role="Customer Service Rep",
        candor=candor,
        background="Lives in the inbound queue all day. Warm, quick, loyal to her regulars.",
        latent_truths=[
            LatentTruth("ines_vip", 2, ["workarounds"], ["instead", "workaround"],
                        "If a VIP customer asks, I move them to the front of the queue "
                        "instead of the official order — keeping the VIPs happy is my job."),
        ],
    )
    marcus = Persona(
        name="Marcus",
        role="Warehouse Lead",
        candor=candor,
        background="Runs the floor crew. Direct, protects his people, hates idle trailers.",
        latent_truths=[
            LatentTruth("marcus_approval", 3, ["friction"], ["decision", "made"],
                        "Everything on my shift waits on the director's approval — that "
                        "decision, made upstairs, is the bottleneck that stalls the whole floor."),
            LatentTruth("marcus_pallets", 2, ["workarounds"], ["instead", "workaround"],
                        "When the dock backs up, I stack pallets in the fire lane instead of "
                        "the marked bay — it's the only thing that keeps the trailers moving."),
        ],
    )
    priya = Persona(
        name="Priya",
        role="Finance Clerk",
        candor=candor,
        background="Closes the payables side every week. Precise, allergic to loose ends.",
        latent_truths=[
            LatentTruth("priya_approval", 3, ["friction"], ["decision", "made"],
                        "Refunds of any real size wait on the director's approval — that "
                        "decision, made at the top, is the bottleneck that stalls the payout."),
            LatentTruth("priya_report", 2, ["wasted_effort"], ["redundant", "redone"],
                        "Every Friday I rebuild the weekly finance report by hand in a "
                        "spreadsheet — the export gives me half of what I need, so I retype the rest."),
            LatentTruth("priya_journal", 3, ["workarounds"], ["instead", "workaround"],
                        "For VIP discounts the system has no field, so I book an unlogged "
                        "manual journal entry instead and it never shows in the audit trail."),
        ],
    )
    theo = Persona(
        name="Theo",
        role="IT Support",
        candor=candor,
        background="Keeps the site's machines and printers alive. Fixes everything, files nothing.",
        latent_truths=[
            LatentTruth("theo_budget", 3, ["friction"], ["decision", "made"],
                        "Every tooling request dies in the ops manager's budget review — the "
                        "decision made there kills anything with a price tag."),
            LatentTruth("theo_report", 2, ["wasted_effort"], ["redundant", "redone"],
                        "The asset register is the same story — I rebuild that spreadsheet by "
                        "hand every month because the export tool skips half the fleet."),
            LatentTruth("theo_password", 4, ["friction"], ["honest", "differently"],
                        "Honestly, I do it differently than I'm supposed to — the legacy label "
                        "printer runs on one shared password instead of proper accounts, and "
                        "I've never reported it."),
        ],
    )
    wren = Persona(
        name="Wren",
        role="Night-shift Inventory Clerk",
        candor=candor,
        background="Counts the warehouse alone after midnight. Quiet, stubborn, exact.",
        latent_truths=[
            LatentTruth("wren_approval", 3, ["friction"], ["decision", "made"],
                        "Everything on nights waits on the director's approval — the decision "
                        "gets made at a morning meeting and the bottleneck stalls the restock."),
            LatentTruth("wren_report", 2, ["wasted_effort"], ["redundant", "redone"],
                        "The stock report I rebuild by hand in a spreadsheet every morning "
                        "before clocking off, because the scanner export comes out stale."),
            LatentTruth("wren_cycle", 2, ["workarounds"], ["instead", "workaround"],
                        "When we're short-staffed I skip the cycle counts and trust last "
                        "week's numbers instead — it's a workaround, but the shelves stay right."),
        ],
    )
    return [dana, eli, fern, bram, ines, marcus, priya, theo, wren]
