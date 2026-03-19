#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

cd "$ROOT_DIR"

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

RCLONE_ARGS=(
  copy . "$S3_ROOT"
  --exclude ".git/**"
  --exclude "__pycache__/**"
  --exclude "*.pyc"
  --exclude "*.npy"
  --exclude "node_modules/**"
  --exclude "browser-automation/profile/**"
  --progress
  --transfers 8
)

if [[ "${1:-}" == "--dry-run" ]]; then
  RCLONE_ARGS+=(--dry-run)
fi

"$RCLONE_BIN" "${RCLONE_ARGS[@]}"
