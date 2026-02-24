#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_container_common.sh"

ENGINE="$(detect_container_engine)"
ROOT="$(repo_root)"
IMAGE_NAME="${IMAGE_NAME:-lamecoder-ci:local}"
build_args=()

if [[ "${ENGINE}" == "podman" ]]; then
  # WSL/rootless podman often lacks a user systemd session; cgroupfs is more portable here.
  build_args+=(--cgroup-manager=cgroupfs)
fi

echo "[build] engine=${ENGINE}"
echo "[build] image=${IMAGE_NAME}"
echo "[build] context=${ROOT}"
"${ENGINE}" build "${build_args[@]}" -t "${IMAGE_NAME}" "${ROOT}"
echo "[build] done"
