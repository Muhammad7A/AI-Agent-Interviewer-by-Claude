# Contributing to Ontora

Thanks for looking. This document covers how to get the code running, what CI
enforces, and the few rules that are not negotiable.

## Get it running

You need **Python 3.10 or newer**. Nothing else.

```bash
git clone https://github.com/Muhammad7A/AI-Agent-Interviewer-by-Claude.git
cd AI-Agent-Interviewer-by-Claude/apps/ai-engine
python3 -m unittest discover -s tests
```

That should report 273 tests and `OK`. If it does, you have a complete working
environment — there is no install step for the core engine.

Then watch it work:

```bash
python3 -m ai_engine.cli --simulated --candor open      # produces findings
python3 -m ai_engine.cli --simulated --candor guarded   # correctly produces none
```

For the web apps:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[web]'
python3 -m ai_engine.webapp
```

New to the codebase? [`docs/CODE_WALKTHROUGH.md`](docs/CODE_WALKTHROUGH.md)
explains every module, and [`docs/REPO_MAP.md`](docs/REPO_MAP.md) is a
file-by-file index.

## What CI enforces

Every push runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml), in this
order. All of it must pass.

**1. The zero-dependency import contract, on a bare interpreter.**
Every core module must import with no third-party package installed. This runs
*before* anything is installed, deliberately.

**2. The full test suite, with optional extras installed.**
The extras are installed so their tests actually execute.

**3. Zero skipped tests.**
A skip in CI means a dependency is missing and a guarantee went unverified. A
green build that tested nothing is worse than a red one, because it lies.
Skipping locally is fine.

**4. The evaluation gate** (`python3 -m ai_engine.eval`).
Fails the build if confabulation rises or truth recovery drops below threshold.

**5. The fuzz audit** (`python3 -m ai_engine.fuzz --cases 800 --org-size 8`).
Property-based adversarial testing of the grounding and entailment gates. Any
false accept, false reject, integrity violation, or crash fails the build.

Run the whole thing locally before opening a PR:

```bash
cd apps/ai-engine
python3 -m unittest discover -s tests && python3 -m ai_engine.eval && python3 -m ai_engine.fuzz
```

## Rules that are not negotiable

These exist because breaking them produces failures that look like success,
which is the dangerous kind. [`docs/ENGINEERING_CONSTITUTION.md`](docs/ENGINEERING_CONSTITUTION.md)
has the full reasoning.

**The core imports with zero dependencies.** Optional packages go behind
extras and lazy imports. This broke once — the web app's `__init__` eagerly
imported FastAPI — and `tests/test_import_contract.py` exists so it cannot break
again silently.

**No claim reaches a report without passing both gates.** Grounding proves the
quote exists; entailment proves it supports the claim. Neither substitutes for
the other. Do not add a path that bypasses either, and do not weaken a gate to
make a test pass — if a gate rejects something you believe is correct, the
interesting bug is probably in the gate, and it needs a test either way.

**Transcripts are immutable.** Evidence references are permanent addresses into
them. Anything that mutates a transcript after the fact invalidates every
finding that cites it.

**Nothing reaches an employer except through `privacy.release()`.** Not a
convenience path, not a debug endpoint, not a log line.

**Never commit testimony or keys.** `.gitignore` covers `data/`,
`*.testimony.jsonl`, `*.RESTRICTED.*`, and `identity-key*`. Git history is
permanent; a key removed in the next commit is still in the history forever.
Use `python3 -m ai_engine.synthetic` when you need realistic data.

**Determinism is the cache boundary.** `temperature == 0` calls are cacheable;
anything above 0 is deliberate sampling and is never cached. Caching a sampled
call replaces variation with repetition — a behavior change disguised as an
optimization.

## Pull requests

Work on a branch, not `main`.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(ai-engine): encrypt the event logs, closing a half-truth I introduced
fix(evidence): guard word boundaries so "vendor I" stops matching "vendor ignores"
docs(readme): show real CLI output instead of an invented example
test(fuzz): add cosmetic mutations that must not change gate verdicts
```

Say what changed and why. `fix stuff` tells a future reader nothing.

In the PR description, cover: what changed, why, and how you verified it. If
you changed anything in `evidence/`, `privacy/`, or `validation/`, say
explicitly what you did to convince yourself the gates still hold.

**New behavior needs a test that would have failed before.** For the safety
gates specifically, prefer a property the fuzzer can check over a single
example — every real bug found in those gates so far was found by the fuzzer,
not by inspection.

## Reporting bugs

Open an issue with the command you ran, what you expected, what happened, your
Python version, and the commit SHA.

**Except for security and privacy defects** — those go through
[SECURITY.md](SECURITY.md), privately. A re-identification path or a gate false
accept should not be disclosed in a public issue.

Never paste real testimony into an issue. Use synthetic data.

## Good first contributions

- Run the fuzzer with a high case count and a new mutation strategy; if it
  finds a false accept, that is a genuinely valuable bug report
- Improve `docs/CODE_WALKTHROUGH.md` where it lost you — confusion is data
- Add adversarial cases to the eval dataset that current gates handle badly
- Widen `_canon` normalization coverage for quote text the grounding gate
  currently rejects for cosmetic reasons

## License

Contributions are licensed under [Apache License 2.0](LICENSE), the same terms
as the project.
