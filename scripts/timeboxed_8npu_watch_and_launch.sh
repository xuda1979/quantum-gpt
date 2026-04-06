#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/timeboxed_8npu_watch_and_launch.sh --command "<cmd>" [--timeout-sec 7200] [--poll-sec 60] [--status-file <path>] [--launch-log <path>]

Waits until all 8 NPUs are idle, then launches the provided command.
Intended to run on ai2.
EOF
  exit 1
}

COMMAND=""
TIMEOUT_SEC=7200
POLL_SEC=60
STATUS_FILE="/tmp/timeboxed_8npu_watch_status.log"
LAUNCH_LOG="/tmp/timeboxed_8npu_launch.log"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --command)
      COMMAND="${2:-}"
      shift 2
      ;;
    --timeout-sec)
      TIMEOUT_SEC="${2:-}"
      shift 2
      ;;
    --poll-sec)
      POLL_SEC="${2:-}"
      shift 2
      ;;
    --status-file)
      STATUS_FILE="${2:-}"
      shift 2
      ;;
    --launch-log)
      LAUNCH_LOG="${2:-}"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

[[ -n "$COMMAND" ]] || usage

start_ts="$(date +%s)"
echo "$(date -Iseconds) waiting_for_8_idle_npus" >> "$STATUS_FILE"

while true; do
  now_ts="$(date +%s)"
  elapsed="$((now_ts - start_ts))"
  if [[ "$elapsed" -ge "$TIMEOUT_SEC" ]]; then
    echo "$(date -Iseconds) timeout_after_${elapsed}s" >> "$STATUS_FILE"
    exit 124
  fi

  idle_count="$(npu-smi info | grep -c 'No running processes found in NPU' || true)"
  if [[ "$idle_count" -ge 8 ]]; then
    echo "$(date -Iseconds) launch_start idle_count=${idle_count}" >> "$STATUS_FILE"
    nohup bash -lc "$COMMAND" > "$LAUNCH_LOG" 2>&1 < /dev/null &
    launch_pid="$!"
    echo "$(date -Iseconds) launch_pid=${launch_pid} launch_log=${LAUNCH_LOG}" >> "$STATUS_FILE"
    exit 0
  fi

  echo "$(date -Iseconds) still_waiting idle_count=${idle_count}" >> "$STATUS_FILE"
  sleep "$POLL_SEC"
done
