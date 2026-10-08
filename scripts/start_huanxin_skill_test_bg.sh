#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

JOB_ID="${HUANXIN_SKILL_TEST_JOB_ID:-huanxin-skill-test-$(date -u +%Y%m%dT%H%M%SZ)}"
ENV_NAME="${HUANXIN_TEST_ENV:-AI}"
MODE="${HUANXIN_SKILL_TEST_MODE:-full}"
JOB_DIR="$ROOT_DIR/.huanxin_jobs/$JOB_ID"
LOG_PATH="$JOB_DIR/nohup.log"
PID_PATH="$JOB_DIR/pid"
STATE_PATH="$JOB_DIR/state.json"

mkdir -p "$JOB_DIR"

if [[ -f "$PID_PATH" ]]; then
  OLD_PID="$(tr -d '[:space:]' < "$PID_PATH" || true)"
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "already_running job_id=$JOB_ID pid=$OLD_PID state=$STATE_PATH log=$LOG_PATH"
    exit 0
  fi
fi

cat > "$STATE_PATH" <<EOF
{
  "ok": false,
  "state": "launched",
  "jobId": "$JOB_ID",
  "envName": "$ENV_NAME",
  "mode": "$MODE",
  "startedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "currentStep": "process_start",
  "artifacts": {
    "jobDir": "$JOB_DIR",
    "logPath": "$LOG_PATH",
    "statePath": "$STATE_PATH"
  }
}
EOF

HUANXIN_SKILL_TEST_JOB_ID="$JOB_ID" \
HUANXIN_TEST_ENV="$ENV_NAME" \
HUANXIN_SKILL_TEST_MODE="$MODE" \
nohup node browser-automation/huanxin_skill_background_test.js --env "$ENV_NAME" --job-id "$JOB_ID" --mode "$MODE" \
  > "$LOG_PATH" 2>&1 &

PID="$!"
printf '%s\n' "$PID" > "$PID_PATH"

cat <<EOF
started job_id=$JOB_ID
mode=$MODE
pid=$PID
state=$STATE_PATH
log=$LOG_PATH
EOF
