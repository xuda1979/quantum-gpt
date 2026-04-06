#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/timeboxed_8npu_pipeline.sh --sft-command "<cmd>" --grpo-command "<cmd>" [--timeout-sec 7200] [--poll-sec 60] [--status-file <path>] [--sft-log <path>] [--grpo-log <path>]

Waits for all 8 NPUs to become idle, then runs the SFT command followed by
the GRPO command under one shared wall-clock budget.
Intended to run on ai2.
EOF
  exit 1
}

SFT_COMMAND=""
GRPO_COMMAND=""
TIMEOUT_SEC=7200
POLL_SEC=60
STATUS_FILE="/tmp/timeboxed_8npu_pipeline_status.log"
SFT_LOG="/tmp/timeboxed_8npu_sft.log"
GRPO_LOG="/tmp/timeboxed_8npu_grpo.log"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sft-command)
      SFT_COMMAND="${2:-}"
      shift 2
      ;;
    --grpo-command)
      GRPO_COMMAND="${2:-}"
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
    --sft-log)
      SFT_LOG="${2:-}"
      shift 2
      ;;
    --grpo-log)
      GRPO_LOG="${2:-}"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

[[ -n "$SFT_COMMAND" ]] || usage
[[ -n "$GRPO_COMMAND" ]] || usage

start_ts="$(date +%s)"
echo "$(date -Iseconds) pipeline_waiting_for_8_idle_npus" >> "$STATUS_FILE"

wait_for_idle() {
  while true; do
    now_ts="$(date +%s)"
    elapsed="$((now_ts - start_ts))"
    if [[ "$elapsed" -ge "$TIMEOUT_SEC" ]]; then
      echo "$(date -Iseconds) timeout_before_launch elapsed=${elapsed}s" >> "$STATUS_FILE"
      return 124
    fi
    idle_count="$(npu-smi info | grep -c 'No running processes found in NPU' || true)"
    if [[ "$idle_count" -ge 8 ]]; then
      echo "$(date -Iseconds) all_8_idle elapsed=${elapsed}s" >> "$STATUS_FILE"
      return 0
    fi
    echo "$(date -Iseconds) still_waiting idle_count=${idle_count} elapsed=${elapsed}s" >> "$STATUS_FILE"
    sleep "$POLL_SEC"
  done
}

run_stage() {
  local stage_name="$1"
  local command_text="$2"
  local log_path="$3"
  local now_ts elapsed remaining

  now_ts="$(date +%s)"
  elapsed="$((now_ts - start_ts))"
  remaining="$((TIMEOUT_SEC - elapsed))"
  if [[ "$remaining" -le 0 ]]; then
    echo "$(date -Iseconds) no_budget_remaining_before_${stage_name}" >> "$STATUS_FILE"
    return 124
  fi

  echo "$(date -Iseconds) ${stage_name}_start remaining=${remaining}s log=${log_path}" >> "$STATUS_FILE"
  if ! timeout "$remaining" bash -lc "$command_text" > "$log_path" 2>&1; then
    local rc=$?
    echo "$(date -Iseconds) ${stage_name}_failed rc=${rc}" >> "$STATUS_FILE"
    return "$rc"
  fi
  echo "$(date -Iseconds) ${stage_name}_done" >> "$STATUS_FILE"
}

wait_for_idle
run_stage sft "$SFT_COMMAND" "$SFT_LOG"
run_stage grpo "$GRPO_COMMAND" "$GRPO_LOG"
echo "$(date -Iseconds) pipeline_done" >> "$STATUS_FILE"
