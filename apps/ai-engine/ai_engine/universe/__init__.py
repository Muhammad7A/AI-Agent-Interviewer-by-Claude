"""The interview simulation universe — a composable scenario framework.

Nine domains × four levels × five interview kinds, composed from dimension
tables into scenarios the existing engine runs offline and the existing lab
grades. Nothing here hardcodes thousands of prompts: a domain contributes
*nouns*, a level contributes a *bar*, a kind contributes *sentence shapes*,
a competency contributes the *content ladder* — and `compose()` + `render()`
assemble them, loudly refusing anything that would half-work.
"""
from .tables import DEFAULT_TABLES, DOMAINS, KINDS, LEVELS, TaxonomyTables
from .compose import (CompositionError, RenderedScenario, ScenarioSpec,
                      compose, render)

__all__ = [
    "TaxonomyTables", "DEFAULT_TABLES", "LEVELS", "KINDS", "DOMAINS",
    "compose", "render", "CompositionError", "ScenarioSpec",
    "RenderedScenario",
]
