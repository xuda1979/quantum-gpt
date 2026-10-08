#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_NAME="${ASI1_ISQ_UPLOAD_ENV:-ASI1}"
SOURCE_PATH="${ASI1_ISQ_UPLOAD_SOURCE:-isq_train_cot.json}"
REMOTE_PATH="${ASI1_ISQ_UPLOAD_REMOTE_PATH:-/root/work/software/quantum-gpt/isq_train_cot.json}"
CHUNK_BYTES="${ASI1_ISQ_UPLOAD_CHUNK_BYTES:-24000}"
CHUNKS_PER_COMMAND="${ASI1_ISQ_UPLOAD_CHUNKS_PER_COMMAND:-6}"
MAX_BYTES="${ASI1_ISQ_UPLOAD_MAX_BYTES:-25000000}"

exec bash scripts/huanxin_upload_small_file.sh \
  --env "$ENV_NAME" \
  --source "$SOURCE_PATH" \
  --remote-path "$REMOTE_PATH" \
  --max-bytes "$MAX_BYTES" \
  --chunk-bytes "$CHUNK_BYTES" \
  --chunks-per-command "$CHUNKS_PER_COMMAND"
