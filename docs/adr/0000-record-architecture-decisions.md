# 0. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-07-21

## Context

This platform is intended to grow from a Discovery-phase interview tool into a
full Organizational Intelligence product. Early structural decisions have
outsized, long-lived consequences. We want those decisions to be explicit,
justified, and reviewable rather than implicit in the code.

## Decision

We will use **Architecture Decision Records (ADRs)** to capture every
significant architectural choice — one file per decision, numbered
sequentially, immutable once accepted.

- A decision is "significant" if reversing it later would be expensive: runtime
  boundaries, layering rules, persistence strategy, tenancy model, the AI
  provider abstraction, etc.
- ADRs are append-only. A decision is changed by writing a **new** ADR that
  supersedes the old one; the old one is marked `Superseded by NNNN` but not
  deleted. The history is the point.

## Consequences

- The rationale behind the codebase's shape is discoverable in one place.
- New engineers (and future us) can see _why_, not just _what_.
- `docs/ARCHITECTURE.md` describes the current state; `docs/adr/` explains how we
  got there.

## Format

Each ADR: **Context** (the forces at play) → **Decision** (what we chose) →
**Consequences** (what follows, good and bad).
