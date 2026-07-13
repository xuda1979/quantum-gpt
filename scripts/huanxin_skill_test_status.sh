#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SUMMARY=0
TAIL_LINES=0
JOB_ID="${HUANXIN_SKILL_TEST_JOB_ID:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --summary)
      SUMMARY=1
      shift
      ;;
    --tail)
      TAIL_LINES="${2:-80}"
      shift 2
      ;;
    *)
      JOB_ID="$1"
      shift
      ;;
  esac
done
if [[ -z "$JOB_ID" ]]; then
  JOB_DIR="$(find "$ROOT_DIR/.huanxin_jobs" -mindepth 1 -maxdepth 1 -type d -name 'huanxin-skill-test-*' 2>/dev/null | sort | tail -n 1 || true)"
else
  JOB_DIR="$ROOT_DIR/.huanxin_jobs/$JOB_ID"
fi

if [[ -z "${JOB_DIR:-}" || ! -d "$JOB_DIR" ]]; then
  echo "no huanxin skill test job found" >&2
  exit 1
fi

STATE_PATH="$JOB_DIR/state.json"
PID_PATH="$JOB_DIR/pid"
LOG_PATH="$JOB_DIR/nohup.log"

if [[ "$TAIL_LINES" != "0" ]]; then
  if [[ -f "$JOB_DIR/runner.log" ]]; then
    tail -n "$TAIL_LINES" "$JOB_DIR/runner.log"
  elif [[ -f "$LOG_PATH" ]]; then
    tail -n "$TAIL_LINES" "$LOG_PATH"
  else
    echo "no log found for $JOB_DIR" >&2
    exit 1
  fi
elif [[ -f "$STATE_PATH" && "$SUMMARY" == "1" ]]; then
  python3 - "$STATE_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    payload = json.load(handle)

steps = payload.get("steps") or []
latest = steps[-1] if steps else {}
print(f"jobId={payload.get('jobId')}")
print(f"state={payload.get('state')} ok={payload.get('ok')} mode={payload.get('mode')}")
print(f"currentStep={payload.get('currentStep')}")
if latest:
    print(
        "latestStep="
        f"{latest.get('name')} state={latest.get('state')} ok={latest.get('ok')} "
        f"failureKind={latest.get('failureKind')}"
    )
    if latest.get("captchaImage"):
        print(f"captchaImage={latest.get('captchaImage')}")
print(f"statePath={sys.argv[1]}")
PY
elif [[ -f "$STATE_PATH" ]]; then
  cat "$STATE_PATH"
else
  echo "{\"ok\":false,\"state\":\"state_missing\",\"jobDir\":\"$JOB_DIR\",\"pidPath\":\"$PID_PATH\",\"logPath\":\"$LOG_PATH\"}"
fi
