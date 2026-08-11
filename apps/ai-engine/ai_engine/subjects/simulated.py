"""A simulated interviewee: a persona with hidden, tier-tagged truths and a candor dial.

This is the seed of the synthetic-organization testbed (research program Q16) and
the in-code version of the candor experiment (Q1/Q2): the persona holds a known
set of latent truths with known tiers, so we have *ground truth*. Running the same
interviewer against the same persona at different candor levels measures how much
Tier 2-4 truth the loop recovers — the candor capture ratio, with the denominator
known by construction.

With a live LLM the persona answers naturally in character; offline it uses a
deterministic keyword match so the loop and tests run with no network.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..llm.client import LLMClient
from ..interview.prompts import SUBJECT_SYSTEM

CANDOR_LEVELS = ("guarded", "neutral", "open")

# How sensitive a tier a given candor level will disclose.
_CANDOR_TIER_CAP = {"guarded": 1, "neutral": 3, "open": 4}


@dataclass
class LatentTruth:
    id: str
    tier: int
    areas: list[str]
    keywords: list[str]
    statement: str  # what the persona says when they disclose it


@dataclass
class Persona:
    name: str
    role: str
    candor: str  # guarded | neutral | open
    latent_truths: list[LatentTruth]
    background: str = ""
    _disclosed: set[str] = field(default_factory=set)

    def tier_cap(self) -> int:
        return _CANDOR_TIER_CAP.get(self.candor, 3)


def default_persona(candor: str = "neutral") -> Persona:
    """A concrete ops-analyst persona with known, tier-tagged truths."""
    return Persona(
        name="Sam",
        role="Operations Analyst",
        candor=candor,
        background=(
            "Mid-level ops analyst on a 6-person team. Diligent, a bit tired of "
            "manual work, careful about office politics."
        ),
        latent_truths=[
            LatentTruth("t1_crm", 1, ["process_reality"], ["crm", "update", "system", "record"],
                        "Honestly nobody really updates the CRM after a deal closes — it's always out of date."),
            LatentTruth("t2_spreadsheet", 2, ["workarounds", "wasted_effort"],
                        ["workaround", "instead", "tool", "spreadsheet", "manual", "report"],
                        "I keep my own private spreadsheet because the official dashboard is unusable, and I rebuild the weekly report by hand — about four hours every week."),
            LatentTruth("t2_shadow_ai", 2, ["workarounds", "ai_opportunity"],
                        ["ai", "chatgpt", "draft", "summar", "repetit", "automat"],
                        "I use my personal ChatGPT to draft the summaries — it's not sanctioned but it saves me a ton of time."),
            LatentTruth("t2_bottleneck", 2, ["bottlenecks"],
                        ["stall", "wait", "pile", "bottleneck", "stuck", "delay", "handoff"],
                        "Everything waits on the weekly report going out, and that waits on me having the numbers reconciled."),
            LatentTruth("t3_approval", 3, ["friction", "bottlenecks"],
                        ["approval", "decision", "manager", "director", "sign off", "friction", "politics"],
                        "The real bottleneck is my director's manual approval step — it routinely adds about three days and everyone just routes around it when they can."),
            LatentTruth("t4_padding", 4, ["friction", "wasted_effort"],
                        ["honest", "standup", "status", "hide", "pad", "yourself", "own version"],
                        "If I'm honest, the team pads status in standups so things look on-track, and I'm probably underutilized about a day a week."),
        ],
    )


def support_lead_persona(candor: str = "neutral") -> Persona:
    """A second persona (different role, different truths) for eval diversity."""
    return Persona(
        name="Rae",
        role="Support Team Lead",
        candor=candor,
        background="Leads a 5-person support queue. Protective of the team, wary of blame.",
        latent_truths=[
            LatentTruth("sl_t1_runbook", 1, ["process_reality"],
                        ["actually", "supposed", "runbook"],
                        "The runbook is out of date, so we actually just go off tribal knowledge instead of what we're supposed to do."),
            LatentTruth("sl_t2_triage", 2, ["workarounds"],
                        ["instead", "workaround", "tickets", "routing"],
                        "I re-triage tickets by hand in a side channel instead of the queue, because the routing rules are wrong."),
            LatentTruth("sl_t2_escalation", 2, ["bottlenecks"],
                        ["pile", "waiting", "stall", "escalation"],
                        "Escalations pile up waiting for engineering to pick them up — that's where everything stalls."),
            LatentTruth("sl_t2_canned", 2, ["ai_opportunity"],
                        ["repetitive", "rules-based", "canned", "responses"],
                        "I hand-write the same canned responses over and over; it's totally repetitive and rules-based."),
            LatentTruth("sl_t3_vp", 3, ["friction"],
                        ["decision", "priorities", "override", "made"],
                        "The VP keeps overriding our priorities — that's the real decision that's made badly."),
            LatentTruth("sl_t4_sla", 4, ["friction", "wasted_effort"],
                        ["honest", "differently", "supposed", "sla"],
                        "Honestly, I do it differently than I'm supposed to — I mark tickets resolved before they really are, to hit the SLA."),
        ],
    )


class SimulatedInterviewee:
    def __init__(self, persona: Persona, *, llm: LLMClient | None = None, temperature: float = 0.7) -> None:
        self._persona = persona
        self._llm = llm
        self._temperature = temperature
        self._history: list[dict[str, str]] = []

    @property
    def persona(self) -> Persona:
        return self._persona

    def answer(self, question: str) -> str:
        if self._llm is not None:
            return self._live_answer(question)
        return self._mock_answer(question)

    # -- live path ---------------------------------------------------------
    def _live_answer(self, question: str) -> str:
        truths = "\n".join(
            f"- (tier {t.tier}, {'/'.join(t.areas)}) {t.statement}"
            for t in self._persona.latent_truths
        )
        system = (
            f"{SUBJECT_SYSTEM}\n\n"
            f"YOUR CHARACTER: {self._persona.name}, {self._persona.role}. "
            f"{self._persona.background}\n"
            f"YOUR CANDOR LEVEL: {self._persona.candor}.\n"
            f"YOUR PRIVATE KNOWLEDGE (disclose per the candor rules):\n{truths}"
        )
        self._history.append({"role": "user", "content": question})
        text = self._llm.complete(
            system=system,
            messages=self._history,
            max_tokens=300,
            temperature=self._temperature,
        )
        self._history.append({"role": "assistant", "content": text})
        return text

    # -- mock path ---------------------------------------------------------
    def _mock_answer(self, question: str) -> str:
        low = question.lower()
        cap = self._persona.tier_cap()
        # Find the most relevant undisclosed truth this candor level permits.
        best: LatentTruth | None = None
        best_hits = 0
        for t in self._persona.latent_truths:
            if t.id in self._persona._disclosed or t.tier > cap:
                continue
            hits = sum(1 for kw in t.keywords if kw in low)
            if hits > best_hits:
                best, best_hits = t, hits
        if best is not None and best_hits > 0:
            self._persona._disclosed.add(best.id)
            return best.statement
        # No permitted, relevant truth: deflect if it's clearly sensitive, else be vague.
        if any(w in low for w in ("manager", "director", "politics", "honest", "own version", "status")):
            if cap < 3:
                return "I'd rather not get into personalities, to be honest."
        return "It's mostly fine, I guess — pretty standard stuff, nothing jumps out."
