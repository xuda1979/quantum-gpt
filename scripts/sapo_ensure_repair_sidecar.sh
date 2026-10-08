#!/usr/bin/env bash
# =============================================================================
# Repair-sidecar boot guard (guardian alarm 8, 2026-08-26).
#
# Defect class: the repair sidecar died SILENTLY at launch (SIGKILL from
# box-prep cleanup loops is untrappable; the log froze right after the startup
# line), the repair queue starved, and the all_fail_without_repair breaker
# stopped runs 11 and 12 with no operator-visible cause.
#
# This script makes the class extinct as a SILENT failure: at boot (launcher)
# and any time ops/lanes run it, it checks pidfile + log-heartbeat liveness
# (shared logic: training/sidecar_liveness.py). Alive -> no-op with a
# SIDECAR_ALIVE line. Dead/missing/stale -> LOUD SIDECAR_DEAD_ALARM line and
# an idempotent relaunch via nohup (the same spawn that survives the daemon
# transport — proven by the run-5 sidecar surviving for hours).
#
# Usage (normally called by asi3_launch_grpo_direct.sh at boot):
#   bash scripts/sapo_ensure_repair_sidecar.sh <run-output-dir> [logdir]
#
# Env:
#   REPAIR_POLL_SECONDS   sidecar poll interval (default 60)
#   REPAIR_LIMIT          sidecar records-per-run cap (default 20)
#   MAX_SIDECAR_LOG_AGE   heartbeat staleness limit in seconds (default 300)
# =============================================================================
set -euo pipefail

OUT="${1:?usage: sapo_ensure_repair_sidecar.sh <run-output-dir> [logdir]}"
LOGDIR="${2:-${REPAIR_LOGDIR:-logs/sapo_27b_ai}}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() { printf '[%s] [sapo_ensure_repair_sidecar] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*"; }

RUN_NAME="$(basename "$OUT")"
RUN_ID="$RUN_NAME"
for prefix in sapo-27b-ai- grpo-27b-selfeval- sapo-27b-asi3-; do
  case "$RUN_NAME" in
    "$prefix"*) RUN_ID="${RUN_NAME#"$prefix"}"; break ;;
  esac
done

PID_FILE="$OUT/repair_sidecar.pid"
SIDE_LOG="$LOGDIR/repair_sidecar_${RUN_ID}.log"
mkdir -p "$LOGDIR"

STATUS="$(python3 "$REPO_ROOT/training/sidecar_liveness.py" \
  --pidfile "$PID_FILE" --log "$SIDE_LOG" \
  --max-age "${MAX_SIDECAR_LOG_AGE:-300}" 2>/dev/null || true)"

if [[ -z "$STATUS" ]]; then
  log "SIDECAR_LIVENESS_UNKNOWN: liveness CLI failed for pidfile=$PID_FILE log=$SIDE_LOG; not relaunching (avoid double-spawn)"
  exit 0
fi

ALIVE="$(printf '%s' "$STATUS" | python3 -c "import json,sys; print(json.load(sys.stdin).get('alive', False))" 2>/dev/null || echo false)"

if [[ "$ALIVE" == "True" ]]; then
  log "SIDECAR_ALIVE: pidfile=$PID_FILE log=$SIDE_LOG"
  exit 0
fi

log "SIDECAR_DEAD_ALARM: $(printf '%s' "$STATUS" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('status'), d.get('alarm_reason') or '')" 2>/dev/null || echo "status parse failed")"
log "SIDECAR_DEAD_ALARM: relaunching repair sidecar for $OUT (log=$SIDE_LOG poll=${REPAIR_POLL_SECONDS:-60}s)"

rm -f "$PID_FILE"
export REPAIR_POLL_SECONDS="${REPAIR_POLL_SECONDS:-60}"
export REPAIR_LIMIT="${REPAIR_LIMIT:-20}"
nohup bash "$REPO_ROOT/scripts/fv_gspo_repair_sidecar.sh" "$OUT" \
  >> "$SIDE_LOG" 2>&1 &
NEW_PID=$!
disown "$NEW_PID" 2>/dev/null || true
echo "$NEW_PID" > "$PID_FILE"
sleep 2
if kill -0 "$NEW_PID" 2>/dev/null; then
  log "SIDECAR_RELAUNCHED: pid=$NEW_PID pidfile=$PID_FILE"
else
  log "SIDECAR_RELAUNCH_FAILED: pid=$NEW_PID died within 2s of spawn — investigate launcher/box cleanup loops (kill -KILL on fv_gspo_repair_sidecar is the known killer)"
fi
