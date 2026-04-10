#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"

if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

MODEL_SUBDIR="${1:-OmniCoder-9B}"
POLL_SECONDS="${POLL_SECONDS:-60}"

if [[ "$MODEL_SUBDIR" == /* ]]; then
  echo "model-subdir must be relative, for example: OmniCoder-9B" >&2
  exit 1
fi

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

cd "$ROOT_DIR"

S3_MODEL_DIR="$S3_ROOT/models/$MODEL_SUBDIR"

while true; do
  ts="$(date '+%F %T %Z')"
  if bash scripts/model_snapshot_s3_ready.sh "$MODEL_SUBDIR" >/dev/null 2>&1; then
    echo "[$ts] detected a complete model snapshot for $MODEL_SUBDIR in S3; starting ai2 model sync"
    bash scripts/ai2_sync_model_from_s3.sh "$MODEL_SUBDIR"
    echo "[$ts] ai2 model sync completed for $MODEL_SUBDIR"
    exit 0
  fi
  echo "[$ts] waiting for a complete model snapshot in $S3_MODEL_DIR"
  sleep "$POLL_SECONDS"
done
