#!/usr/bin/env bash
# =============================================================================
# FV-GSPO repair sidecar: continuously convert the trainer's repair queue into
# verified SFT/DPO positives (writes repair_converted.jsonl).
#
# Why: the trainer's `all_fail_without_repair` circuit breaker trips (halting
# the run) when all-fail rollouts accumulate without ANY repair conversion.
# The conversion feed is written by scripts/fv_gspo_repair_stage.py, which was
# never launched in-loop: runs stopped at step ~40 with repair_converted.jsonl
# never written (diagnosed 2026-08-19). This sidecar polls the queue the
# trainer writes (repair_queue.jsonl) and runs the stage (CPU-only, dedupes by
# record dedup_key) so conversions keep flowing and unblock the breaker.
#
# Usage (normally spawned by asi2_launch_grpo_27b_selfeval.sh):
#   bash scripts/fv_gspo_repair_sidecar.sh <run-output-dir>
#
# Env:
#   REPAIR_POLL_SECONDS   poll interval (default 600)
#   REPAIR_LIMIT          records per run (default 20)
# =============================================================================
set -euo pipefail

SCRIPT_NAME="fv_gspo_repair_sidecar"
export TZ="${TZ:-Asia/Shanghai}"

log() { printf '[%s] [%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$SCRIPT_NAME" "$*"; }

OUT="${1:?usage: fv_gspo_repair_sidecar.sh <run-output-dir>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE="$OUT/repair_queue.jsonl"
STAGE_OUT="$OUT/repair_stage"
TASKS_DIR="${FV_GSPO_TASKS_DIR:-$REPO_ROOT/evals/tasks}"
POLL_SECONDS="${REPAIR_POLL_SECONDS:-600}"
LIMIT="${REPAIR_LIMIT:-20}"
TEACHER_CMD="${FV_GSPO_TEACHER_CMD:-}"
PID_FILE="${REPAIR_PID_FILE:-$OUT/repair_sidecar.pid}"

echo "$$" > "$PID_FILE"
trap 'rm -f "$PID_FILE"; exit 0' TERM INT

log "repair sidecar started: queue=$QUEUE stage_out=$STAGE_OUT poll=${POLL_SECONDS}s limit=$LIMIT"

while true; do
  if [[ -s "$QUEUE" ]]; then
    args=(--queue "$QUEUE" --tasks-dir "$TASKS_DIR" --output "$STAGE_OUT" --limit "$LIMIT")
    if [[ -n "$TEACHER_CMD" ]]; then
      args+=(--teacher-command "$TEACHER_CMD")
    fi
    log "running repair stage (queue size $(wc -l < "$QUEUE" 2>/dev/null || echo 0))..."
    if python3 "$REPO_ROOT/scripts/fv_gspo_repair_stage.py" "${args[@]}"; then
      log "repair stage pass; converted=$(grep -c . "$STAGE_OUT/repair_converted.jsonl" 2>/dev/null || echo 0)"
    else
      log "repair stage failed (exit $?); will retry next poll"
    fi
  else
    log "no repair queue yet; waiting"
  fi
  sleep "$POLL_SECONDS"
done
