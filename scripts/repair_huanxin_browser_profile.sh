#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

resolve_node() {
  local candidate
  for candidate in \
    "${NODE_BIN:-}" \
    "$HOME"/.local/state/fnm_multishells/*/bin/node \
    /opt/homebrew/bin/node \
    /usr/local/bin/node \
    /usr/bin/node
  do
    if [[ -n "${candidate:-}" && -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

NODE_PATH="$(resolve_node)" || {
  echo "node binary not found for Huanxin profile repair" >&2
  exit 1
}

RESULT_PATH="${HUANXIN_PROFILE_REPAIR_RESULT_PATH:-/tmp/huanxin-browser-profile-repair.json}"
STATE_PATH="${HUANXIN_PROFILE_REPAIR_STATE_PATH:-/tmp/huanxin-browser-profile-repair-state.json}"
RUN_PROBE="${HUANXIN_REPAIR_RUN_PROBE:-0}"
PRINT_RESULT="${HUANXIN_PROFILE_REPAIR_PRINT_RESULT:-1}"
RESTART_DAEMON_ON_SUCCESS="${HUANXIN_REPAIR_RESTART_DAEMON_ON_SUCCESS:-1}"
DAEMON_RESTART_MIN_INTERVAL_SEC="${HUANXIN_DAEMON_RESTART_MIN_INTERVAL_SEC:-90}"
DAEMON_RESTART_LAST_FILE="${HUANXIN_DAEMON_RESTART_LAST_FILE:-/tmp/huanxin-ai2-daemon-restart.last_started}"
DAEMON_AGENT_SCRIPT="${HUANXIN_AI2_DAEMON_AGENT_SCRIPT:-$ROOT_DIR/scripts/install_huanxin_ai2_daemon_agent.sh}"
STARTED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
LAST_STAGE="bootstrap"

write_state() {
  local status="$1"
  local stage="$2"
  local payload_json="${3:-}"
  /usr/bin/python3 - "$STATE_PATH" "$status" "$stage" "$STARTED_AT" "$RESULT_PATH" "$payload_json" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

state_path = Path(sys.argv[1])
status = sys.argv[2]
stage = sys.argv[3]
started_at = sys.argv[4]
result_path = sys.argv[5]
payload_json = sys.argv[6]

payload = {
    "status": status,
    "stage": stage,
    "pid": os.getpid(),
    "started_at": started_at,
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "result_path": result_path,
}
if payload_json:
    try:
        payload["detail"] = json.loads(payload_json)
    except json.JSONDecodeError:
        payload["detail"] = {"raw": payload_json}

tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
tmp_path.replace(state_path)
PY
}

on_exit() {
  local rc=$?
  if [[ "$rc" -ne 0 ]]; then
    local error_json
    error_json="$(/usr/bin/python3 - "$rc" "$LAST_STAGE" <<'PY'
import json
import sys

print(json.dumps({"exit_code": int(sys.argv[1]), "last_stage": sys.argv[2]}, ensure_ascii=False))
PY
)"
    write_state "failed" "$LAST_STAGE" "$error_json" || true
  fi
  return "$rc"
}
trap on_exit EXIT

write_state "running" "$LAST_STAGE"

LAST_STAGE="repair_profile"
"$NODE_PATH" browser-automation/huanxin_repair_profile_via_safari_sso.js --result-path "$RESULT_PATH" "$@"
if [[ "$RUN_PROBE" == "1" ]]; then
  LAST_STAGE="post_repair_probe"
  "$NODE_PATH" browser-automation/huanxin_probe.js
fi

LAST_STAGE="validate_result"
/usr/bin/python3 - "$RESULT_PATH" "$PRINT_RESULT" <<'PY'
import json
import sys
from pathlib import Path

result_path = Path(sys.argv[1])
print_result = sys.argv[2] == "1"

if not result_path.exists():
    raise SystemExit(f"Huanxin profile repair did not produce result file: {result_path}")

try:
    payload = json.loads(result_path.read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    raise SystemExit(f"Huanxin profile repair result is not valid JSON: {result_path} ({exc})") from exc

if "ok" not in payload:
    raise SystemExit(f"Huanxin profile repair result is missing required field 'ok': {result_path}")

if print_result:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
PY

LAST_STAGE="completed"
RESULT_JSON="$(cat "$RESULT_PATH")"
write_state "succeeded" "$LAST_STAGE" "$RESULT_JSON"

if [[ "$RESTART_DAEMON_ON_SUCCESS" == "1" ]]; then
  LAST_STAGE="restart_daemon_if_needed"
  SHOULD_RESTART="$(
    /usr/bin/python3 - "$DAEMON_RESTART_LAST_FILE" "$DAEMON_RESTART_MIN_INTERVAL_SEC" <<'PY'
import pathlib
import sys
import time

last_file = pathlib.Path(sys.argv[1])
min_interval = int(sys.argv[2])
now = int(time.time())
try:
    last = int(last_file.read_text(encoding="utf-8").strip())
except Exception:
    last = 0
if now - last < min_interval:
    print("0")
    raise SystemExit(0)
last_file.write_text(f"{now}\n", encoding="utf-8")
print("1")
PY
  )"
  if [[ "$SHOULD_RESTART" == "1" ]]; then
    if [[ -f "$DAEMON_AGENT_SCRIPT" ]]; then
      if bash "$DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1; then
        echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"event\":\"daemon_kickstart\",\"ok\":true}" >&2
      else
        echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"event\":\"daemon_kickstart\",\"ok\":false}" >&2
      fi
    else
      echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"event\":\"daemon_kickstart\",\"ok\":false,\"reason\":\"agent_script_missing\"}" >&2
    fi
  fi
fi
