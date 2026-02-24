#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_container_common.sh"

require_cmd act
require_cmd podman

ROOT="$(repo_root)"
JOB_NAME="${JOB_NAME:-container-runtime}"
ACT_IMAGE="${ACT_IMAGE:-catthehacker/ubuntu:act-latest}"
SOCKET_PATH="${PODMAN_ACT_SOCKET:-/tmp/podman-act.sock}"
PODMAN_LOG="${PODMAN_ACT_LOG:-/tmp/podman-act.log}"

service_pid=""
cleanup() {
  if [[ -n "${service_pid}" ]]; then
    kill "${service_pid}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${tmp_docker_config:-}" ]]; then
    rm -rf "${tmp_docker_config}"
  fi
}
trap cleanup EXIT

if [[ ! -S "${SOCKET_PATH}" ]]; then
  rm -f "${SOCKET_PATH}"
  nohup podman system service --time=0 "unix://${SOCKET_PATH}" >"${PODMAN_LOG}" 2>&1 &
  service_pid="$!"
  sleep 1
fi

if [[ ! -S "${SOCKET_PATH}" ]]; then
  echo "Podman socket not available at ${SOCKET_PATH}" >&2
  exit 1
fi

tmp_docker_config="$(mktemp -d)"
printf '{}' > "${tmp_docker_config}/config.json"

echo "[act] repo=${ROOT}"
echo "[act] job=${JOB_NAME}"
echo "[act] socket=${SOCKET_PATH}"
echo "[act] image=${ACT_IMAGE}"

(
  cd "${ROOT}"
  DOCKER_CONFIG="${tmp_docker_config}" \
  DOCKER_HOST="unix://${SOCKET_PATH}" \
  act -j "${JOB_NAME}" \
    --container-daemon-socket "unix://${SOCKET_PATH}" \
    -P "ubuntu-latest=${ACT_IMAGE}"
)
