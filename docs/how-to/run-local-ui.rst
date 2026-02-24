Run the Local UI
===============

This project serves a simple web UI from a Python process.

Steps
-----

1. Install in editable mode::

   pip install -e .

2. Start the UI from your workspace directory::

   cd /path/to/your/project
   lamecoder ui

3. Open the printed URL in your browser.

Optional: Use Ollama
--------------------

If you have an OpenAI-compatible Ollama endpoint, set::

   export LAMECODER_OLLAMA_BASE_URL=http://127.0.0.1:11434
   export LAMECODER_MODEL=qwen2.5-coder:7b

The server will then call ``/v1/chat/completions``.
