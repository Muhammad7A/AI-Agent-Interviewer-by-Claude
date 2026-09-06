# Security Policy

## Why this file matters more here than in most repositories

Groundwork records employees describing their own workplaces — including
unsanctioned tools they use, workarounds they rely on, and judgments about
their managers. A vulnerability in this system does not leak rows in a
database. It can identify a named person as the source of a disclosure that
costs them their job.

Please treat that as the threat model when deciding whether something is worth
reporting. If you are unsure, report it.

## Reporting a vulnerability

**Do not open a public issue for security or privacy defects.**

Use GitHub's private reporting: go to the
[Security tab](https://github.com/Muhammad7A/groundwork/security/advisories/new)
and choose "Report a vulnerability". That opens a private advisory visible only
to the maintainers.

Please include:

- what you found, and the impact you think it has
- steps to reproduce, or a failing test
- the commit SHA you were on
- whether you believe it is already public

**Do not include real employee testimony in a report.** Use synthetic data —
`python3 -m ai_engine.synthetic` generates realistic organizations with known
ground truth, and it is the right vehicle for a reproduction case.

You can expect an acknowledgement within 7 days. This is a small project; that
is a realistic commitment rather than an aspirational one.

## What counts as a vulnerability here

Ordinary security defects apply, and so do these, which are specific to what
this system does. All of them are in scope:

**Re-identification.** Any path by which employer-facing output can be traced
back to an individual participant. This includes indirect routes: a topic label
derived from one person's phrasing, a group size small enough to identify a
lone dissenter, a timestamp that narrows the field, or a quote that is
distinctive enough to be recognized by a colleague.

**Privacy-firewall bypass.** Any route from raw testimony to an employer-facing
artifact that does not pass through `privacy.release()`, or any way to defeat
the k-anonymity or aggregate-only constraints it enforces.

**Evidence-integrity failures.** Anything that lets a claim reach a report
without a real, supporting quote:

- a *false accept* in the grounding gate — a fabricated or drifted quote that
  is accepted as verbatim
- a *false accept* in the entailment gate — a real quote accepted as support
  for a claim it does not support
- any way to mutate a transcript after the fact so that an existing evidence
  reference resolves to different text

These are the two gates the product's credibility rests on. A reproducible
false accept in either is a serious finding, not a bug report.

**Key and cipher handling.** Storage keys or re-identification keys written to
disk in plaintext, included in logs, or recoverable from committed artifacts.
Note that a configured `GROUNDWORK_STORE_KEY` with a broken `cryptography` install
must fail loudly rather than silently store plaintext — a regression there is
in scope.

**Production-posture bypass.** Any way `GROUNDWORK_ENV=production` can start while
serving mock cognition or storing plaintext. A deployment that silently serves
scripted fake interviews to real employees and records them as genuine
testimony is a serious defect, not a configuration mistake.

## Out of scope

- Findings in the `apps/core-api` TypeScript skeleton, which is unimplemented
  and does not run
- Reports generated solely by automated scanners, with no demonstrated impact
- Denial of service against a locally run development server
- Missing hardening headers on the local-only web apps, absent a concrete
  exploit

## Deploying this yourself

If you run Groundwork against real people, the following are your responsibility
and no license term transfers them:

- run with `GROUNDWORK_ENV=production`, which refuses to start without a live model
  and a working cipher
- store `GROUNDWORK_STORE_KEY` and the pseudonymization key in a secrets manager,
  never in the repository, never in the same place as employer deliverables
- obtain informed consent covering what is recorded, what is retained, who can
  see it, and how a participant withdraws
- honor withdrawal — the system supports it; your process has to actually use it
- never hand an employer anything that did not pass through `privacy.release()`

Anyone deploying this inherits a duty of care toward the people it interviews.
The Apache License disclaims warranty. It does not disclaim that.
