#!/usr/bin/env bash
set -euo pipefail

# Wrapper for Huanxin ai2 shell access.
# Tries the persistent browser daemon first; falls back to standalone.
# Usage:
#   scripts/ai2_shell.sh "cd /root/root/work/quantum-gpt && ls"

if [[ $# -lt 1 ]]; then
  echo 'Usage: scripts/ai2_shell.sh "<remote command>"' >&2
  exit 1
fi

PROFILE_COPY_NAME="${HUANXIN_PROFILE_COPY_NAME:-quantum-rnd}"
export HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME"
export HUANXIN_HEADLESS="${HUANXIN_HEADLESS:-1}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
ENV_NAME="ai2"
DEFAULT_PORT="19002"
USE_DAEMON="${HUANXIN_USE_DAEMON:-0}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUN_MARKER="__AI2_RUN_$(date +%s%N)__"
REMOTE_CMD="$*; echo ${RUN_MARKER}"

DAEMON_PORT_FILE="/tmp/huanxin-daemon-${ENV_NAME}.port"
DAEMON_PID_FILE="/tmp/huanxin-daemon-${ENV_NAME}.pid"
DAEMON_LOG_FILE="/tmp/huanxin-daemon-${ENV_NAME}.log"

daemon_health_ok() {
  local port=""
  if [[ -f "$DAEMON_PORT_FILE" ]]; then
    port="$(cat "$DAEMON_PORT_FILE" 2>/dev/null | tr -d '[:space:]')"
  fi
  if [[ -z "$port" ]]; then
    port="$DEFAULT_PORT"
  fi
  curl -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1
}

daemon_port_file_ready() {
  [[ -f "$DAEMON_PORT_FILE" ]] && [[ -n "$(cat "$DAEMON_PORT_FILE" 2>/dev/null | tr -d '[:space:]')" ]]
}

start_daemon_if_needed() {
  if daemon_health_ok; then
    if ! daemon_port_file_ready; then
      printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
    fi
    return 0
  fi

  echo "[ai2_shell] Starting browser daemon for ai2..." >&2
  HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
    nohup node browser-automation/huanxin_browser_daemon.js "$ENV_NAME" > "$DAEMON_LOG_FILE" 2>&1 &

  for _ in $(seq 1 30); do
    if daemon_health_ok; then
      if ! daemon_port_file_ready; then
        printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
      fi
      if [[ -f "$DAEMON_PID_FILE" ]]; then
        echo "[ai2_shell] Daemon ready (PID $(cat "$DAEMON_PID_FILE" 2>/dev/null))" >&2
      else
        echo "[ai2_shell] Daemon ready" >&2
      fi
      return 0
    fi
    sleep 2
  done

  echo "[ai2_shell] Daemon unavailable after startup attempt; falling back to standalone browser execution." >&2
  if [[ -f "$DAEMON_LOG_FILE" ]]; then
    tail -n 20 "$DAEMON_LOG_FILE" >&2 || true
  fi
  return 1
}

if [[ "$USE_DAEMON" == "1" ]] && start_daemon_if_needed && daemon_port_file_ready; then
  echo "[ai2_shell] Using daemon transport for ai2." >&2
  JSON_OUT="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --require-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD")"
else
  if [[ "$USE_DAEMON" == "1" ]]; then
    echo "[ai2_shell] Falling back to standalone transport for ai2." >&2
  else
    echo "[ai2_shell] Using standalone transport for ai2." >&2
  fi
  JSON_OUT="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --wait-ms "$WAIT_MS" --command "$REMOTE_CMD")"
fi

python3 - <<'PY' "$JSON_OUT" "$*" "$RUN_MARKER"
import json
import sys

payload = json.loads(sys.argv[1])
command = sys.argv[2]
run_marker = sys.argv[3]
marker_prefixes = ('__AI2_', '__FRESH', '__HX_')
combined = '\n'.join(str(payload.get(k, '')) for k in ('output', 'after', 'before'))

if not payload.get('ok', False):
  raise SystemExit(f"ai2_shell command failed: {payload}")

if run_marker not in combined:
  raise SystemExit(
    f"Detected stale Huanxin shell output: expected run marker {run_marker} was not observed."
  )

if payload.get('ok') and any(prefix in command for prefix in marker_prefixes):
  observed = any(prefix in combined for prefix in marker_prefixes)
  if not observed:
    raise SystemExit(
      'Detected stale Huanxin shell output: command contains explicit validation markers '
      'but response does not include any marker text. Remote state is ambiguous; stop and retry later.'
    )

print(json.dumps(payload, indent=2))
PY
