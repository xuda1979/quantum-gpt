#!/usr/bin/env bash
set -euo pipefail

LABEL="com.quantumgpt.huanxin-safari-keepalive"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${HOME}/Library/LaunchAgents"
TARGET_PLIST="${TARGET_DIR}/${LABEL}.plist"
SOURCE_PLIST="${ROOT_DIR}/launchd/${LABEL}.plist"
LOG_FILE="${HUANXIN_KEEPALIVE_LAUNCHD_LOG_FILE:-/tmp/huanxin-safari-keepalive.launchd.log}"
INTERVAL_SEC="${HUANXIN_KEEPALIVE_INTERVAL_SEC:-120}"
MODE="install"

usage() {
  cat >&2 <<EOF
Usage:
  scripts/install_huanxin_safari_keepalive_agent.sh [--install|--uninstall|--status]

Installs or manages the per-user LaunchAgent that refreshes the existing Safari
Huanxin train-dev or environment tab in place and relays fresh auth back into
the browser-automation profile so the shell session stays warm.

Environment overrides:
  HUANXIN_KEEPALIVE_INTERVAL_SEC  Refresh interval in seconds (default: 120)
  HUANXIN_KEEPALIVE_LAUNCHD_LOG_FILE  LaunchAgent stdout/stderr log path
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
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

render_plist() {
  python3 - "$ROOT_DIR" "$INTERVAL_SEC" "$LOG_FILE" <<'PY'
import plistlib
import sys

root_dir, interval_sec, log_file = sys.argv[1:]
plist = {
    "Label": "com.quantumgpt.huanxin-safari-keepalive",
    "ProgramArguments": [
        "/bin/bash",
        f"{root_dir}/scripts/huanxin_safari_keepalive.sh",
        "--refresh",
    ],
    "WorkingDirectory": root_dir,
    "RunAtLoad": True,
    "StartInterval": int(interval_sec),
    "StandardOutPath": log_file,
    "StandardErrorPath": log_file,
}
sys.stdout.buffer.write(plistlib.dumps(plist))
PY
}

launchctl_print() {
  launchctl print "gui/$(id -u)/${LABEL}"
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
  install)
    mkdir -p "$TARGET_DIR"
    TMP_PLIST="$(mktemp /tmp/${LABEL}.XXXXXX.plist)"
    trap 'rm -f "$TMP_PLIST"' EXIT
    render_plist > "$TMP_PLIST"
    plutil -lint "$TMP_PLIST" >/dev/null
    cp "$TMP_PLIST" "$TARGET_PLIST"
    launchctl bootout "gui/$(id -u)" "$TARGET_PLIST" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$TARGET_PLIST"
    launchctl kickstart -k "gui/$(id -u)/${LABEL}"
    echo "installed $TARGET_PLIST"
    launchctl_print
    ;;
esac
