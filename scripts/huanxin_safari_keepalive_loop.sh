#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEEPALIVE_SCRIPT="$ROOT_DIR/scripts/huanxin_safari_keepalive.sh"
INTERVAL_SEC="${HUANXIN_KEEPALIVE_INTERVAL_SEC:-240}"
PID_FILE="${HUANXIN_KEEPALIVE_PID_FILE:-/tmp/huanxin-safari-keepalive.pid}"
LOG_FILE="${HUANXIN_KEEPALIVE_LOG_FILE:-/tmp/huanxin-safari-keepalive.log}"
ONCE=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_safari_keepalive_loop.sh [--once]

Runs the existing Safari Huanxin train-dev tab keepalive on an interval without
opening a new page. The loop can be stopped with:
  kill "$(cat /tmp/huanxin-safari-keepalive.pid)"
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --once)
      ONCE=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

run_keepalive() {
  local timestamp output status
  timestamp="$(date '+%Y-%m-%dT%H:%M:%S%z')"
  if output="$(bash "$KEEPALIVE_SCRIPT" --refresh 2>&1)"; then
    status="ok"
  else
    status="failed"
  fi
  printf '[%s] %s %s\n' "$timestamp" "$status" "$output" | tee -a "$LOG_FILE"
  [[ "$status" == "ok" ]]
}

if [[ "$ONCE" -eq 1 ]]; then
  run_keepalive
  exit $?
fi

if [[ -f "$PID_FILE" ]]; then
  existing_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "${existing_pid:-}" ]] && kill -0 "$existing_pid" 2>/dev/null; then
    echo "keepalive loop already running with PID $existing_pid" >&2
    exit 0
  fi
fi

printf '%s' "$$" > "$PID_FILE"
trap 'rm -f "$PID_FILE"' EXIT

while true; do
  run_keepalive || true
  sleep "$INTERVAL_SEC"
done
