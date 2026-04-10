#!/usr/bin/env bash
set -euo pipefail

# Wrapper for Huanxin ai2 shell access.
# Uses the persistent browser daemon by default.
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
USE_DAEMON="${HUANXIN_USE_DAEMON:-1}"
USE_DAEMON_AGENT="${HUANXIN_USE_DAEMON_AGENT:-1}"
ALLOW_STANDALONE_FALLBACK="${HUANXIN_ALLOW_STANDALONE_FALLBACK:-0}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
DAEMON_AGENT_SCRIPT="$ROOT_DIR/scripts/install_huanxin_ai2_daemon_agent.sh"
DAEMON_AGENT_PLIST="$HOME/Library/LaunchAgents/com.quantumgpt.huanxin-ai2-daemon.plist"
REPAIR_SCRIPT="$ROOT_DIR/scripts/repair_huanxin_browser_profile.sh"

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
  curl --max-time 2 -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1
}

daemon_health_json() {
  local port=""
  if [[ -f "$DAEMON_PORT_FILE" ]]; then
    port="$(cat "$DAEMON_PORT_FILE" 2>/dev/null | tr -d '[:space:]')"
  fi
  if [[ -z "$port" ]]; then
    port="$DEFAULT_PORT"
  fi
  curl --max-time 2 -sf "http://127.0.0.1:${port}/health" 2>/dev/null || true
}

daemon_log_tail() {
  if [[ -f "$DAEMON_LOG_FILE" ]]; then
    tail -n 40 "$DAEMON_LOG_FILE" 2>/dev/null || true
  fi
}

daemon_log_has_known_launch_crash() {
  python3 - <<'PY' "$1"
import sys

text = str(sys.argv[1] or "")
patterns = (
  "Target page, context or browser has been closed",
  "Received signal 6",
  "bootstrap_check_in",
  "Operation not permitted",
  "launchPersistentContext",
)
print("1" if any(pattern in text for pattern in patterns) else "0")
PY
}

daemon_pid_running() {
  if [[ ! -f "$DAEMON_PID_FILE" ]]; then
    return 1
  fi
  local pid=""
  pid="$(cat "$DAEMON_PID_FILE" 2>/dev/null | tr -d '[:space:]')"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" >/dev/null 2>&1
}

daemon_failed_to_launch() {
  local log_tail=""
  log_tail="$(daemon_log_tail)"
  if [[ -n "$log_tail" && "$(daemon_log_has_known_launch_crash "$log_tail")" == "1" ]]; then
    printf '%s' "$log_tail"
    return 0
  fi
  if [[ -f "$DAEMON_LOG_FILE" && ! daemon_health_ok && ! daemon_pid_running ]]; then
    printf '%s' "$log_tail"
    return 0
  fi
  return 1
}

daemon_needs_local_repair() {
  python3 - <<'PY' "$1"
import json
import sys

try:
  payload = json.loads(sys.argv[1])
except Exception:
  print("0")
  raise SystemExit(0)

startup_error = str(payload.get("startupError") or "")
current_url = str(payload.get("currentUrl") or "")
ready = bool(payload.get("ready"))
needs = (
  "safari_capture_callback.sh" in startup_error
  or "Safari callback capture failed" in startup_error
  or ((not ready) and "/auth/realms/" in current_url)
)
print("1" if needs else "0")
PY
}

daemon_health_ready() {
  python3 - <<'PY' "$1"
import json
import sys

try:
  payload = json.loads(sys.argv[1])
except Exception:
  print("0")
  raise SystemExit(0)

print("1" if payload.get("ready") else "0")
PY
}

daemon_lock_stale() {
  python3 - <<'PY' "$1" "$2"
import json
import sys

try:
  payload = json.loads(sys.argv[1])
except Exception:
  print("0")
  raise SystemExit(0)

try:
  stale_ms = int(sys.argv[2])
except Exception:
  stale_ms = 0

busy = bool(payload.get("busy"))
busy_age_ms = int(payload.get("busyAgeMs") or 0)
print("1" if busy and busy_age_ms >= stale_ms and stale_ms > 0 else "0")
PY
}

