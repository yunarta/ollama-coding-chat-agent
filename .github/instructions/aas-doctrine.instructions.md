---
applyTo: "**"
---
# AAS v5.1 "Evo" — Doctrine (Reference)

This file is **reference only**. Hard guardrails live in `.github/copilot-instructions.md` and the selected AAS agents.

## Canonical Stages
1 Controller: REHYDRATE (read state + arc context + write continuation)
2 PO+Analyst: PLAN (ARC/EPIC/STORY/TASK, report plan, doc plan)
3 SM: GATE (APPROVE_FOR_EXECUTION / REJECT / REQUEST_CHANGE → READY_FOR_EXECUTION)
4 Implementer+Verifier: EXECUTE & VERIFY (requires explicit user `EXECUTE SPRINT <SPRINT-ID>`) + PO+SM DEMO & REPORT

## MP Role (on‑demand)
MP is **not** a stage. MP is engaged only when the squad lacks a role/skill definition, risk framing, or staffing plan.
Outputs go to: `.agile/workspace/staffing/`.

## ARC Model
- ARC-000 Vision & Goals is the foundation.
- Other arcs may run in parallel.

SSOT location:
- `.agile/program/arcs/<ARC-ID>/` (arc brief, goals, glossary, constraints)

## Naming
- ARC: `ARC-000`, `ARC-010`, `ARC-020`, ...
- Sprint: `<ARC-ID>-SPRINT-YYYYMMDD-XX`
- EPIC-###-slug
- STORY-###-slug
- TASK-###-slug

## Diátaxis docs (always)
Project documentation is always maintained in `docs/` using Diátaxis:
- `docs/tutorials/`
- `docs/how-to/`
- `docs/explanation/`
- `docs/reference/`

Use reStructuredText unless there is a very specific reason not to.
