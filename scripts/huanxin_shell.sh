#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_shell.sh <ai1|ai2> "<remote command>"

Examples:
  scripts/huanxin_shell.sh ai1 "cd /root/root/work/quantum-gpt && pwd"
  scripts/huanxin_shell.sh ai2 "echo ok"
  HUANXIN_ALLOW_STANDALONE_FALLBACK=1 scripts/huanxin_shell.sh ai2 "echo ok"
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
USE_DAEMON="${HUANXIN_USE_DAEMON:-1}"
USE_DAEMON_AGENT="${HUANXIN_USE_DAEMON_AGENT:-0}"
ALLOW_STANDALONE_FALLBACK="${HUANXIN_ALLOW_STANDALONE_FALLBACK:-0}"

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
AI2_DAEMON_AGENT_SCRIPT="$ROOT_DIR/scripts/install_huanxin_ai2_daemon_agent.sh"
AI2_DAEMON_AGENT_PLIST="$HOME/Library/LaunchAgents/com.quantumgpt.huanxin-ai2-daemon.plist"
REPAIR_SCRIPT="$ROOT_DIR/scripts/repair_huanxin_browser_profile.sh"

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
  curl --max-time 2 -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1
}

daemon_health_json() {
  local port=""
  if [[ -f "$DAEMON_PORT_FILE" ]]; then
    port="$(tr -d '[:space:]' < "$DAEMON_PORT_FILE" 2>/dev/null)"
  fi
  if [[ -z "$port" ]]; then
    port="$DEFAULT_PORT"
  fi
  curl --max-time 2 -sf "http://127.0.0.1:${port}/health" 2>/dev/null || true
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

daemon_port_file_ready() {
  [[ -f "$DAEMON_PORT_FILE" ]] && [[ -n "$(tr -d '[:space:]' < "$DAEMON_PORT_FILE" 2>/dev/null)" ]]
}

daemon_restart_label() {
  if [[ "$ENV_NAME" == "ai2" && "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
    printf '%s' 'supervised daemon'
    return 0
  fi
  printf '%s' 'daemon'
}

start_daemon_if_needed() {
  local repaired=0 health_json=""
  if daemon_health_ok; then
    if ! daemon_port_file_ready; then
      printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
    fi
    health_json="$(daemon_health_json)"
    if [[ "$ENV_NAME" == "ai2" && -n "$health_json" && "$(daemon_needs_local_repair "$health_json")" == "1" ]]; then
      repaired=1
      echo "[huanxin_shell:$ENV_NAME] Daemon is alive but still on auth boot; running local repair and restarting $(daemon_restart_label)." >&2
      bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
      if [[ "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
        HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
          bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
      fi
    fi
    if [[ "$repaired" != "1" ]]; then
      if [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
        return 0
      fi
    fi
  fi

  if [[ "$ENV_NAME" == "ai2" && "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
    echo "[huanxin_shell:$ENV_NAME] Kickstarting supervised browser daemon..." >&2
    HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
      bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
  else
    echo "[huanxin_shell:$ENV_NAME] Starting browser daemon..." >&2
    HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
      nohup node browser-automation/huanxin_browser_daemon.js "$ENV_NAME" > "$DAEMON_LOG_FILE" 2>&1 &
  fi

  for poll_index in $(seq 1 30); do
    if daemon_health_ok; then
      if ! daemon_port_file_ready; then
        printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
      fi
      health_json="$(daemon_health_json)"
      if [[ "$ENV_NAME" == "ai2" && -n "$health_json" && "$(daemon_needs_local_repair "$health_json")" == "1" && "$repaired" != "1" ]]; then
        repaired=1
        echo "[huanxin_shell:$ENV_NAME] Daemon boot is stalled on auth; running local repair and restarting $(daemon_restart_label)." >&2
        bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
        if [[ "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
          HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
            bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
          sleep 2
          continue
        fi
      fi
      if [[ -f "$DAEMON_PID_FILE" ]]; then
        if [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
          echo "[huanxin_shell:$ENV_NAME] Daemon ready (PID $(cat "$DAEMON_PID_FILE" 2>/dev/null))" >&2
        fi
      elif [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
        echo "[huanxin_shell:$ENV_NAME] Daemon ready" >&2
      fi
      if [[ -n "$health_json" && "$(daemon_health_ready "$health_json")" == "1" ]]; then
        return 0
      fi
    fi
    if [[ "$ENV_NAME" == "ai2" && "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" && "$repaired" != "1" && "$poll_index" -ge 5 ]]; then
      repaired=1
      echo "[huanxin_shell:$ENV_NAME] Supervised daemon is still not responding; running local repair and restarting it." >&2
      bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
      HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
        bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
    fi
    sleep 2
  done

  echo "[huanxin_shell:$ENV_NAME] Daemon unavailable after startup attempt." >&2
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
  health_json="$(daemon_health_json)"
  if [[ "$ENV_NAME" == "ai2" && ( -z "$health_json" || "$(daemon_needs_local_repair "$health_json")" == "1" ) ]]; then
    echo "[huanxin_shell:$ENV_NAME] Daemon transport is not healthy enough for command execution; running local repair before command execution." >&2
    bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
    if [[ "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
      HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
        bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
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
  echo "[huanxin_shell:$ENV_NAME] Using daemon transport." >&2
  repair_supervised_daemon_if_needed
  JSON_OUT="$(run_daemon_command)"
  if [[ "$ENV_NAME" == "ai2" && "$(needs_local_repair_retry "$JSON_OUT")" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Detected Safari bridge startup failure in the supervised daemon; running local repair and retrying once." >&2
    bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
    if [[ "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
      HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
        bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
    fi
    JSON_OUT="$(run_daemon_command)"
  fi
else
  if [[ "$USE_DAEMON" == "1" && "$ALLOW_STANDALONE_FALLBACK" != "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Refusing standalone fallback because session preservation is required. Set HUANXIN_ALLOW_STANDALONE_FALLBACK=1 only for explicit recovery/debugging." >&2
    exit 1
  fi
  if [[ "$USE_DAEMON" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Using standalone transport only because HUANXIN_ALLOW_STANDALONE_FALLBACK=1 was set." >&2
  else
    echo "[huanxin_shell:$ENV_NAME] Using standalone transport because HUANXIN_USE_DAEMON=0 was set." >&2
  fi
  JSON_OUT="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --wait-ms "$WAIT_MS" --command "$REMOTE_CMD")"
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
