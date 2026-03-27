#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_shell.sh <ai1|ai2> "<remote command>"

Examples:
  scripts/huanxin_shell.sh ai1 "cd /root/root/work/quantum-gpt && pwd"
  HUANXIN_USE_DAEMON=1 scripts/huanxin_shell.sh ai2 "echo ok"
EOF
  exit 1
}

if [[ $# -lt 2 ]]; then
  usage
fi

ENV_NAME="$1"
shift

case "$ENV_NAME" in
  ai1) DEFAULT_PORT="19001" ;;
  ai2) DEFAULT_PORT="19002" ;;
  *) echo "Unsupported env: $ENV_NAME" >&2; exit 1 ;;
esac

export HUANXIN_HEADLESS="${HUANXIN_HEADLESS:-1}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
USE_DAEMON="${HUANXIN_USE_DAEMON:-0}"

if [[ -n "${HUANXIN_PROFILE_COPY_NAME:-}" ]]; then
  PROFILE_COPY_NAME="$HUANXIN_PROFILE_COPY_NAME"
elif [[ "$USE_DAEMON" == "1" ]]; then
  PROFILE_COPY_NAME="quantum-rnd"
else
  PROFILE_COPY_NAME="quantum-rnd-${$}-$(date +%s%N)"
fi
export HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUN_PREFIX="$(printf '%s' "$ENV_NAME" | tr '[:lower:]' '[:upper:]')"
RUN_MARKER="__${RUN_PREFIX}_RUN_$(date +%s%N)__"
REMOTE_CMD="$*; echo ${RUN_MARKER}"

DAEMON_PORT_FILE="/tmp/huanxin-daemon-${ENV_NAME}.port"
DAEMON_PID_FILE="/tmp/huanxin-daemon-${ENV_NAME}.pid"
DAEMON_LOG_FILE="/tmp/huanxin-daemon-${ENV_NAME}.log"

daemon_health_ok() {
  local port=""
  if [[ -f "$DAEMON_PORT_FILE" ]]; then
    port="$(tr -d '[:space:]' < "$DAEMON_PORT_FILE" 2>/dev/null)"
  fi
  if [[ -z "$port" ]]; then
    port="$DEFAULT_PORT"
  fi
  curl -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1
}

daemon_port_file_ready() {
  [[ -f "$DAEMON_PORT_FILE" ]] && [[ -n "$(tr -d '[:space:]' < "$DAEMON_PORT_FILE" 2>/dev/null)" ]]
}

start_daemon_if_needed() {
  local launch_pid=""
  if daemon_health_ok; then
    if ! daemon_port_file_ready; then
      printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
    fi
    return 0
  fi

  echo "[huanxin_shell:$ENV_NAME] Starting browser daemon..." >&2
  HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
    nohup node browser-automation/huanxin_browser_daemon.js "$ENV_NAME" > "$DAEMON_LOG_FILE" 2>&1 &
  launch_pid="$!"

  for _ in $(seq 1 30); do
    if daemon_health_ok; then
      if ! daemon_port_file_ready; then
        printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
      fi
      if [[ -f "$DAEMON_PID_FILE" ]]; then
        echo "[huanxin_shell:$ENV_NAME] Daemon ready (PID $(cat "$DAEMON_PID_FILE" 2>/dev/null))" >&2
      else
        echo "[huanxin_shell:$ENV_NAME] Daemon ready" >&2
      fi
      return 0
    fi
    if [[ -n "$launch_pid" ]] && ! kill -0 "$launch_pid" 2>/dev/null; then
      echo "[huanxin_shell:$ENV_NAME] Daemon exited before becoming healthy; falling back to standalone browser execution." >&2
      if [[ -f "$DAEMON_LOG_FILE" ]]; then
        tail -n 40 "$DAEMON_LOG_FILE" >&2 || true
      fi
      return 1
    fi
    sleep 2
  done

  echo "[huanxin_shell:$ENV_NAME] Daemon unavailable after startup attempt; falling back to standalone browser execution." >&2
  if [[ -f "$DAEMON_LOG_FILE" ]]; then
    tail -n 20 "$DAEMON_LOG_FILE" >&2 || true
  fi
  return 1
}

if [[ "$USE_DAEMON" == "1" ]] && start_daemon_if_needed && daemon_port_file_ready; then
  echo "[huanxin_shell:$ENV_NAME] Using daemon transport." >&2
  JSON_OUT="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --require-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD")"
else
  if [[ "$USE_DAEMON" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Falling back to standalone transport." >&2
  else
    echo "[huanxin_shell:$ENV_NAME] Using standalone transport." >&2
  fi
  JSON_OUT="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --skip-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD")"
fi

python3 - <<'PY' "$JSON_OUT" "$ENV_NAME" "$*" "$RUN_MARKER"
import json
import sys

payload = json.loads(sys.argv[1])
env_name = sys.argv[2]
command = sys.argv[3]
run_marker = sys.argv[4]
marker_prefixes = ('__AI1_', '__AI2_', '__FRESH', '__HX_')
combined = '\n'.join(str(payload.get(k, '')) for k in ('output', 'after', 'before'))

if not payload.get('ok', False):
    raise SystemExit(f"{env_name}_shell command failed: {payload}")

if run_marker not in combined:
    raise SystemExit(
        f"Detected stale Huanxin shell output for {env_name}: expected run marker {run_marker} was not observed."
    )

if payload.get('ok') and any(prefix in command for prefix in marker_prefixes):
    observed = any(prefix in combined for prefix in marker_prefixes)
    if not observed:
        raise SystemExit(
            f"Detected stale Huanxin shell output for {env_name}: command contains explicit validation markers "
            "but response does not include any marker text. Remote state is ambiguous; stop and retry later."
        )

print(json.dumps(payload, indent=2))
PY