daemon_port_file_ready() {
  [[ -f "$DAEMON_PORT_FILE" ]] && [[ -n "$(cat "$DAEMON_PORT_FILE" 2>/dev/null | tr -d '[:space:]')" ]]
}

daemon_stop() {
  local port=""
  if [[ -f "$DAEMON_PORT_FILE" ]]; then
    port="$(cat "$DAEMON_PORT_FILE" 2>/dev/null | tr -d '[:space:]')"
  fi
  if [[ -z "$port" ]]; then
    port="$DEFAULT_PORT"
  fi
  curl --max-time 5 -sf -X POST "http://127.0.0.1:${port}/stop" >/dev/null 2>&1 || true
  if [[ -f "$DAEMON_PID_FILE" ]]; then
    local pid=""
    pid="$(cat "$DAEMON_PID_FILE" 2>/dev/null | tr -d '[:space:]')"
    if [[ -n "$pid" ]]; then
      kill "$pid" >/dev/null 2>&1 || true
    fi
  fi
  rm -f "$DAEMON_PID_FILE" "$DAEMON_PORT_FILE"
}

daemon_restart_label() {
  if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
    printf '%s' 'supervised daemon'
    return 0
  fi
  printf '%s' 'daemon'
}

kickstart_supervised_daemon() {
  local output="" rc=0
  set +e
  output="$(
    HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
      bash "$DAEMON_AGENT_SCRIPT" --kickstart 2>&1
  )"
  rc=$?
  set -e
  if [[ -n "$output" ]]; then
    printf '%s\n' "$output" >&2
  fi
  return "$rc"
}

ensure_supervised_daemon_agent_installed() {
  if [[ "$USE_DAEMON_AGENT" != "1" ]]; then
    return 0
  fi
  if ! command -v launchctl >/dev/null 2>&1; then
    return 0
  fi
  if [[ -f "$DAEMON_AGENT_PLIST" ]]; then
    return 0
  fi

  echo "[ai2_shell] Installing supervised ai2 daemon agent..." >&2
  HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
    bash "$DAEMON_AGENT_SCRIPT" --install >/dev/null 2>&1 || true
}

