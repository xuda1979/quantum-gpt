#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="$ROOT_DIR/.huanxin_manual_mode"
ENABLE_FILE="$ROOT_DIR/.huanxin_automation_enabled"
PATTERN='browser-automation/huanxin_|scripts/huanxin_|huanxin_shell|huanxin-profile|aihuanxin.cn/auth/realms|kunlun/kl-web'
MODE="status"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_manual_mode.sh [--manual-on|--manual-off|--enable|--disable|--enable-automation|--disable-automation|--status|--kill-local]

Manual mode protects the human-operated Huanxin AI webshell by blocking local
browser automation, Safari keepalive refreshes, profile repair, and AI shell
polling while .huanxin_manual_mode exists.

Automation is disabled by default. Exiting manual mode does not enable browser
automation; use --enable-automation only when Codex is intentionally allowed to
control Huanxin again.
EOF
  exit 1
}

write_lock() {
  cat > "$LOCK_FILE" <<'EOF'
Huanxin manual use lock.

Do not start browser automation against Huanxin while this file exists.
This protects the human's manual Huanxin AI webshell session from refreshes,
terminal reconnects, and lost typed input.

Remove this file only when Huanxin browser automation is intentionally allowed
again.
EOF
  rm -f "$ENABLE_FILE"
}

manual_off() {
  rm -f "$LOCK_FILE"
  rm -f "$ENABLE_FILE"
}

enable_automation() {
  rm -f "$LOCK_FILE"
  cat > "$ENABLE_FILE" <<'EOF'
Huanxin browser automation is explicitly enabled.

This opt-in file allows local Codex helpers to open, refresh, repair, or control
Huanxin browser sessions. Remove this file before human manual webshell use.
EOF
}

disable_automation() {
  rm -f "$ENABLE_FILE"
  write_lock
}

kill_local_automation() {
  local pids
  pids="$(pgrep -f "$PATTERN" 2>/dev/null || true)"
  if [[ -z "$pids" ]]; then
    echo "local_automation=none"
    return 0
  fi
  while IFS= read -r pid; do
    [[ -z "$pid" || "$pid" == "$$" ]] && continue
    kill -TERM "$pid" 2>/dev/null || true
  done <<< "$pids"
  sleep 2
  pids="$(pgrep -f "$PATTERN" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    while IFS= read -r pid; do
      [[ -z "$pid" || "$pid" == "$$" ]] && continue
      kill -KILL "$pid" 2>/dev/null || true
    done <<< "$pids"
  fi
  echo "local_automation=terminated"
}

status() {
  if [[ -f "$LOCK_FILE" ]]; then
    echo "manual_mode=enabled"
    echo "lock_file=$LOCK_FILE"
  else
    echo "manual_mode=disabled"
    echo "lock_file=missing"
  fi
  if [[ -f "$ENABLE_FILE" ]]; then
    echo "browser_automation=enabled"
    echo "enable_file=$ENABLE_FILE"
  else
    echo "browser_automation=disabled"
    echo "enable_file=missing"
  fi
  echo "matching_processes:"
  pgrep -fl "$PATTERN" 2>/dev/null || true
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --enable|--manual-on)
      MODE="manual-on"
      shift
      ;;
    --disable|--manual-off)
      MODE="manual-off"
      shift
      ;;
    --enable-automation)
      MODE="enable-automation"
      shift
      ;;
    --disable-automation)
      MODE="disable-automation"
      shift
      ;;
    --status)
      MODE="status"
      shift
      ;;
    --kill-local)
      MODE="kill-local"
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

case "$MODE" in
  manual-on)
    write_lock
    kill_local_automation
    status
    ;;
  manual-off)
    manual_off
    status
    ;;
  enable-automation)
    enable_automation
    status
    ;;
  disable-automation)
    disable_automation
    status
    ;;
  kill-local)
    kill_local_automation
    status
    ;;
  status)
    status
    ;;
esac
