---
applyTo: "**"
---
# AAS Ceremony Mode (BO‑first, minimal friction)

Humans often want the **ceremonies**, not the internal mechanics.

## Conversation loop (preferred)
1) **Planning**
2) **Start Sprint**
3) **Sprint Demo**
4) **Sprint Retro**
Then loop back to Planning.

> Note: You must infer the ceremony from the user's message. Do not require specific keywords.

## Interaction rules
- Ask **at most one question per ceremony**. Prefer assumptions + options over interrogations.
- If information is missing, proceed with **safe defaults** and clearly label assumptions.
- Keep BO-facing outputs short: **Goal + 3–5 Deliverables + Out-of-scope + Risks + Next step**.
- Do not force the BO to care about EPIC/STORY/TASK unless they explicitly ask.

## What to write (staging)
- Planning produces:
  - `.agile/workspace/planning-brief.rst`
- Demo produces:
  - `.agile/reports/arcs/<ARC-ID>/sprints/<SPRINT-ID>/demo-pack.rst` (or draft in workspace)
- Retro produces:
  - `.agile/reports/arcs/<ARC-ID>/sprints/<SPRINT-ID>/retro-report.rst` (or draft in workspace)

## Governance (still applies)
- Execution remains forbidden until an explicit directive including SPRINT-ID is given
  (see always‑on guardrails).
- SM gate remains strict at Stage 3.
