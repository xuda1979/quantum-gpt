#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${AGENTIC_DASHBOARD_HOST:-127.0.0.1}"
PORT="${AGENTIC_DASHBOARD_PORT:-8765}"
OUTPUTS_DIR="${AGENTIC_DASHBOARD_OUTPUTS_DIR:-$ROOT_DIR/outputs}"
OUTPUT_PATH="${AGENTIC_DASHBOARD_OUTPUT_PATH:-$ROOT_DIR/reports/agentic_training_dashboard.html}"
REGISTRY_PATH="${AGENTIC_DASHBOARD_REGISTRY_PATH:-$ROOT_DIR/reports/agentic_training_run_registry.json}"
HUANXIN_STATUS_PATH="${AGENTIC_DASHBOARD_HUANXIN_STATUS_PATH:-$ROOT_DIR/reports/huanxin_environment_status.json}"
LIMIT="${AGENTIC_DASHBOARD_LIMIT:-16}"
POLL_SECONDS="${AGENTIC_DASHBOARD_POLL_SECONDS:-10}"
REFRESH_HUANXIN_STATUS="${AGENTIC_DASHBOARD_REFRESH_HUANXIN_STATUS:-0}"
HUANXIN_ENVS="${AGENTIC_DASHBOARD_HUANXIN_ENVS:-}"
HUANXIN_REFRESH_SECONDS="${AGENTIC_DASHBOARD_HUANXIN_REFRESH_SECONDS:-120}"
HUANXIN_TIMEOUT_SEC="${AGENTIC_DASHBOARD_HUANXIN_TIMEOUT_SEC:-30}"

usage() {
  cat <<'EOF'
Usage:
  scripts/serve_agentic_training_dashboard.sh [--host <host>] [--port <port>] [--refresh-huanxin-status --huanxin-env <env>]

Serves the local agentic training dashboard and refreshes it on a timer.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --port)
      PORT="${2:-}"
      shift 2
      ;;
    --outputs-dir)
      OUTPUTS_DIR="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT_PATH="${2:-}"
      shift 2
      ;;
    --registry-output)
      REGISTRY_PATH="${2:-}"
      shift 2
      ;;
    --huanxin-status)
      HUANXIN_STATUS_PATH="${2:-}"
      shift 2
      ;;
    --limit)
      LIMIT="${2:-}"
      shift 2
      ;;
    --poll-seconds)
      POLL_SECONDS="${2:-}"
      shift 2
      ;;
    --refresh-huanxin-status)
      REFRESH_HUANXIN_STATUS=1
      shift
      ;;
    --huanxin-env)
      if [[ -n "$HUANXIN_ENVS" ]]; then
        HUANXIN_ENVS="${HUANXIN_ENVS},${2:-}"
      else
        HUANXIN_ENVS="${2:-}"
      fi
      shift 2
      ;;
    --huanxin-refresh-seconds)
      HUANXIN_REFRESH_SECONDS="${2:-}"
      shift 2
      ;;
    --huanxin-timeout-sec)
      HUANXIN_TIMEOUT_SEC="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

CMD=(
  python3
  scripts/serve_agentic_training_dashboard.py
  --host "$HOST"
  --port "$PORT"
  --outputs-dir "$OUTPUTS_DIR"
  --output "$OUTPUT_PATH"
  --registry-output "$REGISTRY_PATH"
  --huanxin-status "$HUANXIN_STATUS_PATH"
  --limit "$LIMIT"
  --poll-seconds "$POLL_SECONDS"
)

if [[ "$REFRESH_HUANXIN_STATUS" == "1" ]]; then
  CMD+=(--refresh-huanxin-status)
  IFS=',' read -r -a HUANXIN_ENV_ARRAY <<< "$HUANXIN_ENVS"
  if [[ "${#HUANXIN_ENV_ARRAY[@]}" -eq 0 || -z "${HUANXIN_ENV_ARRAY[0]:-}" ]]; then
    HUANXIN_ENV_ARRAY=(ASI1)
  fi
  for env_name in "${HUANXIN_ENV_ARRAY[@]}"; do
    [[ -n "$env_name" ]] && CMD+=(--huanxin-env "$env_name")
  done
  CMD+=(--huanxin-refresh-seconds "$HUANXIN_REFRESH_SECONDS")
  CMD+=(--huanxin-timeout-sec "$HUANXIN_TIMEOUT_SEC")
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
