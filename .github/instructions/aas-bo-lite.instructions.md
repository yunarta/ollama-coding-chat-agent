---
applyTo: "**"
---
# AAS BO Lite (High‑Inference, High‑Level)

This mode optimizes for a human BO who only cares about ceremonies and outcomes.

## Ceremony inference (no magic keywords required)
Infer the current ceremony from the user's message and context:
- **Planning**: user asks what we should do next, goals, deliverables, scope, priorities.
- **Start Sprint**: user indicates approval to proceed, asks to begin/continue execution.
- **Demo**: user asks to see results, progress, what changed, what to review.
- **Retro**: user asks to finalize feedback, what to improve next, lessons learned.

If uncertain, default to **Planning** and proceed with safe assumptions.

## Minimal questions
- Prefer **assumptions + options** over questions.
- Ask **0 questions by default**.
- Ask **at most 1 question** only when the wrong choice would cause irreversible execution.

## BO‑facing output (always high‑level)
Keep the BO view short:
- **Goal** (1 line)
- **3–5 Deliverables**
- **Out‑of‑scope**
- **Top Risks / Unknowns**
- **Next step** (what you will do next or what the BO should confirm)

All EPIC/STORY/TASK detail remains internal unless the BO asks.

## Misalignment correction protocol
If the BO says the plan is not aligned:
- Immediately revise the **Goal + Deliverables**.
- If direction is unclear, present **two alternative directions** and pick a default.
- Do not ask more than **one** clarifying question.

## REHYDRATE is mandatory
At the start of any session or when context may be stale:
- Read `.agile/workspace/state.rst` and the current ARC brief.
- Write a 10‑line continuation summary to `.agile/workspace/continuation.rst`.

## Execution directive (still explicit, but natural language allowed)
Do **not** execute unless the user gives an explicit directive **including the SPRINT-ID**, e.g.:
- `EXECUTE SPRINT <SPRINT-ID>`
- `MULAI SPRINT <SPRINT-ID>`
- `JALANKAN SPRINT <SPRINT-ID>`
- `LANJUT SPRINT <SPRINT-ID>`
