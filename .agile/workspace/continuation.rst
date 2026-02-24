What: Continued UI-focused sprint work with real headless browser testing (Playwright + Chromium) against the containerized app, validating frontend send-message behavior directly.
Finding: Frontend send failure was reproduced because the editor never mounted (`.cm-content` missing) while API/backend remained healthy.
Root cause 1: `@codemirror/theme-one-dark@6.2.0` import from esm.sh returned 404; patched to `6.1.2`.
Root cause 2: CodeMirror CDN modules still load mixed `@codemirror/state` instances on esm.sh, causing `Unrecognized extension value` during `EditorState.create()`.
Fix: Added runtime editor adapter + textarea fallback so UI remains usable when CodeMirror init fails; send flow, draft save/load, and Ctrl/Cmd+Enter work through the same `editor.getText()/setText()` interface.
Demo: Headless UI smoke test succeeded (`editorMode=fallback-textarea`, `lastAssistant="OK frontend"`, message stream endpoint 200), proving frontend Send works end-to-end without manual BO testing.
What: Also simplified CodeMirror extension set to reduce external mismatch surface, but CDN instance-mismatch still persists and triggers fallback.
Risk: Rich CodeMirror editor is still degraded; current UX is functional via fallback textarea rather than the intended CodeMirror experience.
Next: Next sprint should stabilize CodeMirror imports (single bundled source / local vendor bundle) and add a committed Playwright smoke test script/workflow for UI regressions.
What: Added committed frontend smoke tooling (`scripts/test-ui-frontend.sh` + `scripts/ui-smoke-playwright.cjs`) so UI can be tested headlessly by script, not manual clicks.
Fix: Made `scripts/run-ui-container.sh` idempotent by removing an existing container name before `run`, preventing repeat-run failures during demos.
Demo: Ran `SKIP_BUILD=1 scripts/test-ui-frontend.sh` successfully; Playwright opened the containerized UI, sent a message via frontend button, and received assistant response `OK`.
Evidence: Script captured API 200 on `/api/sessions/.../messages?stream=true` and frontend state (`lastUser`, `lastAssistant`) from DOM after send.
Status: UI send flow is proven working end-to-end from the browser, currently via textarea fallback (`editorMode=fallback-textarea`) while CodeMirror CDN mismatch remains a non-blocking UX degradation.
What: Continued next sprint work to remove the UI degradation and restore rich editor behavior.
Fix: Eliminated the direct `@codemirror/state` import and let `EditorView` construct state from the same package instance, avoiding the `instanceof` mismatch from esm.sh mixed module copies.
Demo: Rebuilt container image and reran `SKIP_BUILD=1 scripts/test-ui-frontend.sh`; headless Playwright now reports `editorMode=codemirror`, successful frontend send, and assistant reply `OK`.
Status: UI send flow is now verified end-to-end through the intended CodeMirror editor (not fallback) in the containerized app.
