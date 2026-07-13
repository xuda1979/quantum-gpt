#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo 'Usage: scripts/ai_shell.sh "<remote command>"' >&2
  exit 1
fi

exec bash scripts/huanxin_shell.sh AI "$*"
