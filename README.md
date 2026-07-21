# AI-Agent-Interviewer-by-Claude

An **Organizational Intelligence platform** for an AI Transformation consulting
firm. It automates the **Discovery & Assessment** phase of a consulting
engagement: instead of consultants interviewing dozens of employees by hand, the
platform conducts AI-driven interviews, builds a structured model of how the
organization actually works, surfaces bottlenecks and AI opportunities, and
generates evidence-backed insights for consultants to validate and act on.

This is **not** a chatbot product. The AI interview is the ingestion layer; the
product is the pipeline from raw conversation to queryable organizational
knowledge. Human consultants remain accountable for validation and strategy.

> **Core property:** every insight is traceable to the transcript evidence that
> justifies it.

## Architecture at a glance

Two runtimes, one product:

- **`apps/core-api`** — TypeScript / NestJS. The system of record: persistence,
  multi-tenancy, auth, orchestration, audit, consultant APIs. A modular monolith
  of bounded contexts.
- **`apps/ai-engine`** — Python / FastAPI. Stateless AI cognition: interview
  turns, extraction, knowledge construction, and detection. Owns no business
  truth.
- **`packages/contracts`** — the versioned contract between the two runtimes,
  generating both TS types and Python models.
- **`apps/web`** — Next.js UIs (later).

Read the full design in **[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** and
the decisions behind it in **[`docs/adr/`](docs/adr/)**.

## Status

Foundational skeleton. Architecture and bounded-context boundaries are ratified;
no business logic has been implemented yet — that is deliberate. Work is added
_into_ this structure, following the layering and boundary rules the docs
define.
