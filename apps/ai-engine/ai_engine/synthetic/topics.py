"""Topic templates: the vocabulary machinery that makes generated orgs work.

Generated statements must survive four downstream mechanisms, and the templates are
engineered so they do *systematically* rather than by hand-tuning:

1. **Elicitation** — ``slot`` keywords must hit one of the offline interviewer's
   ladder questions, so the truth actually gets disclosed in mock mode. Each
   template owns a distinct slot, so one persona can hold several topics and have
   all of them elicited.
2. **Clustering** — members of one topic must share enough vocabulary to land in the
   same aggregated topic. Guaranteed by a shared ``core`` phrase: with the core at
   least as long as the per-person ``variant``, overlap is >= 0.5 by construction.
3. **Agreement** — same topic + same polarity + overlap >= 0.5 reads as AGREE.
   Two holders of the same core differ only by variant, so they agree.
4. **Contradiction** — ``denial`` keeps the core's topic words but flips polarity
   cues, so it lands in the same cluster and reads as CONFLICT.

``tagger_tier`` records the tier the offline tagger will assign from the keyword in
the core (see ``evidence/tagger._MOCK_RULES``) — the cores are kept disjoint on
those keywords so classification is predictable.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicTemplate:
    key: str
    slot: tuple[str, ...]        # keywords matching one interviewer-ladder question
    areas: tuple[str, ...]
    tier: int                    # disclosure tier -> gates elicitation by candor
    core: str                    # shared phrase: guarantees clustering + AGREE
    variants: tuple[str, ...]    # short per-person prefix (kept shorter than core)
    denial: str | None           # opposite-polarity form, or None if it can't host one
    tagger_tier: int             # tier the offline tagger derives from the core

    def statement(self, variant: str, *, deny: bool = False) -> str:
        body = self.denial if (deny and self.denial) else self.core
        return f"{variant} {body}".strip()

    @property
    def can_contradict(self) -> bool:
        return self.denial is not None


# One template per interviewer-ladder slot. Cores are disjoint on tagger keywords.
TOPIC_TEMPLATES: tuple[TopicTemplate, ...] = (
    # NOTE on polarity: a contradiction is only *detected* when BOTH sides carry a
    # non-zero polarity cue, so every deniable core states its claim with an
    # explicit affirmative cue ("always", "consistently", "reliable") and every
    # denial with an explicit negative one ("never", "nobody", "not"). Without this
    # a planted contradiction is generated but silently never detected — the
    # benchmark would then be measuring nothing.
    TopicTemplate(
        key="approval",
        slot=("decision", "made"),           # "...or a decision someone made?"
        areas=("friction",),
        tier=3,
        # Carries an explicit figure ("three days"). The generated corpus otherwise
        # contains no numbers at all, which left the number-substitution mutator with
        # nothing to substitute — so the entailment gate's quantity check had no case
        # to answer and the fuzz property recorded zero runs while appearing healthy.
        # Both holders of this topic share the core, so the figure agrees between
        # them; the denial carries no figure, so it still conflicts on polarity alone.
        core="the director's approval decision always holds up the whole flow for three days",
        variants=("On my desk,", "For my team,", "In my area,", "Every week,",
                  "From where I sit,"),
        denial="the director's approval decision never holds up the flow for anyone",
        tagger_tier=3,                        # "approval" -> friction, tier 3
    ),
    TopicTemplate(
        key="process",
        slot=("supposed", "officially"),      # "...how it's officially supposed to work?"
        areas=("process_reality",),
        tier=1,
        core="we always follow the official written procedure exactly as intended",
        variants=("Day to day,", "On this team,", "In practice,", "Most weeks,",
                  "Across the board,"),
        denial="nobody will follow the official written procedure as intended",
        tagger_tier=1,                        # no tagger keyword -> observation, tier 1
    ),
    TopicTemplate(
        key="rework",
        slot=("redundant", "redone"),         # "...felt redundant or got redone?"
        areas=("wasted_effort",),
        tier=2,
        core="the weekly report is always redundant work that gets redone from scratch",
        variants=("For me,", "On my side,", "In my role,", "Each cycle,",
                  "Most months,"),
        denial="the weekly report is never redundant and is not redone from scratch",
        tagger_tier=2,                        # "redundant" -> wasted_effort, tier 2
    ),
    TopicTemplate(
        key="queue",
        slot=("stall", "pile"),               # "...stall or pile up waiting?"
        areas=("bottlenecks",),
        tier=2,
        core="jobs always stall and pile up while waiting on the upstream handoff",
        variants=("At the intake,", "On the floor,", "In my queue,", "By midweek,",
                  "At month end,"),
        denial="jobs never stall or pile up while waiting on the upstream handoff",
        tagger_tier=2,                        # "stall" -> bottleneck, tier 2
    ),
    TopicTemplate(
        key="tooling",
        slot=("instead", "workarounds"),      # "...do instead - any workarounds?"
        areas=("workarounds",),
        tier=2,
        core="I keep a private tracker instead of the sanctioned system because it is unusable",
        variants=("Honestly,", "For my own sanity,", "Quietly,", "Since last year,",
                  "Like most people,"),
        denial="the sanctioned system is reliable so I always use it",
        tagger_tier=2,                        # "instead" -> workaround, tier 2
    ),
    TopicTemplate(
        key="repetition",
        slot=("repetitive", "rules-based"),   # "...most repetitive or rules-based?"
        areas=("ai_opportunity",),
        tier=2,
        core="my week is consistently repetitive rules-based copying between systems",
        variants=("Frankly,", "If I add it up,", "Every single day,", "By volume,",
                  "For hours,"),
        denial="my week is never repetitive or rules-based in any way",
        tagger_tier=2,                        # "repetit" -> ai_opportunity, tier 2
    ),
    # A second instance of two topics, with deliberately DISJOINT vocabulary so they
    # form separate clusters despite sharing an interviewer slot. This is what gives
    # a large org topic diversity instead of ten people all corroborating one thing.
    # (One person may only hold one topic per slot, or the other would never be asked.)
    TopicTemplate(
        key="signoff",
        slot=("decision", "made"),
        areas=("friction",),
        tier=3,
        core="finance sign off is always the step that blocks every invoice for weeks",
        variants=("Quarter after quarter,", "In billing,", "For my accounts,",
                  "Since the reorg,", "Without fail,"),
        denial="finance sign off never blocks any invoice at all",
        tagger_tier=3,                        # "sign off" -> friction, tier 3
    ),
    TopicTemplate(
        key="handover",
        slot=("stall", "pile"),
        areas=("bottlenecks",),
        tier=2,
        core="paperwork is consistently stuck at the loading bay overnight",
        variants=("On lates,", "Before dawn,", "At the bay,", "Most nights,",
                  "During peak,"),
        denial="paperwork is never stuck at the loading bay overnight",
        tagger_tier=2,                        # "stuck" -> bottleneck, tier 2
    ),
)

TEMPLATES_BY_KEY = {t.key: t for t in TOPIC_TEMPLATES}

# --- unfounded attributions (bias) ----------------------------------------
# Planted as single-source falsehoods, so each holder needs a DISTINCT target:
# a shared core would make independent bias-holders cluster and *corroborate each
# other*, manufacturing a high-confidence false finding out of nothing. That was a
# real bug this testbed caught. To study that phenomenon deliberately, use
# ``OrgSpec.correlated_bias_rate`` instead of relying on an accident.
BIAS_SLOT = ("honest", "differently")
BIAS_TIER = 3
BIAS_AREAS = ("friction",)
BIAS_PREFIXES = ("Between us,", "To be blunt,", "Off the record,", "Truthfully,",
                 "If I am candid,")

BIAS_CORES: tuple[str, ...] = (
    "I work differently because the other shift simply refuses to coordinate",
    "I plan around finance because those managers quietly veto every request",
    "I avoid the supplier portal because that vendor ignores each deadline",
    "I route around the platform team because they discard our tickets",
    "I double check the depot because those drivers skip their handover notes",
    "I bypass the review board because its members never read a submission",
)
