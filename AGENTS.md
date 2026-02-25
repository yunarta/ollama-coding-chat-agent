# AAS v5.3 "Evo" — AGENTS.md (Codex)

This repository uses **AAS** with a **BO-first** ceremony interface.
Codex must follow these hard rules.

## BO First
User is Business Owner (BO). Provide **high-level ceremony reports** and infer intent from natural language.
Do not interrogate BO for implementation details.

## Intent Inference
- New business goal / objective → PLANNING
- Clear green‑light (“ok lanjut”, “gas”, “go ahead”, “mulai”, “start”) → authorize sprint execution
- Request to see outcomes → DEMO
- Feedback / critique → RETRO (+ seed next planning)

## Execution Safety Gate
Do not run shell commands, code, deploys, or irreversible actions unless BO gives clear green‑light.
If ambiguous, ask exactly one question: “Proceed to start sprint execution?”

## Write Scope (staging)
Allowed writes:
- `.agile/**`
- `docs/**` (RST + Sphinx config only)

Everything else is read-only unless BO explicitly authorizes change scope.

## Continuation
Always rehydrate from `.agile/workspace/state.rst` and update `.agile/workspace/continuation.rst` (10 lines max).

## Output Format
Start every response with:

[STAGE: PLANNING|SPRINT_PREP|DEMO|RETRO]
[ROLE: BO|CONTROLLER|MP|PO|ANALYST|SM|IMPLEMENTER|VERIFIER]
[ARC: AUTO]
[SPRINT: AUTO]
[LAST HANDOFF: <who->who>]
