"""Dimension tables: the curated content of the simulation universe.

These are the legitimately hand-crafted parts (merged taxonomy §8.2): domain
vocabularies, competency ladders, kind sentence-shapes, marker judgments, and
the fairness prohibit-list. Mechanics stay in code; judgment lives here.

Schema: groundwork.universe/v1. Every table is validated at load.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SCHEMA = "groundwork.universe/v1"

LEVELS: dict[str, dict] = {
    "junior": {"required_depth": 2, "required_breadth": 2, "signal_floor": 2,
               "max_turns": 10},
    "mid": {"required_depth": 2, "required_breadth": 3, "signal_floor": 2,
            "max_turns": 12},
    "senior": {"required_depth": 3, "required_breadth": 3, "signal_floor": 3,
               "max_turns": 12},
    "expert": {"required_depth": 4, "required_breadth": 4, "signal_floor": 4,
               "max_turns": 16},
}

#: Sentence shapes per kind. {artifact}/{stressor}/{comp}/{premise} are filled
#: at render time from the domain vocab, competency ladder, and case premise.
KINDS: dict[str, dict] = {
    "technical": {
        "tier_names": {1: "mechanism", 2: "why it's built that way",
                       3: "what you'd change", 4: "learned the hard way"},
        "bank": {
            1: "Walk me through how the {comp} side of {artifact} actually works when {stressor} hits.",
            2: "Why is the {comp} setup built that way — what breaks first if {stressor} doubles?",
            3: "If you could change one thing about how {comp} works here, what and why?",
            4: "What did you learn the hard way about {comp} — what would you warn your past self about?"},
        "probe": "When did {comp} last matter in practice — walk me through that time.",
        "opening": ("Thanks for making the time — this is a working session; no trivia. "
                    "To start, walk me through how {artifact} actually gets done day to day."),
    },
    "behavioral": {
        "tier_names": {1: "the story", 2: "the reflection", 3: "the cost",
                       4: "what it says about you"},
        "bank": {
            1: "Tell me about a time {comp} was tested — when {stressor} hit, walk me through one, end to end.",
            2: "What would you do differently if you ran the same {comp} situation again?",
            3: "What did that {comp} situation cost you — and who else did it cost?",
            4: "What does that experience with {comp} say about how you work now?"},
        "probe": "Back to that {comp} situation — what would you do differently, specifically?",
        "opening": ("Thanks for making the time — I'm mapping how you work, not "
                    "grading you. To start: walk me through one piece of {artifact} "
                    "work you owned, end to end."),
    },
    "case": {
        "tier_names": {1: "structure", 2: "the key number",
                       3: "the recommendation", 4: "what would prove you wrong"},
        "bank": {
            1: "Here's the situation: {premise} Structure the {comp} problem before answering.",
            2: "What {comp} number matters most here, and how would you get a rough version of it?",
            3: "Give me your {comp} recommendation under {stressor}.",
            4: "What would have to be true for your {comp} recommendation to be wrong?"},
        "probe": "Take the {comp} structure you gave — where does it wobble first?",
        "opening": ("Thanks for making the time — this is a case built around a real "
                    "situation: {premise} To start: how would you structure this problem?"),
    },
    "debugging": {
        "tier_names": {1: "first moves", 2: "ruling out", 3: "root cause",
                       4: "the system that produced it"},
        "bank": {
            1: "A report comes in: {artifact} is failing under {stressor}, and it looks like a {comp} problem. How do you start?",
            2: "What would you rule out first in the {comp} path, and what would that tell you?",
            3: "Say your {comp} fix worked — why was it ever broken? What was the root cause?",
            4: "What does this {comp} incident say about the system that produced it?"},
        "probe": "Think of the last time {comp} was the suspect — what did you actually check first?",
        "opening": ("Thanks for making the time — we'll debug a real scenario together, "
                    "no tricks. The report: {premise} To start: how do you begin?"),
    },
    "system_design": {
        "tier_names": {1: "pin it down", 2: "the hardest part",
                       3: "the cost you accept", 4: "what you'd revisit"},
        "bank": {
            1: "Before any boxes and arrows: for the {comp} side of {premise_short}, what do you pin down first?",
            2: "What's the hardest part of the {comp} design — where is the real complexity?",
            3: "Where would your {comp} choice bite you first — what downside are you accepting?",
            4: "Suppose {stressor} doubles and the budget doesn't — what would you revisit in the {comp} design?"},
        "probe": "When did {comp} last shape a design you shipped — what happened?",
        "opening": ("Thanks for making the time — this is a design working session. "
                    "We're building: {premise} To start: what do you pin down first?"),
    },
}

#: Domain vocabularies. A domain contributes nouns; the kinds contribute prose.
DOMAINS: dict[str, dict] = {
    "software_engineering": {
        "name": "Software Engineering",
        "role_title": "Software Engineer",
        "artifacts": ["the ingest pipeline", "the auth service", "the deploy pipeline"],
        "stressors": ["10x load", "a region failover", "a schema migration"],
        "competencies": ["se_decomposition", "se_tradeoffs", "se_failure_thinking"],
        "case_families": ["cf_sre_telemetry_ingest"],
        "premises": [{
            "id": "cf_sre_telemetry_ingest",
            "text": ("We're building the ingest pipeline for a fleet-telemetry "
                     "platform: 40,000 vehicles reporting once a second, a "
                     "3-second freshness promise, and a team of five."),
            "short": "a fleet-telemetry ingest pipeline"}],
    },
    "product_management": {
        "name": "Product Management",
        "role_title": "Product Manager",
        "artifacts": ["the onboarding funnel", "the pricing page", "the roadmap"],
        "stressors": ["a churn spike", "a competitor launch", "half the budget"],
        "competencies": ["pm_prioritization", "pm_metrics", "pm_stakeholders"],
        "case_families": ["cf_activation_drop"],
        "premises": [{
            "id": "cf_activation_drop",
            "text": ("Activation dropped 30% in six weeks while signups held flat; "
                     "sales wants a fix this quarter and engineering has one "
                     "developer free."),
            "short": "a 30% activation drop"}],
    },
    "data": {
        "name": "Data & Analytics",
        "role_title": "Data Analyst",
        "artifacts": ["the metrics warehouse", "the exec dashboard", "the dbt models"],
        "stressors": ["a silent schema change", "duplicate events", "quarter-end"],
        "competencies": ["data_quality", "data_modeling", "data_communication"],
        "case_families": ["cf_metric_dispute"],
        "premises": [{
            "id": "cf_metric_dispute",
            "text": ("Two dashboards disagree about weekly active users by 12%, and "
                     "the board meeting is in nine days."),
            "short": "a 12% metric dispute"}],
    },
    "ai": {
        "name": "AI & Machine Learning",
        "role_title": "ML Engineer",
        "artifacts": ["the support-ticket classifier", "the recommendation model",
                      "the eval harness"],
        "stressors": ["distribution drift", "a prompt-injection wave", "label noise"],
        "competencies": ["ai_eval_thinking", "ai_failure_modes", "ai_data_cycles"],
        "case_families": ["cf_classifier_drift"],
        "premises": [{
            "id": "cf_classifier_drift",
            "text": ("The support-ticket classifier's precision fell from 0.9 to 0.7 "
                     "over a month with no deploy in between; the queue is drowning."),
            "short": "a silent precision drop"}],
    },
    "cybersecurity": {
        "name": "Cybersecurity",
        "role_title": "Security Engineer",
        "artifacts": ["the SSO rollout", "the incident-response runbook",
                      "the vuln scanner"],
        "stressors": ["a phishing wave", "a critical CVE", "an audit deadline"],
        "competencies": ["sec_threat_modeling", "sec_incident_response",
                         "sec_access_design"],
        "case_families": ["cf_credential_leak"],
        "premises": [{
            "id": "cf_credential_leak",
            "text": ("A batch of service credentials just appeared in a public "
                     "paste site; leadership wants to know scope and exposure in "
                     "one hour."),
            "short": "a public credential leak"}],
    },
    "finance": {
        "name": "Finance",
        "role_title": "Finance Analyst",
        "artifacts": ["the monthly close", "the cash forecast", "the pricing model"],
        "stressors": ["a missed quarter", "a funding delay", "an audit finding"],
        "competencies": ["fin_close_discipline", "fin_forecasting",
                         "fin_controls"],
        "case_families": ["cf_runway_shortfall"],
        "premises": [{
            "id": "cf_runway_shortfall",
            "text": ("Cash runway just came back four months shorter than last "
                     "quarter's model; the CEO wants options before the board "
                     "call."),
            "short": "a four-month runway shortfall"}],
    },
    "consulting": {
        "name": "Consulting",
        "role_title": "Associate Consultant",
        "artifacts": ["the client workshop", "the diagnosis deck",
                      "the transformation plan"],
        "stressors": ["a skeptical client CFO", "a two-week deadline",
                      "conflicting stakeholder accounts"],
        "competencies": ["con_structuring", "con_client_handling",
                         "con_synthesis"],
        "case_families": ["cf_ops_diagnosis"],
        "premises": [{
            "id": "cf_ops_diagnosis",
            "text": ("A logistics client says fulfillment is 'slow and chaotic' but "
                     "can't say where; you have two weeks and access to their floor."),
            "short": "a fulfillment diagnosis"}],
    },
    "operations": {
        "name": "Operations",
        "role_title": "Operations Lead",
        "artifacts": ["the dispatch schedule", "the vendor roster", "the SLA board"],
        "stressors": ["a driver shortage", "a warehouse outage", "peak season"],
        "competencies": ["ops_capacity", "ops_escalation", "ops_process_design"],
        "case_families": ["cf_peak_backlog"],
        "premises": [{
            "id": "cf_peak_backlog",
            "text": ("Peak season started early: backlog doubled overnight and two "
                     "of nine drivers called out."),
            "short": "a doubled overnight backlog"}],
    },
    "startup_founder": {
        "name": "Startup Founder",
        "role_title": "Founder",
        "artifacts": ["the pilot launch", "the investor pipeline", "the MVP"],
        "stressors": ["a churned pilot customer", "a demo day deadline",
                      "a co-founder departure"],
        "competencies": ["founder_ownership", "founder_customer",
                         "founder_resourcefulness"],
        "case_families": ["cf_pilot_churn"],
        "premises": [{
            "id": "cf_pilot_churn",
            "text": ("Your first pilot customer churned in week six, two weeks "
                     "before demo day."),
            "short": "a week-six pilot churn"}],
    },
}

#: Competencies: the unit of assessment — and, by design (D1), the engine's
#: coverage areas for a composed scenario. Flagship stems are the pairing
#: anchors between questions, probes, and disclosures; they are globally unique.
COMPETENCIES: dict[str, dict] = {
    # -- software engineering -------------------------------------------------
    "se_decomposition": {"name": "Problem decomposition", "class": "structuring",
                         "value": 4, "ceiling": 3, "domains": {"software_engineering"},
                         "nouns": {2: ["where the real complexity sits"],
                                   3: ["scope cuts"]}},
    "se_tradeoffs": {"name": "Architecture judgment", "class": "judgment",
                     "value": 5, "ceiling": 4, "domains": {"software_engineering"},
                     "nouns": {3: ["the shapes you picked"], 4: ["what you'd revisit"]}},
    "se_failure_thinking": {"name": "Failure-mode reasoning", "class": "failure",
                            "value": 4, "ceiling": 3, "domains": {"software_engineering"},
                            "nouns": {2: ["detect-and-recover"]}},
    # -- product management ---------------------------------------------------
    "pm_prioritization": {"name": "Prioritization under constraint", "class": "judgment",
                          "value": 5, "ceiling": 3, "domains": {"product_management"},
                          "nouns": {2: ["what ships first"]}},
    "pm_metrics": {"name": "Metric reasoning", "class": "evidence", "value": 4,
                   "ceiling": 3, "domains": {"product_management"},
                   "nouns": {2: ["the number that matters"]}},
    "pm_stakeholders": {"name": "Stakeholder handling", "class": "communication",
                        "value": 4, "ceiling": 2, "domains": {"product_management"},
                        "nouns": {2: ["what sales hears"]}},
    # -- data -----------------------------------------------------------------
    "data_quality": {"name": "Data quality reasoning", "class": "failure",
                     "value": 4, "ceiling": 3, "domains": {"data"},
                     "nouns": {2: ["silent breakage"]}},
    "data_modeling": {"name": "Modeling judgment", "class": "structuring",
                      "value": 4, "ceiling": 3, "domains": {"data"},
                      "nouns": {2: ["grain and joins"]}},
    "data_communication": {"name": "Communicating uncertainty", "class": "communication",
                           "value": 4, "ceiling": 2, "domains": {"data"},
                           "nouns": {2: ["confidence bands"]}},
    # -- ai -------------------------------------------------------------------
    "ai_eval_thinking": {"name": "Evaluation-first thinking", "class": "evidence",
                         "value": 5, "ceiling": 4, "domains": {"ai"},
                         "nouns": {2: ["the metric that moved"]}},
    "ai_failure_modes": {"name": "Failure-mode reasoning", "class": "failure",
                         "value": 4, "ceiling": 3, "domains": {"ai"},
                         "nouns": {2: ["drift and injection"]}},
    "ai_data_cycles": {"name": "Data-cycle design", "class": "structuring",
                       "value": 4, "ceiling": 3, "domains": {"ai"},
                       "nouns": {2: ["labeling loops"]}},
    # -- cybersecurity --------------------------------------------------------
    "sec_threat_modeling": {"name": "Threat modeling", "class": "structuring",
                            "value": 5, "ceiling": 4, "domains": {"cybersecurity"},
                            "nouns": {2: ["who would bother and how"]}},
    "sec_incident_response": {"name": "Incident response", "class": "failure",
                              "value": 5, "ceiling": 4, "domains": {"cybersecurity"},
                              "nouns": {2: ["the first hour"]}},
    "sec_access_design": {"name": "Access design", "class": "judgment",
                          "value": 4, "ceiling": 3, "domains": {"cybersecurity"},
                          "nouns": {2: ["least privilege"]}},
    # -- finance --------------------------------------------------------------
    "fin_close_discipline": {"name": "Close discipline", "class": "structuring",
                             "value": 4, "ceiling": 3, "domains": {"finance"},
                             "nouns": {2: ["reconciliation order"]}},
    "fin_forecasting": {"name": "Forecasting judgment", "class": "judgment",
                        "value": 5, "ceiling": 4, "domains": {"finance"},
                        "nouns": {2: ["assumptions vs actuals"]}},
    "fin_controls": {"name": "Controls reasoning", "class": "failure",
                     "value": 4, "ceiling": 3, "domains": {"finance"},
                     "nouns": {2: ["what a reviewer catches"]}},
    # -- consulting -----------------------------------------------------------
    "con_structuring": {"name": "Problem structuring", "class": "structuring",
                        "value": 5, "ceiling": 4, "domains": {"consulting"},
                        "nouns": {2: ["the issue tree"]}},
    "con_client_handling": {"name": "Client handling", "class": "communication",
                            "value": 4, "ceiling": 3, "domains": {"consulting"},
                            "nouns": {2: ["the skeptical CFO"]}},
    "con_synthesis": {"name": "Synthesis into recommendation", "class": "judgment",
                      "value": 5, "ceiling": 3, "domains": {"consulting"},
                      "nouns": {2: ["so-what logic"]}},
    # -- operations -----------------------------------------------------------
    "ops_capacity": {"name": "Capacity reasoning", "class": "structuring",
                     "value": 5, "ceiling": 3, "domains": {"operations"},
                     "nouns": {2: ["bottlenecks vs headcount"]}},
    "ops_escalation": {"name": "Escalation judgment", "class": "communication",
                       "value": 4, "ceiling": 3, "domains": {"operations"},
                       "nouns": {2: ["what reaches you at 2 a.m."]}},
    "ops_process_design": {"name": "Process design", "class": "judgment",
                           "value": 4, "ceiling": 3, "domains": {"operations"},
                           "nouns": {2: ["the checklist that prevents it"]}},
    # -- startup founder --------------------------------------------------------
    "founder_ownership": {"name": "Ownership & accountability", "class": "judgment",
                          "value": 5, "ceiling": 4, "domains": {"startup_founder"},
                          "nouns": {2: ["what you'd do differently"],
                                    3: ["what it cost you"]}},
    "founder_customer": {"name": "Customer proximity", "class": "evidence",
                         "value": 4, "ceiling": 2, "domains": {"startup_founder"},
                         "nouns": {2: ["what actually shipped"]}},
    "founder_resourcefulness": {"name": "Resourcefulness under constraint",
                                "class": "structuring", "value": 4, "ceiling": 2,
                                "domains": {"startup_founder"},
                                "nouns": {2: ["the scrappiest fix"]}},
}

#: Red-flag markers: an answer-shape that DEMANDS an evidence probe. A red
#: flag never auto-fails anyone — the probe outcome is the signal.
RED_FLAGS: dict[str, dict] = {
    "blame_shift": {"answer_stems": ["not our fault", "their team was a mess",
                                     "ghosted us"],
                    "probe": ("When you say it was their side — what did your "
                              "team own in that path, and what did you do when "
                              "they went quiet?")},
    "vague_forever": {"answer_stems": ["can't think of", "nothing specific"],
                      "probe": "Give me one concrete moment — any one."},
}


class TaxonomyTables:
    """The whole content universe, validated at load (loud, never partial)."""

    def __init__(self) -> None:
        self.schema = SCHEMA
        self.levels = LEVELS
        self.kinds = KINDS
        self.domains = DOMAINS
        self.competencies = COMPETENCIES
        self.red_flags = RED_FLAGS
        self._validate()

    def _validate(self) -> None:
        for domain_id, domain in self.domains.items():
            for comp in domain["competencies"]:
                if comp not in self.competencies:
                    raise ValueError(
                        f"domain {domain_id!r} references unknown competency "
                        f"{comp!r}")
                comp_domains = self.competencies[comp]["domains"]
                if "*" not in comp_domains and domain_id not in comp_domains:
                    raise ValueError(
                        f"domain {domain_id!r} lists competency {comp!r} that "
                        f"does not declare it")
        for comp_id, comp in self.competencies.items():
            if not (1 <= comp["ceiling"] <= 4):
                raise ValueError(f"competency {comp_id!r}: ceiling must be 1..4")
        for kind_id, kind in self.kinds.items():
            if set(kind["bank"]) != {1, 2, 3, 4}:
                raise ValueError(f"kind {kind_id!r}: bank must have tiers 1..4")
        # Global flagship-stem uniqueness: the taxonomy's scarce resource.
        stems: dict[str, str] = {}
        for comp_id, comp in self.competencies.items():
            for noun in comp.get("nouns", {}).values():
                for filler in ([noun] if isinstance(noun, str) else noun):
                    if filler in stems and stems[filler] != comp_id:
                        raise ValueError(
                            f"competencies {stems[filler]!r} and {comp_id!r} "
                            f"share the noun filler {filler!r} — flagship stems "
                            f"must be globally unique")
                    stems.setdefault(filler, comp_id)


DEFAULT_TABLES = TaxonomyTables()


#: Fairness prohibit-list: never appears in any lexicon, marker, or rendered
#: text; checked against produced utterances. Curated, versioned, fail-closed.
PROHIBITED_STEMS = (
    "your age", "how old", "pregnan", "married", "religion", "ethnic",
    "disability", "sexual orientation", "where are you really from",
)
