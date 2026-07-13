#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "--dry-run" ]]; then
  shift
fi

exec python3 "$ROOT_DIR/scripts/render_asi1_agentic_grpo_runner_spec.py" "$@"
