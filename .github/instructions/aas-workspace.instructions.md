---
applyTo: ".agile/workspace/**"
---
# AAS Workspace Writing Rules (v5)

- Workspace files may be iterative, but must be readable and structured.
- Prefer **reStructuredText (RST)** for artifacts that may later be published.

## Mandatory workspace anchors
- `.agile/workspace/state.rst` tracks: current ARC, current sprint, stage, role, last handoff, and next actions.
- `.agile/workspace/continuation.rst` is written at Stage 1 REHYDRATE (10–15 lines).

## Every major artifact includes
- ID
- Title
- Intent
- Links (traceability)
- Status
- Last updated timestamp (ISO 8601)
