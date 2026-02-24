Architecture (Sprint S01)
========================

Overview
--------

The UI is a static frontend (HTML/CSS/JS) served by a FastAPI backend.

- Backend responsibilities:

  - Persist sessions/messages under ``.lame/`` (workspace = current directory)
  - Provide REST endpoints for session list/create/read and message append
  - Optionally call an OpenAI-compatible local model endpoint (Ollama)

- Frontend responsibilities:

  - Session picker sidebar
  - Conversation viewer
  - CodeMirror-based composer/editor with shortcuts and search

Streaming
---------

Message sending supports a simple NDJSON stream:

- Server returns ``application/x-ndjson``.
- Client reads lines and applies ``delta`` updates to the last assistant message.

This avoids a heavier SSE/WebSocket implementation while still feeling responsive.
