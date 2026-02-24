# Scripts

Utility scripts for local container testing and `act` execution.

## Quick start

Build image:

```bash
scripts/build-image.sh
```

Run UI container (defaults to `http://ollama.mobilesolutionworks.com:11434` and `qwen2.5:7b`):

```bash
scripts/run-ui-container.sh
```

Persona A smoke test (build + run + create session + send prompt):

```bash
scripts/test-persona-a.sh
```

Frontend UI smoke test (real headless browser; opens page and sends via UI):

```bash
SKIP_BUILD=1 scripts/test-ui-frontend.sh
```

Run GitHub Action locally via `act` + Podman socket:

```bash
scripts/run-act-container-ci.sh
```

## Useful env vars

- `CONTAINER_ENGINE=docker|podman`
- `IMAGE_NAME=lamecoder-ci:local`
- `LAMECODER_OLLAMA_BASE_URL=http://ollama.mobilesolutionworks.com:11434`
- `LAMECODER_MODEL=qwen2.5:7b`
- `CONTAINER_NETWORK_MODE=host|bridge|auto`
- `SKIP_BUILD=1`
- `KEEP_CONTAINER=1` (for `test-persona-a.sh`)
- `KEEP_CONTAINER=1` (for `test-ui-frontend.sh`)
- `PLAYWRIGHT_DIR=/tmp/lamecoder-playwright-smoke`
- `PLAYWRIGHT_VERSION=1.52.0`
- `KEEP_TEST_DEPS=0` (delete temporary Playwright install after `test-ui-frontend.sh`)
