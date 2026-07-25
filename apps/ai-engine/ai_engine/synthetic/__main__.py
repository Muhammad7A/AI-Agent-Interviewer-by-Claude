"""Inspect a generated organization without running any interviews.

    python -m ai_engine.synthetic --size 20 --seed 3
    python -m ai_engine.synthetic --size 12 --minority-correct-rate 0.5

Prints the org's composition, what was planted, and each persona's beliefs with
ground truth marked — so you can see exactly what the pipeline is being asked to
recover before you ask it to recover anything.
"""
from __future__ import annotations

import argparse
import sys

from .generator import generate_org
from .model import OrgSpec


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect a synthetic organization")
    parser.add_argument("--size", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--name", default="SynthCo")
    parser.add_argument("--topics-per-person", type=int, default=3)
    parser.add_argument("--contradiction-rate", type=float, default=0.5)
    parser.add_argument("--minority-correct-rate", type=float, default=0.25)
    parser.add_argument("--bias-rate", type=float, default=0.25)
    parser.add_argument("--verbose", action="store_true", help="list every belief")
    args = parser.parse_args(argv)

    org = generate_org(OrgSpec(
        size=args.size, seed=args.seed, name=args.name,
        topics_per_person=args.topics_per_person,
        contradiction_rate=args.contradiction_rate,
        minority_correct_rate=args.minority_correct_rate,
        bias_rate=args.bias_rate,
    ))

    print(f"# {args.name} — generated organization (seed {args.seed})")
    print()
    print(f"- Employees: {len(org.personas)} (requested {args.size})")
    print(f"- Candor mix: {org.candor_counts()}")
    print(f"- Planted beliefs: {org.total_truths}  "
          f"({org.total_mistaken} false = {org.total_mistaken / max(1, org.total_truths):.0%})")
    print(f"- Reachable given candor: {org.reachable_truths()}/{org.total_truths} "
          f"(guarded employees withhold their Tier 2+ beliefs)")
    print(f"- Unfounded attributions: {len(org.bias_holders)} "
          f"({', '.join(org.bias_holders) or 'none'})")
    print()
    if org.contradictions:
        print("## Planted contradictions")
        print()
        for c in org.contradictions:
            who = "MINORITY is right" if c.minority_is_correct else "majority is right"
            print(f"- **{c.topic_key}** — {who}")
            print(f"  - majority ({len(c.majority)}): {', '.join(c.majority)}")
            print(f"  - minority ({len(c.minority)}): {', '.join(c.minority)}")
            print(f"  - therefore wrong: {', '.join(c.wrong_side)}")
        print()

    if args.verbose:
        print("## Beliefs by employee")
        print()
        for p in org.personas:
            print(f"### {p.name} — {p.role} (candor: {p.candor})")
            for t in p.latent_truths:
                mark = "FALSE" if not org.is_veridical(t.id) else "true "
                print(f"  - [{mark} tier {t.tier}] {t.statement}")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
