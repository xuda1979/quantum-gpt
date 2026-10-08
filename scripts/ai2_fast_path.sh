#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI2_SHELL="$ROOT_DIR/scripts/ai2_shell.sh"
AI2_JOB="$ROOT_DIR/scripts/ai2_job.sh"
QUEUE_SCRIPT="$ROOT_DIR/scripts/queue_ai2_timeboxed_pipeline.sh"
STATUS_SCRIPT="$ROOT_DIR/scripts/huanxin_status.sh"
DAEMON_AGENT_SCRIPT="$ROOT_DIR/scripts/install_huanxin_ai2_daemon_agent.sh"
DAEMON_AGENT_PLIST="$HOME/Library/LaunchAgents/com.quantumgpt.huanxin-ai2-daemon.plist"
READY_MARKER="__AI2_FAST_READY__"
DEFAULT_READY_CMD="pwd && python3 --version && echo ${READY_MARKER}"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai2_fast_path.sh status
  scripts/ai2_fast_path.sh ready
  scripts/ai2_fast_path.sh exec "<remote command>"
  scripts/ai2_fast_path.sh job-start <job-name> <log-path> "<remote command>"
  scripts/ai2_fast_path.sh queue-fast [queue_ai2_timeboxed_pipeline args...]

This is the narrow ai2 fast-iteration control path for this workspace:
- supervised daemon only
- no standalone browser fallback
- profile/session repair delegated to ai2_shell.sh
EOF
  exit 1
}

subcommand="${1:-}"
if [[ -z "$subcommand" ]]; then
  usage
fi
shift || true

export HUANXIN_USE_DAEMON="${HUANXIN_USE_DAEMON:-1}"
export HUANXIN_USE_DAEMON_AGENT="${HUANXIN_USE_DAEMON_AGENT:-1}"
export HUANXIN_ALLOW_STANDALONE_FALLBACK=0
export HUANXIN_HEADLESS="${HUANXIN_HEADLESS:-1}"
export HUANXIN_PROFILE_COPY_NAME="${HUANXIN_PROFILE_COPY_NAME:-quantum-rnd}"
export HUANXIN_WAIT_MS="${HUANXIN_WAIT_MS:-180000}"

ensure_supervised_daemon_agent() {
  if command -v launchctl >/dev/null 2>&1; then
    if [[ ! -f "$DAEMON_AGENT_PLIST" ]]; then
      HUANXIN_PROFILE_COPY_NAME="$HUANXIN_PROFILE_COPY_NAME" HUANXIN_HEADLESS="$HUANXIN_HEADLESS" \
        bash "$DAEMON_AGENT_SCRIPT" --install >/dev/null 2>&1 || true
    fi
  fi
}

run_ready_probe() {
  bash "$AI2_SHELL" "$DEFAULT_READY_CMD"
}

case "$subcommand" in
  status)
    [[ $# -eq 0 ]] || usage
    bash "$STATUS_SCRIPT"
    ;;
  ready)
    [[ $# -eq 0 ]] || usage
    ensure_supervised_daemon_agent
    run_ready_probe
    ;;
  exec)
    [[ $# -eq 1 ]] || usage
    ensure_supervised_daemon_agent
    run_ready_probe >/dev/null
    bash "$AI2_SHELL" "$1"
    ;;
  job-start)
    [[ $# -eq 3 ]] || usage
    ensure_supervised_daemon_agent
    run_ready_probe >/dev/null
    bash "$AI2_JOB" start "$1" "$2" "$3"
    ;;
  queue-fast)
    ensure_supervised_daemon_agent
    run_ready_probe >/dev/null
    bash "$QUEUE_SCRIPT" --iteration-profile fast "$@"
    ;;
  *)
    usage
    ;;
esac
