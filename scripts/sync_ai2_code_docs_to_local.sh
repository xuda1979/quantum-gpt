#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_ROOT="${SYNC_DEST_ROOT:-$ROOT_DIR/artifacts/ai2_code_docs_snapshot}"
cd "$ROOT_DIR"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/sync_ai2_code_docs_to_local.sh [--dry-run]

Push selected code/docs from ai2 to S3, then pull them into a local snapshot tree.
Excludes model weights and adapter tensors by design.
EOF
  exit 1
}

DRY_RUN=0
if [[ $# -gt 1 ]]; then
  usage
fi
if [[ $# -eq 1 ]]; then
  case "$1" in
    --dry-run)
      DRY_RUN=1
      ;;
    *)
      usage
      ;;
  esac
fi

sync_paths=(
  scripts
  training
  tests
  evals
  reports
  artifacts/quantum-generalization-command-sheet.txt
  .huanxin_jobs
  AGENTS.md
  SOUL.md
  USER.md
  MEMORY.md
  PROJECT.md
  HEARTBEAT.md
  TOOLS.md
  memory
)

bash_push_args=("${sync_paths[@]}")
bash_pull_args=("${sync_paths[@]}")
if [[ $DRY_RUN -eq 1 ]]; then
  bash_push_args=(--dry-run "${bash_push_args[@]}")
  bash_pull_args=(--dry-run "${bash_pull_args[@]}")
fi

bash scripts/ai2_push_results_to_s3.sh "${bash_push_args[@]}"
mkdir -p "$DEST_ROOT"
SYNC_DEST_ROOT="$DEST_ROOT" bash scripts/pull_from_s3.sh "${bash_pull_args[@]}"
if [[ $DRY_RUN -eq 0 ]]; then
  # Keep snapshot docs portable after sync instead of preserving machine-local file links.
  python3 scripts/check_markdown_links.py "$DEST_ROOT"
fi
printf 'Synced ai2 code/docs snapshot to %s\n' "$DEST_ROOT"
