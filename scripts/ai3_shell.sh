#!/usr/bin/env bash
set -euo pipefail

# Wrapper for Huanxin ai3 shell access via the shared huanxin_shell.sh router.
# ai3 is the second active train-dev environment used for the Qwen3.6-35B-A3B
# agentic-RL run; AI continues to serve the Qwen3.6-27B RAG product.
#
# Usage:
#   scripts/ai3_shell.sh "cd /root/work/quantum-gpt && ls"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo 'Usage: scripts/ai3_shell.sh "<remote command>"' >&2
  exit 1
fi

export HUANXIN_DAEMON_STARTUP_MAX_POLLS="${HUANXIN_DAEMON_STARTUP_MAX_POLLS:-180}"
export HUANXIN_DAEMON_STARTUP_POLL_INTERVAL_SECONDS="${HUANXIN_DAEMON_STARTUP_POLL_INTERVAL_SECONDS:-2}"

exec bash scripts/huanxin_shell.sh ai3 "$*"
