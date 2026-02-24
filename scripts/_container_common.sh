#!/usr/bin/env bash
set -euo pipefail

repo_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

detect_container_engine() {
  if [[ -n "${CONTAINER_ENGINE:-}" ]]; then
    echo "$CONTAINER_ENGINE"
    return 0
  fi
  if command -v podman >/dev/null 2>&1; then
    echo "podman"
    return 0
  fi
  if command -v docker >/dev/null 2>&1; then
    echo "docker"
    return 0
  fi
  echo "No container engine found (docker/podman)." >&2
  return 1
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

default_ollama_base_url() {
  local scheme host
  scheme="${OLLAMA_SCHEME:-http}"
  host="${OLLAMA_HOST:-ollama.mobilesolutionworks.com}"
  echo "${scheme}://${host}:11434"
}

default_ollama_model() {
  echo "${OLLAMA_MODEL_DEFAULT:-qwen2.5:7b}"
}

wait_for_http() {
  local url="$1"
  local timeout="${2:-20}"
  local i
  for ((i=1; i<=timeout; i++)); do
    if curl -fsS "$url" >/dev/null; then
      return 0
    fi
    sleep 1
  done
  echo "Timed out waiting for $url" >&2
  return 1
}
