#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_container_common.sh"

require_cmd curl
require_cmd python3

ENGINE="$(detect_container_engine)"
ROOT="$(repo_root)"
IMAGE_NAME="${IMAGE_NAME:-lamecoder-ci:local}"
CONTAINER_NAME="${CONTAINER_NAME:-lamecoder-persona-a}"
WORKSPACE_DIR="${WORKSPACE_DIR:-$ROOT}"
LAMECODER_MODEL="${LAMECODER_MODEL:-$(default_ollama_model)}"
LAMECODER_OLLAMA_BASE_URL="${LAMECODER_OLLAMA_BASE_URL:-$(default_ollama_base_url)}"
SKIP_BUILD="${SKIP_BUILD:-0}"
KEEP_CONTAINER="${KEEP_CONTAINER:-0}"
NETWORK_MODE="${CONTAINER_NETWORK_MODE:-auto}"
HOST_PORT="${HOST_PORT:-8080}"

cleanup() {
  if [[ "${KEEP_CONTAINER}" == "1" ]]; then
    return 0
  fi
  "${ENGINE}" rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

if [[ "${SKIP_BUILD}" != "1" ]]; then
  IMAGE_NAME="${IMAGE_NAME}" CONTAINER_ENGINE="${ENGINE}" "${SCRIPT_DIR}/build-image.sh"
fi

effective_network="${NETWORK_MODE}"
if [[ "${NETWORK_MODE}" == "auto" ]]; then
  if [[ "${ENGINE}" == "podman" ]]; then
    effective_network="host"
  else
    effective_network="bridge"
  fi
fi

run_args=(
  run -d --rm
  --name "${CONTAINER_NAME}"
  -e "LAMECODER_OLLAMA_BASE_URL=${LAMECODER_OLLAMA_BASE_URL}"
  -e "LAMECODER_MODEL=${LAMECODER_MODEL}"
  -v "${WORKSPACE_DIR}:/workspace"
  -w /workspace
)
if [[ "${effective_network}" == "host" ]]; then
  run_args+=(--network host)
  HOST_PORT="8080"
else
  run_args+=(-p "${HOST_PORT}:8080")
fi

echo "[persona-a] starting container"
echo "[persona-a] engine=${ENGINE} image=${IMAGE_NAME} network=${effective_network}"
echo "[persona-a] ollama=${LAMECODER_OLLAMA_BASE_URL} model=${LAMECODER_MODEL}"
"${ENGINE}" rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
cid="$("${ENGINE}" "${run_args[@]}" "${IMAGE_NAME}")"
echo "[persona-a] container_id=${cid}"

base_url="http://127.0.0.1:${HOST_PORT}"
wait_for_http "${base_url}/api/health" 20

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"; cleanup' EXIT

echo "[persona-a] health"
curl -fsS "${base_url}/api/health" | tee "${tmpdir}/health.json"
echo

echo "[persona-a] create session"
curl -fsS \
  -X POST "${base_url}/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{"title":"Persona A smoke test"}' \
  | tee "${tmpdir}/create.json"
echo

session_id="$(python3 - "${tmpdir}/create.json" <<'PY'
import json, sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    print(json.load(f)["session"]["id"])
PY
)"

cat > "${tmpdir}/message.json" <<'EOF'
{"content":"Persona A test: kamu adalah reviewer backend senior yang galak tapi fair. Review pendek ide fitur \"export session ke markdown\". Balas dalam 4 bullet: risiko, desain API, test cases, keputusan go/no-go."}
EOF

echo "[persona-a] post message to /api/sessions/${session_id}/messages"
curl -fsS \
  -X POST "${base_url}/api/sessions/${session_id}/messages?stream=false" \
  -H "Content-Type: application/json" \
  --data @"${tmpdir}/message.json" \
  | tee "${tmpdir}/reply.json"
echo

echo "[persona-a] assistant reply"
python3 - "${tmpdir}/reply.json" <<'PY'
import json, sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
assistant = data.get("assistant", {})
print(assistant.get("content", ""))
PY

echo "[persona-a] host session files (${WORKSPACE_DIR}/.lame/sessions)"
ls -la "${WORKSPACE_DIR}/.lame/sessions" || true

echo "[persona-a] done"
if [[ "${KEEP_CONTAINER}" == "1" ]]; then
  echo "[persona-a] container kept running: ${CONTAINER_NAME}"
fi
