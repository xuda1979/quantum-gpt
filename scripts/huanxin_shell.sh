#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR_EARLY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -f "$ROOT_DIR_EARLY/.huanxin_automation_enabled" || -f "$ROOT_DIR_EARLY/.huanxin_manual_mode" ]]; then
  echo "[huanxin_shell] Huanxin browser automation is disabled; refusing to touch the webshell." >&2
  echo "[huanxin_shell] Create $ROOT_DIR_EARLY/.huanxin_automation_enabled only when automation is intentionally allowed again." >&2
  exit 125
fi

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_shell.sh <env-name> "<remote command>"

Examples:
  scripts/huanxin_shell.sh ASI1 "cd /root/work/quantum-gpt && pwd"
  HUANXIN_ALLOW_STANDALONE_FALLBACK=1 scripts/huanxin_shell.sh ASI1 "echo ok"
EOF
  exit 1
}

if [[ $# -lt 2 ]]; then
  usage
fi

ENV_NAME="$1"
shift

ENV_CONFIG="$("$ROOT_DIR_EARLY/.venv/bin/python" "$ROOT_DIR_EARLY/scripts/huanxin_env_config.py" --env "$ENV_NAME" --format shell 2>/dev/null || python3 "$ROOT_DIR_EARLY/scripts/huanxin_env_config.py" --env "$ENV_NAME" --format shell)"
eval "$ENV_CONFIG"
DEFAULT_PORT="$HUANXIN_ENV_DAEMON_PORT"
export HUANXIN_TRAIN_DEV_URL="${HUANXIN_TRAIN_DEV_URL:-$HUANXIN_ENV_TRAIN_DEV_URL}"

export HUANXIN_HEADLESS="${HUANXIN_HEADLESS:-1}"
export HUANXIN_ALLOW_HEADED_FALLBACK="${HUANXIN_ALLOW_HEADED_FALLBACK:-0}"
export HUANXIN_ALLOW_SAFARI_SSO_BRIDGE="${HUANXIN_ALLOW_SAFARI_SSO_BRIDGE:-0}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
USE_DAEMON="${HUANXIN_USE_DAEMON:-1}"
USE_DAEMON_AGENT="${HUANXIN_USE_DAEMON_AGENT:-0}"
ALLOW_STANDALONE_FALLBACK="${HUANXIN_ALLOW_STANDALONE_FALLBACK:-0}"
DAEMON_STARTUP_MAX_POLLS="${HUANXIN_DAEMON_STARTUP_MAX_POLLS:-30}"
DAEMON_STARTUP_POLL_INTERVAL_SECONDS="${HUANXIN_DAEMON_STARTUP_POLL_INTERVAL_SECONDS:-2}"
PROFILE_COPY_NAME_EXPLICIT=0

if [[ -n "${HUANXIN_PROFILE_DIR:-}" ]]; then
  PROFILE_COPY_NAME=""
  unset HUANXIN_PROFILE_COPY_NAME
elif [[ -n "${HUANXIN_PROFILE_COPY_NAME:-}" ]]; then
  PROFILE_COPY_NAME="$HUANXIN_PROFILE_COPY_NAME"
  PROFILE_COPY_NAME_EXPLICIT=1
elif [[ "$USE_DAEMON" == "1" ]]; then
  PROFILE_COPY_NAME="quantum-rnd"
else
  PROFILE_COPY_NAME="quantum-rnd-${$}-$(date +%s%N)"
fi
if [[ -n "$PROFILE_COPY_NAME" ]]; then
  export HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME"
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
MANUAL_MODE_LOCK="$ROOT_DIR/.huanxin_manual_mode"
if [[ -f "$MANUAL_MODE_LOCK" ]]; then
  echo "[huanxin_shell:$ENV_NAME] Manual Huanxin use lock is active at $MANUAL_MODE_LOCK; refusing browser automation." >&2
  echo "[huanxin_shell:$ENV_NAME] Remove the lock only when Huanxin browser automation is intentionally allowed again." >&2
  exit 125
fi
AI2_DAEMON_AGENT_SCRIPT="$ROOT_DIR/scripts/install_huanxin_ai2_daemon_agent.sh"
AI2_DAEMON_AGENT_PLIST="$HOME/Library/LaunchAgents/com.quantumgpt.huanxin-ai2-daemon.plist"
REPAIR_SCRIPT="$ROOT_DIR/scripts/repair_huanxin_browser_profile.sh"
DAEMON_STATE_HELPER="$ROOT_DIR/scripts/huanxin_daemon_state.py"

RUN_PREFIX="$(printf '%s' "$ENV_NAME" | tr '[:lower:]' '[:upper:]')"
RUN_MARKER="__${RUN_PREFIX}_RUN_$(date +%s%N)__"
REMOTE_CMD="$(printf '%s\n%s\n' "$*" "echo ${RUN_MARKER}")"

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

daemon_terminal_prompt_failure() {
  python3 - <<'PY' "$1"
import json
import sys

try:
    payload = json.loads(sys.argv[1])
except Exception:
    print("0")
    raise SystemExit(0)

startup_error = str(payload.get("startupError") or "")
needs = (
    payload.get("startupState") == "error"
    and "did not reach a prompt" in startup_error
)
print("1" if needs else "0")
PY
}

daemon_shell_endpoint_failure_summary() {
  python3 - <<'PY' "$1"
import json
import sys

try:
    payload = json.loads(sys.argv[1])
except Exception:
    print("")
    raise SystemExit(0)

failure = payload.get("startupFailure") or {}
summary = ""
if isinstance(failure, dict):
    if failure.get("kind") == "shell_endpoint_unavailable":
        summary = str(failure.get("summary") or "")
    elif payload.get("shellEndpointFailure"):
        summary = str(payload.get("healthSummary") or payload.get("startupError") or "")

if not summary:
    startup_error = str(payload.get("startupError") or "")
    if "shell endpoint API returned no terminal URL" in startup_error:
        summary = startup_error

print(summary)
PY
}

daemon_non_retryable_shell_failure() {
  python3 - <<'PY' "$1"
import json
import sys

try:
    payload = json.loads(sys.argv[1])
except Exception:
    print("0")
    raise SystemExit(0)

failure = payload.get("startupFailure") or {}
summary = str(payload.get("healthSummary") or "")
startup_error = str(payload.get("startupError") or "")
kind = str(failure.get("kind") or "")

needs = (
    kind == "shell_endpoint_unavailable"
    or bool(payload.get("shellEndpointFailure"))
    or "shell endpoint API returned no terminal URL" in startup_error
    or "shell endpoint API returned no terminal URL" in summary
)
print("1" if needs else "0")
PY
}

daemon_port_file_ready() {
  [[ -f "$DAEMON_PORT_FILE" ]] && [[ -n "$(tr -d '[:space:]' < "$DAEMON_PORT_FILE" 2>/dev/null)" ]]
}

daemon_state_json() {
  python3 "$DAEMON_STATE_HELPER" inspect "$ENV_NAME" 2>/dev/null || true
}

daemon_state_stale() {
  python3 - <<'PY' "$1"
import json
import sys

try:
    payload = json.loads(sys.argv[1])
except Exception:
    print("0")
    raise SystemExit(0)

print("1" if payload.get("stale_state_detected") else "0")
PY
}

cleanup_stale_daemon_state_if_needed() {
  local state_json=""
  state_json="$(daemon_state_json)"
  if [[ -n "$state_json" && "$(daemon_state_stale "$state_json")" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Found stale daemon pid/port/ipc state; cleaning it up before restart." >&2
    python3 "$DAEMON_STATE_HELPER" cleanup-stale "$ENV_NAME" >&2 || true
  fi
}

start_local_daemon_detached() {
  /usr/bin/env node - "$ROOT_DIR" "$ENV_NAME" "$DEFAULT_PORT" "$DAEMON_LOG_FILE" "$PROFILE_COPY_NAME" "$HUANXIN_HEADLESS" <<'NODE'
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const [rootDir, envName, port, logPath, profileCopyName, headless] = process.argv.slice(2);
const out = fs.openSync(logPath, 'a');
const childEnv = {
  ...process.env,
  HUANXIN_HEADLESS: headless,
};
if (profileCopyName) {
  childEnv.HUANXIN_PROFILE_COPY_NAME = profileCopyName;
} else {
  delete childEnv.HUANXIN_PROFILE_COPY_NAME;
}
const child = spawn(process.execPath, ['browser-automation/huanxin_browser_daemon.js', envName, '--port', port], {
  cwd: rootDir,
  detached: true,
  stdio: ['ignore', out, out],
  env: childEnv,
});
child.unref();
console.error(`[huanxin_shell:${envName}] Detached browser daemon starter pid=${child.pid}`);
NODE
}

daemon_repair_supported() {
  [[ "$ENV_NAME" == "AI" || "$ENV_NAME" == "ai2" || "$ENV_NAME" == "ai3" || "$ENV_NAME" == "ASI3" ]]
}

daemon_restart_label() {
  if [[ "$ENV_NAME" == "ai2" && "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
    printf '%s' 'supervised daemon'
    return 0
  fi
  printf '%s' 'daemon'
}

standalone_profile_copy_name() {
  if [[ -n "${HUANXIN_PROFILE_DIR:-}" ]]; then
    return 0
  fi

  if [[ "$PROFILE_COPY_NAME_EXPLICIT" == "1" ]]; then
    printf '%s' "$PROFILE_COPY_NAME"
    return 0
  fi

  if [[ "$USE_DAEMON" == "1" ]]; then
    printf 'quantum-rnd-standalone-%s-%s-%s' "$ENV_NAME" "$$" "$(date +%s%N)"
    return 0
  fi

  printf '%s' "$PROFILE_COPY_NAME"
}

start_daemon_if_needed() {
  local repaired=0 health_json=""
  cleanup_stale_daemon_state_if_needed
  if daemon_health_ok; then
    if ! daemon_port_file_ready; then
      printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
    fi
    health_json="$(daemon_health_json)"
    if [[ -n "$health_json" && "$(daemon_non_retryable_shell_failure "$health_json")" == "1" ]]; then
      echo "[huanxin_shell:$ENV_NAME] Existing daemon reports a non-retryable shell endpoint blocker: $(daemon_shell_endpoint_failure_summary "$health_json")" >&2
      return 1
    fi
    if daemon_repair_supported && [[ -n "$health_json" && "$(daemon_needs_local_repair "$health_json")" == "1" ]]; then
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
    start_local_daemon_detached
  fi

  for poll_index in $(seq 1 "$DAEMON_STARTUP_MAX_POLLS"); do
    if daemon_health_ok; then
      if ! daemon_port_file_ready; then
        printf '%s' "$DEFAULT_PORT" > "$DAEMON_PORT_FILE"
      fi
      health_json="$(daemon_health_json)"
      if daemon_repair_supported && [[ -n "$health_json" && "$(daemon_needs_local_repair "$health_json")" == "1" && "$repaired" != "1" ]]; then
        repaired=1
        echo "[huanxin_shell:$ENV_NAME] Daemon boot is stalled on auth; running local repair and restarting $(daemon_restart_label)." >&2
        bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
        if [[ "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
          HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
            bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
          sleep "$DAEMON_STARTUP_POLL_INTERVAL_SECONDS"
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
    sleep "$DAEMON_STARTUP_POLL_INTERVAL_SECONDS"
  done

  echo "[huanxin_shell:$ENV_NAME] Daemon unavailable after startup attempt (polls=$DAEMON_STARTUP_MAX_POLLS interval=${DAEMON_STARTUP_POLL_INTERVAL_SECONDS}s)." >&2
  health_json="$(daemon_health_json)"
  if [[ -n "$health_json" && "$(daemon_non_retryable_shell_failure "$health_json")" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Non-retryable Huanxin shell endpoint blocker: $(daemon_shell_endpoint_failure_summary "$health_json")" >&2
    echo "$health_json" >&2
    return 1
  fi
  if [[ -f "$DAEMON_LOG_FILE" ]]; then
    tail -n 20 "$DAEMON_LOG_FILE" >&2 || true
  fi
  return 1
}

run_daemon_command() {
  if [[ -n "${HUANXIN_DAEMON_HARD_TIMEOUT_MS:-}" && "${HUANXIN_DAEMON_HARD_TIMEOUT_MS}" =~ ^[0-9]+$ && "${HUANXIN_DAEMON_HARD_TIMEOUT_MS}" -gt 0 ]]; then
    python3 - "$ENV_NAME" "$WAIT_MS" "$REMOTE_CMD" "$HUANXIN_DAEMON_HARD_TIMEOUT_MS" <<'PY'
import subprocess
import sys
import threading
import time

env_name, wait_ms, remote_cmd, hard_timeout_ms = sys.argv[1:5]
cmd = [
    "node",
    "browser-automation/huanxin_shell_exec.js",
    env_name,
    "--require-daemon",
    "--wait-ms",
    wait_ms,
    "--command",
    remote_cmd,
]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out_lines = []
err_lines = []

def drain(stream, sink):
    for line in iter(stream.readline, ""):
      sink.append(line)
    stream.close()

threads = [
    threading.Thread(target=drain, args=(proc.stdout, out_lines), daemon=True),
    threading.Thread(target=drain, args=(proc.stderr, err_lines), daemon=True),
]
for thread in threads:
    thread.start()

timeout_s = max(1.0, float(hard_timeout_ms) / 1000.0)
try:
    proc.wait(timeout=timeout_s)
except subprocess.TimeoutExpired:
    proc.kill()
    time.sleep(0.2)
    tail = "".join((err_lines or out_lines)[-20:])
    sys.stderr.write(
        f"[huanxin_shell:{env_name}] daemon transport timed out after {hard_timeout_ms}ms; last output follows:\\n{tail}"
    )
    raise SystemExit(1)

for thread in threads:
    thread.join(timeout=1.0)

stdout = "".join(out_lines)
stderr = "".join(err_lines)
if stderr:
    sys.stderr.write(stderr)
if stdout:
    sys.stdout.write(stdout)
raise SystemExit(proc.returncode)
PY
    return $?
  fi
  node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --require-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD"
}

repair_supervised_daemon_if_needed() {
  local health_json=""
  health_json="$(daemon_health_json)"
  if daemon_repair_supported && [[ -z "$health_json" || "$(daemon_needs_local_repair "$health_json")" == "1" ]]; then
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

daemon_transport_retryable() {
  python3 - <<'PY' "$1"
import json
import sys

try:
    payload = json.loads(sys.argv[1])
except Exception:
    print("0")
    raise SystemExit(0)

error = str(payload.get("error") or "")
retryable = (
    not payload.get("ok", False)
    and (
        "stale_daemon_state_recovered" in error
        or "daemon_processing_interrupted" in error
        or "daemon_file_timeout_processing" in error
        or "daemon_file_timeout_no_response" in error
    )
)
print("1" if retryable else "0")
PY
}

DAEMON_READY=0
FORCE_STANDALONE_RECOVERY=0
if [[ "$USE_DAEMON" == "1" ]] && start_daemon_if_needed && daemon_port_file_ready; then
  DAEMON_READY=1
fi

if [[ "$USE_DAEMON" == "1" && "$DAEMON_READY" == "1" ]]; then
  echo "[huanxin_shell:$ENV_NAME] Using daemon transport." >&2
  repair_supervised_daemon_if_needed
  JSON_OUT="$(run_daemon_command)"
  if daemon_repair_supported && [[ "$(needs_local_repair_retry "$JSON_OUT")" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Detected Safari bridge startup failure in the supervised daemon; running local repair and retrying once." >&2
    bash "$REPAIR_SCRIPT" >/dev/null 2>&1 || true
    if [[ "$USE_DAEMON_AGENT" == "1" && -f "$AI2_DAEMON_AGENT_PLIST" ]] && command -v launchctl >/dev/null 2>&1; then
      HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME" HUANXIN_HEADLESS="${HUANXIN_HEADLESS}" \
        bash "$AI2_DAEMON_AGENT_SCRIPT" --kickstart >/dev/null 2>&1 || true
    fi
    JSON_OUT="$(run_daemon_command)"
  fi
  if [[ "$(daemon_transport_retryable "$JSON_OUT")" == "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Daemon transport hit stale/interrupted file state; cleaning up and retrying once." >&2
    cleanup_stale_daemon_state_if_needed
    if start_daemon_if_needed && daemon_port_file_ready; then
      JSON_OUT="$(run_daemon_command)"
    fi
  fi
else
  if [[ "$USE_DAEMON" == "1" ]]; then
    health_json="$(daemon_health_json)"
    if [[ -n "$health_json" && "$(daemon_non_retryable_shell_failure "$health_json")" == "1" ]]; then
      FORCE_STANDALONE_RECOVERY=1
      echo "[huanxin_shell:$ENV_NAME] Huanxin shell endpoint is unavailable in daemon transport; attempting standalone recovery." >&2
      echo "[huanxin_shell:$ENV_NAME] $(daemon_shell_endpoint_failure_summary "$health_json")" >&2
      echo "$health_json" >&2
    fi
    if [[ -n "$health_json" && "$(daemon_terminal_prompt_failure "$health_json")" == "1" ]]; then
      echo "[huanxin_shell:$ENV_NAME] Shell terminal failed to reach a prompt; refusing slow standalone retry." >&2
      echo "$health_json" >&2
      exit 1
    fi
  fi
  if [[ "$USE_DAEMON" == "1" && "$ALLOW_STANDALONE_FALLBACK" != "1" && "$FORCE_STANDALONE_RECOVERY" != "1" ]]; then
    echo "[huanxin_shell:$ENV_NAME] Refusing standalone fallback because session preservation is required. Set HUANXIN_ALLOW_STANDALONE_FALLBACK=1 only for explicit recovery/debugging." >&2
    exit 1
  fi
  STANDALONE_PROFILE_COPY_NAME="$(standalone_profile_copy_name)"
  if [[ -n "$STANDALONE_PROFILE_COPY_NAME" ]]; then
    export HUANXIN_PROFILE_COPY_NAME="$STANDALONE_PROFILE_COPY_NAME"
    PROFILE_LABEL="profile copy: $HUANXIN_PROFILE_COPY_NAME"
  else
    unset HUANXIN_PROFILE_COPY_NAME
    PROFILE_LABEL="profile dir: ${HUANXIN_PROFILE_DIR:-default}"
  fi
  if [[ "$USE_DAEMON" == "1" ]]; then
    if [[ "$FORCE_STANDALONE_RECOVERY" == "1" ]]; then
      echo "[huanxin_shell:$ENV_NAME] Using standalone transport as recovery from daemon shell-endpoint failure ($PROFILE_LABEL)." >&2
    else
      echo "[huanxin_shell:$ENV_NAME] Using standalone transport only because HUANXIN_ALLOW_STANDALONE_FALLBACK=1 was set ($PROFILE_LABEL)." >&2
    fi
  else
    echo "[huanxin_shell:$ENV_NAME] Using standalone transport because HUANXIN_USE_DAEMON=0 was set ($PROFILE_LABEL)." >&2
  fi
  JSON_OUT="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --skip-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD")"
fi

python3 - <<'PY' "$JSON_OUT" "$ENV_NAME" "$*" "$RUN_MARKER" "$ROOT_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

payload = json.loads(sys.argv[1])
env_name = sys.argv[2]
command = sys.argv[3]
run_marker = sys.argv[4]
root_dir = Path(sys.argv[5])
marker_prefixes = ('__AI1_', '__AI2_', '__AI3_', '__ASI', '__FRESH', '__HX_')
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

status_dir = root_dir / ".huanxin_shell_connections"
status_dir.mkdir(parents=True, exist_ok=True)
status_path = status_dir / f"{env_name}.json"
status_payload = {
    "schema_version": 1,
    "env_name": env_name,
    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    "ok": bool(payload.get("ok")),
    "command_ok": bool(payload.get("commandOk")),
    "command_status": payload.get("commandStatus"),
    "transport": payload.get("transport"),
    "browser_mode": payload.get("browserMode"),
    "url": payload.get("url"),
    "duration_ms": payload.get("durationMs"),
    "output_tail": str(payload.get("output") or "")[-2000:],
}
temp_path = status_path.with_suffix(".json.tmp")
temp_path.write_text(json.dumps(status_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
temp_path.replace(status_path)

print(json.dumps(payload, indent=2))
PY
