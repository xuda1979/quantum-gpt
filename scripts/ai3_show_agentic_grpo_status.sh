#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_ROOT="${AI3_REMOTE_ROOT:-/root/work/quantum-gpt}"

if [[ $# -lt 1 ]]; then
  echo 'Usage: scripts/ai3_show_agentic_grpo_status.sh <remote-output-dir>' >&2
  exit 1
fi

REMOTE_OUTPUT_DIR="$1"
if [[ "$REMOTE_OUTPUT_DIR" == /* ]]; then
  REMOTE_OUTPUT_REL="${REMOTE_OUTPUT_DIR#${REMOTE_ROOT}/}"
else
  REMOTE_OUTPUT_REL="$REMOTE_OUTPUT_DIR"
fi

exec bash "$ROOT_DIR/scripts/ai3_shell.sh" \
  "cd '$REMOTE_ROOT' && python3 scripts/show_agentic_grpo_status.py '$REMOTE_OUTPUT_REL'"
