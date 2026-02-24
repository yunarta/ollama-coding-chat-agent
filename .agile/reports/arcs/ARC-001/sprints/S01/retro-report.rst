Retro Report: Sprint S01
=======================

What Went Well
--------------

- Session persistence is simple (index.json + jsonl) and robust.
- NDJSON streaming gives a "live" feel without complex protocols.
- CodeMirror 6 provides a modern composer with minimal UI code.

What Was Painful
----------------

- File locking libraries add dependency weight; implemented a POSIX lock fallback.
- CDN-based frontend dependencies are convenient but not fully offline.

Next Improvements
-----------------

1. Optional offline bundling for CodeMirror (esbuild into static assets).
2. Workspace guardrails: allowlist shell commands and enforce path boundaries.
3. Add export-to-markdown for sessions (useful for tickets/PRs).
