Commands
========

Execution command:
- EXECUTE SPRINT <SPRINT-ID>

IDs:
- ARC-000 / ARC-010 / ...
- <ARC-ID>-SPRINT-YYYYMMDD-XX

Chat tool commands
------------------

Inside the composer message, the following slash commands are handled directly by the server:

- ``/read <relative-path>``
  - Read a UTF-8 file from the current workspace.
- ``/write <relative-path> <content>``
  - Write content to a file in the current workspace (creates parent folders if needed).
- ``/sh <command>``
  - Execute a shell command in the current workspace and return exit code/stdout/stderr.

Notes:
- Paths are restricted to the current workspace (no absolute paths, no ``..`` escape).
- Tool errors are returned in-chat as assistant messages with ``(tool error)`` prefix.
