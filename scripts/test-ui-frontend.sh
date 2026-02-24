#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_container_common.sh"

require_cmd curl
require_cmd node
require_cmd npm

ENGINE="$(detect_container_engine)"
ROOT="$(repo_root)"
CONTAINER_NAME="${CONTAINER_NAME:-lamecoder-ui}"
HOST_PORT="${HOST_PORT:-8080}"
SKIP_BUILD="${SKIP_BUILD:-0}"
KEEP_CONTAINER="${KEEP_CONTAINER:-0}"
KEEP_TEST_DEPS="${KEEP_TEST_DEPS:-1}"
PLAYWRIGHT_DIR="${PLAYWRIGHT_DIR:-${TMPDIR:-/tmp}/lamecoder-playwright-smoke}"
PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.52.0}"

cleanup() {
  if [[ "${KEEP_CONTAINER}" != "1" ]]; then
    "${ENGINE}" rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
  fi
  if [[ "${KEEP_TEST_DEPS}" != "1" ]]; then
    rm -rf "${PLAYWRIGHT_DIR}"
  fi
}
trap cleanup EXIT

echo "[ui-frontend] starting app container"
DETACH=1 \
SKIP_BUILD="${SKIP_BUILD}" \
CONTAINER_NAME="${CONTAINER_NAME}" \
HOST_PORT="${HOST_PORT}" \
"${SCRIPT_DIR}/run-ui-container.sh" >/tmp/lamecoder-ui-run.log
cat /tmp/lamecoder-ui-run.log
rm -f /tmp/lamecoder-ui-run.log

BASE_URL="http://127.0.0.1:${HOST_PORT}"
wait_for_http "${BASE_URL}/api/health" 25
echo "[ui-frontend] health ok: ${BASE_URL}/api/health"

mkdir -p "${PLAYWRIGHT_DIR}"
if [[ ! -f "${PLAYWRIGHT_DIR}/package.json" ]]; then
  (cd "${PLAYWRIGHT_DIR}" && npm init -y >/dev/null)
fi

if [[ ! -d "${PLAYWRIGHT_DIR}/node_modules/playwright" ]]; then
  echo "[ui-frontend] installing playwright@${PLAYWRIGHT_VERSION}"
  (cd "${PLAYWRIGHT_DIR}" && npm install "playwright@${PLAYWRIGHT_VERSION}")
fi

if [[ ! -d "${HOME}/.cache/ms-playwright" ]]; then
  echo "[ui-frontend] installing Chromium runtime"
  (cd "${PLAYWRIGHT_DIR}" && npx playwright install chromium)
fi

echo "[ui-frontend] running headless UI smoke"
NODE_PATH="${PLAYWRIGHT_DIR}/node_modules" \
UI_BASE_URL="${BASE_URL}" \
node "${SCRIPT_DIR}/ui-smoke-playwright.cjs"

echo "[ui-frontend] done"
if [[ "${KEEP_CONTAINER}" == "1" ]]; then
  echo "[ui-frontend] container kept running: ${CONTAINER_NAME}"
fi
