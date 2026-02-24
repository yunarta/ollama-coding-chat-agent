# LameCoder (Sprint S01 demo)

Local-first coding agent web UI with persistent sessions stored in `.lame/` (current working directory).

## Install (editable)

```bash
pip install -e .
```

## Run

```bash
cd /path/to/your/workspace
lamecoder ui
```

It will print a URL like `http://127.0.0.1:51623`.

## Configure Ollama (optional)

By default the server replies with a stub response.

Set these env vars to use an OpenAI-compatible Ollama endpoint:

```bash
export LAMECODER_OLLAMA_BASE_URL=http://127.0.0.1:11434
export LAMECODER_MODEL=qwen2.5-coder:7b
```

## Storage layout

```
.lame/
  sessions/
    index.json
    <session_id>.jsonl
```

