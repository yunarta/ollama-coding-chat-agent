#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_container_common.sh"

require_cmd curl

ENGINE="$(detect_container_engine)"
ROOT="$(repo_root)"
IMAGE_NAME="${IMAGE_NAME:-lamecoder-ci:local}"
CONTAINER_NAME="${CONTAINER_NAME:-lamecoder-ui}"
WORKSPACE_DIR="${WORKSPACE_DIR:-$ROOT}"
LAMECODER_MODEL="${LAMECODER_MODEL:-$(default_ollama_model)}"
LAMECODER_OLLAMA_BASE_URL="${LAMECODER_OLLAMA_BASE_URL:-$(default_ollama_base_url)}"
NETWORK_MODE="${CONTAINER_NETWORK_MODE:-auto}"
HOST_PORT="${HOST_PORT:-8080}"
DETACH="${DETACH:-0}"
SKIP_BUILD="${SKIP_BUILD:-0}"

if [[ "${SKIP_BUILD}" != "1" ]]; then
  IMAGE_NAME="${IMAGE_NAME}" CONTAINER_ENGINE="${ENGINE}" "${SCRIPT_DIR}/build-image.sh"
fi

run_args=(
  run --rm
  --name "${CONTAINER_NAME}"
  -e "LAMECODER_OLLAMA_BASE_URL=${LAMECODER_OLLAMA_BASE_URL}"
  -e "LAMECODER_MODEL=${LAMECODER_MODEL}"
  -v "${WORKSPACE_DIR}:/workspace"
  -w /workspace
)

effective_network="${NETWORK_MODE}"
if [[ "${NETWORK_MODE}" == "auto" ]]; then
  if [[ "${ENGINE}" == "podman" ]]; then
    effective_network="host"
  else
    effective_network="bridge"
  fi
fi

if [[ "${effective_network}" == "host" ]]; then
  run_args+=(--network host)
  HOST_PORT="8080"
else
  run_args+=(-p "${HOST_PORT}:8080")
fi

if [[ "${DETACH}" == "1" ]]; then
  run_args+=(-d)
fi

echo "[run] engine=${ENGINE}"
echo "[run] image=${IMAGE_NAME}"
echo "[run] container=${CONTAINER_NAME}"
echo "[run] workspace=${WORKSPACE_DIR}"
echo "[run] ollama=${LAMECODER_OLLAMA_BASE_URL}"
echo "[run] model=${LAMECODER_MODEL}"
echo "[run] network=${effective_network}"
echo "[run] url=http://127.0.0.1:${HOST_PORT}"

"${ENGINE}" rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
"${ENGINE}" "${run_args[@]}" "${IMAGE_NAME}"
