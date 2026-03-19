#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo 'Usage: scripts/ai2_shell.sh "<remote command>"' >&2
  exit 1
fi

PROFILE_COPY_NAME="${HUANXIN_PROFILE_COPY_NAME:-quantum-rnd}"
export HUANXIN_PROFILE_COPY_NAME="$PROFILE_COPY_NAME"
export HUANXIN_HEADLESS="${HUANXIN_HEADLESS:-1}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

node browser-automation/huanxin_shell_exec.js ai2 --command "$*"