start_daemon_if_needed() {
  local repaired=0 health_json=""
  local stale_lock_ms=$(( WAIT_MS + 30000 ))
  ensure_supervised_daemon_agent_installed
  if daemon_health_ok; then
    if ! daemon_port_file_ready; then
      printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
    fi
    health_json="$(daemon_health_json)"
    if [[ -n "$health_json" && "$(daemon_lock_stale "$health_json" "$stale_lock_ms")" == "1" ]]; then
      echo "[ai2_shell] Detected stale daemon command lock; restarting daemon before command execution." >&2
      daemon_stop
      sleep 1
      health_json=""
    fi
    if [[ -n "$health_json" && "$(daemon_needs_local_repair "$health_json")" == "1" ]]; then
      repaired=1
      echo "[ai2_shell] Daemon is alive but still on auth boot; running local repair and restarting $(daemon_restart_label)." >&2
      bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
      if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
        kickstart_supervised_daemon || true
      fi
    fi
    if [[ "$repaired" != "1" ]]; then
      if [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
        return 0
      fi
    fi
  fi

  if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
    echo "[ai2_shell] Kickstarting supervised ai2 daemon..." >&2
    kickstart_supervised_daemon || true
  else
    echo "[ai2_shell] Starting browser daemon for ai2..." >&2
    HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
      nohup node browser-automation/huanxin_browser_daemon.js "$ENV_NAME" > "$DAEMON_LOG_FILE" 2>&1 &
  fi

  for poll_index in $(seq 1 30); do
    if daemon_health_ok; then
      if ! daemon_port_file_ready; then
        printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
      fi
      health_json="$(daemon_health_json)"
      if [[ -n "$health_json" && "$(daemon_needs_local_repair "$health_json")" == "1" && "$repaired" != "1" ]]; then
        repaired=1
        echo "[ai2_shell] Daemon boot is stalled on auth; running local repair and restarting $(daemon_restart_label)." >&2
        bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
        if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
          kickstart_supervised_daemon || true
          sleep 2
          continue
        fi
      fi
      if [[ -f "$DAEMON_PID_FILE" ]]; then
        if [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
          echo "[ai2_shell] Daemon ready (PID $(cat "$DAEMON_PID_FILE" 2>/dev/null))" >&2
        fi
      elif [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
        echo "[ai2_shell] Daemon ready" >&2
      fi
      if [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
        return 0
      fi
    fi
    if failed_log="$(daemon_failed_to_launch)"; then
      echo "[ai2_shell] Local ai2 browser daemon failed to launch; this blocks shell transport before any remote status command runs." >&2
      if [[ -n "$failed_log" ]]; then
        printf '%s\n' "$failed_log" >&2
      fi
      return 1
    fi
    if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" && "$repaired" != "1" && "$poll_index" -ge 5 ]]; then
      repaired=1
      echo "[ai2_shell] Supervised daemon is still not responding; running local repair and restarting it." >&2
      bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
      kickstart_supervised_daemon || true
    fi
    sleep 2
  done

  echo "[ai2_shell] Daemon unavailable after startup attempt." >&2
  if [[ -f "$DAEMON_LOG_FILE" ]]; then
    tail -n 20 "$DAEMON_LOG_FILE" >&2 || true
  fi
  return 1
}

run_daemon_command() {
  node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --require-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD"
}

repair_supervised_daemon_if_needed() {
  local health_json=""
  local stale_lock_ms=$(( WAIT_MS + 30000 ))
  ensure_supervised_daemon_agent_installed
  health_json="$(daemon_health_json)"
  if [[ -n "$health_json" && "$(daemon_lock_stale "$health_json" "$stale_lock_ms")" == "1" ]]; then
    echo "[ai2_shell] Daemon is holding a stale command lock; restarting it before command execution." >&2
    daemon_stop
    sleep 1
    return
  fi
  if [[ -z "$health_json" || "$(daemon_needs_local_repair "$health_json")" == "1" ]]; then
    echo "[ai2_shell] Daemon transport is not healthy enough for command execution; running local repair before command execution." >&2
    bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
    if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
      kickstart_supervised_daemon || true
    fi
  fi
}

needs_local_repair_retry() {
  python3 - <<'PY' "$1"
import json
import sys

try:
  payload = json.loads(sys.argv[1])
except Exception:
  print("0")
  raise SystemExit(0)

error = str(payload.get("error") or "")
needs = (
  not payload.get("ok", False)
  and (
    "safari_capture_callback.sh" in error
    or "Safari callback capture failed" in error
  )
)
print("1" if needs else "0")
PY
}

if [[ "$USE_DAEMON" == "1" ]] && start_daemon_if_needed && daemon_port_file_ready; then
  echo "[ai2_shell] Using daemon transport for ai2." >&2
  repair_supervised_daemon_if_needed
  JSON_OUT="$(run_daemon_command)"
  if [[ "$(needs_local_repair_retry "$JSON_OUT")" == "1" ]]; then
    echo "[ai2_shell] Detected Safari bridge startup failure in the supervised daemon; running local repair and retrying once." >&2
    bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
    if [[ "$USE_DAEMON_AGENT" == "1" && -f "$DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
      kickstart_supervised_daemon || true
    fi
    JSON_OUT="$(run_daemon_command)"
  fi
else
  if [[ "$USE_DAEMON" == "1" && "$ALLOW_STANDALONE_FALLBACK" != "1" ]]; then
    echo "[ai2_shell] Refusing standalone fallback because session preservation is required. Set HUANXIN_ALLOW_STANDALONE_FALLBACK=1 only for explicit recovery/debugging." >&2
    exit 1
  fi
  if [[ "$USE_DAEMON" == "1" ]]; then
    echo "[ai2_shell] Using standalone transport only because HUANXIN_ALLOW_STANDALONE_FALLBACK=1 was set." >&2
  else
    echo "[ai2_shell] Using standalone transport because HUANXIN_USE_DAEMON=0 was set." >&2
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
