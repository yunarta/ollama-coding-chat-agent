Storage Layout
==============

LameCoder stores all UI/session data inside the current directory in ``.lame/``.

::

   .lame/
     sessions/
       index.json
       <session_id>.jsonl

Files
-----

``index.json``
  Session metadata list (title, timestamps, snippet, pinned). Includes a schema ``version``.

``<session_id>.jsonl``
  Append-only message log. Each line is a JSON object with at least:

  - ``id``
  - ``role`` (user/assistant/tool/system)
  - ``content``
  - ``created_at``
