ARC-001: Session UX + Cakep Editor
=================================

Vision
------

Deliver a local-first coding agent UI that feels like a product:

- Persistent sessions stored inside the current workspace (``.lame/``)
- Session picker + conversation viewer
- A modern, comfortable text editor/composer

Goals
-----

1. Select a session, view its conversation, and continue it.
2. Provide a "cakep" editor (line numbers, syntax highlighting, search, shortcuts).

Constraints
-----------

- No diff viewer in this arc.
- Workspace = current directory where the command is executed.
- Persist all UI data under ``.lame/``.

Success Signals
---------------

- Restarting the server does not lose sessions or conversations.
- Switching sessions is instant and does not mix messages.
- Copy/paste of multi-line code in the composer is stable.
