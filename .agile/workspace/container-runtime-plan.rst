Epic: Container Runtime Testing for ARC-001
  Containerize the LameCoder server + test suite so local developers can run builds and verification inside a disposable image that mounts the current workspace.

Story: Build reproducible container image
  Acceptance criteria:
    - Given the repo defines its Python dependencies in `pyproject.toml`, when we build the new `Dockerfile` image, then the build completes with all `fastapi`, `uvicorn`, `pydantic`, and `httpx` packages installed and an entrypoint that can run `lamecoder ui`.
    - Given the image exists, when we start the container pointing at a workspace-mounted `/workspace`, then hitting `/api/health` should report the same path and return `ok: True`.
  Tasks:
    1. Add a Dockerfile that sets Python 3.11+, installs dependencies, copies `src/`, `tests/`, and exposes `lamecoder` in PATH.
    2. Add a shell script (or `docker-compose` service) that accepts `--target tests` to run `pytest` inside the container using the mounted workspace.
    3. Validate health endpoint by running the container locally and hitting `/api/health` via `curl` from the host.

Story: Persist session storage through volume mounts
  Acceptance criteria:
    - Given `.lame/` is mounted from the host, when the FastAPI server under test writes sessions, then the host filesystem shows new `.lame/sessions/index.json` and message files.
    - Given the playback tests run inside the image, when `pytest tests/test_store.py` executes, then it succeeds and the temporary `.lame/` artifacts remain accessible on the host to inspect.
  Tasks:
    1. Document or script the recommended `docker run` flags for mounting the current directory and exposing ports (e.g., `-v $(pwd):/workspace -w /workspace`).
    2. Ensure `store.workspace_root()` respects environment variables (if needed) so the container uses `/workspace/.lame/` and the host sees the same files.
    3. Add helper in tests (or a new module) that can optionally detect the container environment to clean up or assert storage behavior.

Story: Capture container testing workflow in docs
  Acceptance criteria:
    - Given a developer reads the sprint plan, when they follow the documented steps, then they can rebuild the image (`docker build`), run the test suite (`docker run ... pytest`), and start the UI (`docker run ... lamecoder ui`).
    - Given the instructions describe the goal, when they execute the commands, then they can confirm `http://127.0.0.1:<port>` is reachable and the server reports `ok: True` on `/api/health`.
  Tasks:
    1. Create or extend a `docs/how-to/container-runtime.rst` (or similar) describing the build/run/test loop and how to pass in environment variables (OLLAMA settings, ports, volumes).
    2. Update `README.md` to mention the container workflow for testing, linking to the detailed how-to.
    3. Note any additional prerequisites (Docker Engine, environment variables) and how to clean up the container artifacts.
