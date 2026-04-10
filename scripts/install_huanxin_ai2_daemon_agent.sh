#!/usr/bin/env bash
set -euo pipefail

LABEL="com.quantumgpt.huanxin-ai2-daemon"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${HOME}/Library/LaunchAgents"
TARGET_PLIST="${TARGET_DIR}/${LABEL}.plist"
SOURCE_PLIST="${ROOT_DIR}/launchd/${LABEL}.plist"
LOG_FILE="${HUANXIN_AI2_DAEMON_LAUNCHD_LOG_FILE:-/tmp/huanxin-daemon-ai2.log}"
PROFILE_COPY_NAME="${HUANXIN_PROFILE_COPY_NAME:-quantum-rnd}"
HEADLESS="${HUANXIN_HEADLESS:-1}"
MODE="install"
DAEMON_PID_FILE="/tmp/huanxin-daemon-ai2.pid"
DAEMON_PORT_FILE="/tmp/huanxin-daemon-ai2.port"

usage() {
  cat >&2 <<EOF
Usage:
  scripts/install_huanxin_ai2_daemon_agent.sh [--install|--uninstall|--status|--kickstart]

Installs or manages the per-user LaunchAgent that keeps the Huanxin ai2 browser
daemon alive locally so shell access stays warm and self-healing.

Environment overrides:
  HUANXIN_AI2_DAEMON_LAUNCHD_LOG_FILE  LaunchAgent stdout/stderr log path
  HUANXIN_PROFILE_COPY_NAME            Browser profile copy name (default: quantum-rnd)
  HUANXIN_HEADLESS                     Browser mode flag passed to the daemon (default: 1)
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install)
      MODE="install"
      shift
      ;;
    --uninstall)
      MODE="uninstall"
      shift
      ;;
    --status)
      MODE="status"
      shift
      ;;
    --kickstart)
      MODE="kickstart"
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

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
  echo "node binary not found for Huanxin ai2 daemon agent" >&2
  exit 1
}

render_plist() {
  python3 - "$ROOT_DIR" "$NODE_PATH" "$LOG_FILE" "$PROFILE_COPY_NAME" "$HEADLESS" <<'PY'
import plistlib
import sys

root_dir, node_path, log_file, profile_copy_name, headless = sys.argv[1:]
plist = {
    "Label": "com.quantumgpt.huanxin-ai2-daemon",
    "ProgramArguments": [
        node_path,
        f"{root_dir}/browser-automation/huanxin_browser_daemon.js",
        "ai2",
    ],
    "WorkingDirectory": root_dir,
    "RunAtLoad": True,
    "KeepAlive": True,
    "ThrottleInterval": 5,
    "EnvironmentVariables": {
        "HUANXIN_PROFILE_COPY_NAME": profile_copy_name,
        "HUANXIN_HEADLESS": headless,
    },
    "StandardOutPath": log_file,
    "StandardErrorPath": log_file,
}
sys.stdout.buffer.write(plistlib.dumps(plist))
PY
}

launchctl_print() {
  launchctl print "gui/$(id -u)/${LABEL}"
}

stop_existing_daemon() {
  curl --max-time 2 -sf -X POST http://127.0.0.1:19002/stop >/dev/null 2>&1 || true
  if [[ -f "$DAEMON_PID_FILE" ]]; then
    local existing_pid
    existing_pid="$(cat "$DAEMON_PID_FILE" 2>/dev/null || true)"
    if [[ -n "${existing_pid:-}" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      kill "$existing_pid" 2>/dev/null || true
      for _ in $(seq 1 20); do
        if ! kill -0 "$existing_pid" 2>/dev/null; then
          break
        fi
        sleep 0.5
      done
    fi
  fi
  rm -f "$DAEMON_PID_FILE" "$DAEMON_PORT_FILE"
}

case "$MODE" in
  status)
    if [[ -f "$TARGET_PLIST" ]]; then
      echo "installed_plist=$TARGET_PLIST"
    else
      echo "installed_plist=missing"
    fi
    echo "repo_plist=$SOURCE_PLIST"
    echo "log_file=$LOG_FILE"
    echo "node_path=$NODE_PATH"
    echo "profile_copy_name=$PROFILE_COPY_NAME"
    echo "headless=$HEADLESS"
    set +e
    STATUS_OUTPUT="$(launchctl_print 2>&1)"
    STATUS_CODE=$?
    set -e
    if [[ "$STATUS_CODE" -eq 0 ]]; then
      echo "launchd_state=loaded"
      printf '%s\n' "$STATUS_OUTPUT"
    else
      echo "launchd_state=not_loaded"
      printf '%s\n' "$STATUS_OUTPUT"
    fi
    ;;
  uninstall)
    launchctl bootout "gui/$(id -u)" "$TARGET_PLIST" 2>/dev/null || true
    rm -f "$TARGET_PLIST"
    echo "uninstalled $TARGET_PLIST"
    ;;
  kickstart)
    if [[ ! -f "$TARGET_PLIST" ]]; then
      echo "LaunchAgent is not installed: $TARGET_PLIST" >&2
      exit 1
    fi
    stop_existing_daemon
    set +e
    launchctl_print >/dev/null 2>&1
    STATUS_CODE=$?
    set -e
    if [[ "$STATUS_CODE" -ne 0 ]]; then
      launchctl bootstrap "gui/$(id -u)" "$TARGET_PLIST"
    fi
    launchctl kickstart -k "gui/$(id -u)/${LABEL}"
    echo "kickstarted ${LABEL}"
    launchctl_print
    ;;
  install)
    mkdir -p "$TARGET_DIR"
    TMP_PLIST="$(mktemp /tmp/${LABEL}.XXXXXX.plist)"
    trap 'rm -f "$TMP_PLIST"' EXIT
    render_plist > "$TMP_PLIST"
    plutil -lint "$TMP_PLIST" >/dev/null
    cp "$TMP_PLIST" "$TARGET_PLIST"
    stop_existing_daemon
    launchctl bootout "gui/$(id -u)" "$TARGET_PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$TARGET_PLIST"
    launchctl kickstart -k "gui/$(id -u)/${LABEL}"
    echo "installed $TARGET_PLIST"
    launchctl_print
    ;;
esac
