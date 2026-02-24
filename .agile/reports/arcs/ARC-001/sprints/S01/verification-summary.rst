Verification Summary: Sprint S01
================================

Acceptance Checklist
--------------------

A1 Session list exists
  - Given >=2 sessions, UI shows list with title/snippet/updated_at.
  - Evidence: implemented in ``app.js`` (session list render) and ``/api/sessions``.

A2 Click session to view conversation
  - Evidence: ``GET /api/sessions/{id}`` + conversation render.

A3 Continue conversation in same session
  - Evidence: ``POST /api/sessions/{id}/messages`` appends user + assistant into the same ``.jsonl``.

A4 New session creation
  - Evidence: ``POST /api/sessions`` + frontend New button.

A5 Editor supports multi-line paste + stable formatting
  - Evidence: CodeMirror 6 composer.

A6 Ctrl+F search works
  - Evidence: CodeMirror search extension + keybinding.

Executable Evidence
-------------------

- ``.agile/reports/evidence/S01/api_evidence.json``
- ``.agile/reports/evidence/S01/storage_files.txt``

Notes
-----

- LLM calls fall back to a clear message when Ollama env vars are not configured.
- Streaming is implemented with NDJSON (not SSE/WebSocket) for low complexity.
