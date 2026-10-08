#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/relay_model_snapshot_to_s3.sh <model-subdir> [--local-dir <path>] [--expected-family-substring <family>] [--dry-run]

Examples:
  scripts/relay_model_snapshot_to_s3.sh gemma-4-31B-it
  scripts/relay_model_snapshot_to_s3.sh Qwen2.5-1.5B-Instruct --local-dir /path/to/snapshot --expected-family-substring qwen
  POLL_SECONDS=30 scripts/relay_model_snapshot_to_s3.sh gemma-4-31B-it --dry-run
EOF
  exit 1
}

if [[ $# -lt 1 ]]; then
  usage
fi

MODEL_SUBDIR="$1"
shift

if [[ "$MODEL_SUBDIR" == /* ]]; then
  echo "model-subdir must be relative, for example: gemma-4-31B-it" >&2
  exit 1
fi

LOCAL_MODEL_DIR_OVERRIDE=""
EXPECTED_FAMILY_SUBSTRING_OVERRIDE=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --local-dir)
      LOCAL_MODEL_DIR_OVERRIDE="${2:-}"
      shift 2
      ;;
    --expected-family-substring)
      EXPECTED_FAMILY_SUBSTRING_OVERRIDE="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      usage
      ;;
  esac
done

infer_expected_family_substring() {
  local lowered
  lowered="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
  case "$lowered" in
    *gemma*) printf '%s' 'gemma' ;;
    *qwen*|*omnicoder*) printf '%s' 'qwen' ;;
    *) printf '%s' '' ;;
  esac
}

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

POLL_SECONDS="${POLL_SECONDS:-60}"
LOCAL_MODEL_DIR="${LOCAL_MODEL_DIR_OVERRIDE:-$ROOT_DIR/models/$MODEL_SUBDIR}"
EXPECTED_FAMILY_SUBSTRING="${EXPECTED_FAMILY_SUBSTRING_OVERRIDE:-$(infer_expected_family_substring "$MODEL_SUBDIR")}"
S3_MODEL_DIR="$S3_ROOT/models/$MODEL_SUBDIR"
MODEL_RELAY_TRANSFERS="${MODEL_RELAY_TRANSFERS:-8}"
MODEL_RELAY_MULTI_THREAD_STREAMS="${MODEL_RELAY_MULTI_THREAD_STREAMS:-8}"
MODEL_RELAY_MULTI_THREAD_CUTOFF="${MODEL_RELAY_MULTI_THREAD_CUTOFF:-256M}"
MODEL_RELAY_MULTI_THREAD_CHUNK_SIZE="${MODEL_RELAY_MULTI_THREAD_CHUNK_SIZE:-64M}"
MODEL_RELAY_S3_UPLOAD_CONCURRENCY="${MODEL_RELAY_S3_UPLOAD_CONCURRENCY:-8}"
MODEL_RELAY_S3_CHUNK_SIZE="${MODEL_RELAY_S3_CHUNK_SIZE:-64M}"

if [[ ! -d "$LOCAL_MODEL_DIR" ]]; then
  echo "local model dir not found: $LOCAL_MODEL_DIR" >&2
  exit 1
fi

COPY_ARGS=(
  --copy-links
  --s3-no-check-bucket
  --exclude ".cache/**"
  --exclude "__pycache__/**"
  --exclude "*.pyc"
  --exclude "*.tmp"
  --exclude "*.incomplete"
  --exclude "*.lock"
  --stats-one-line-date
  --stats 30s
  --progress
  --transfers "$MODEL_RELAY_TRANSFERS"
  --multi-thread-cutoff "$MODEL_RELAY_MULTI_THREAD_CUTOFF"
  --multi-thread-streams "$MODEL_RELAY_MULTI_THREAD_STREAMS"
  --multi-thread-chunk-size "$MODEL_RELAY_MULTI_THREAD_CHUNK_SIZE"
  --s3-upload-concurrency "$MODEL_RELAY_S3_UPLOAD_CONCURRENCY"
  --s3-chunk-size "$MODEL_RELAY_S3_CHUNK_SIZE"
)

if [[ $DRY_RUN -eq 1 ]]; then
  COPY_ARGS+=(--dry-run)
fi

verify_local_snapshot() {
  if python3 "$ROOT_DIR/training/verify_qwen_snapshot.py" \
    "$LOCAL_MODEL_DIR" \
    --expected-substring "$MODEL_SUBDIR" \
    --expected-family-substring "$EXPECTED_FAMILY_SUBSTRING" \
    >/tmp/relay_model_snapshot_verify.json 2>&1; then
    return 0
  fi
  return 1
}

while true; do
  ts="$(date '+%F %T %Z')"
  echo "[$ts] relaying completed files from $LOCAL_MODEL_DIR to $S3_MODEL_DIR"
  "$RCLONE_BIN" copy "$LOCAL_MODEL_DIR" "$S3_MODEL_DIR" "${COPY_ARGS[@]}"

  if verify_local_snapshot; then
    echo "[$ts] local snapshot verifies cleanly; relay is complete"
    exit 0
  fi

  if [[ -f /tmp/relay_model_snapshot_verify.json ]]; then
    echo "[$ts] verifier_status: $(tr '\n' ' ' < /tmp/relay_model_snapshot_verify.json | cut -c1-400)"
  fi
  echo "[$ts] local snapshot still incomplete; sleeping ${POLL_SECONDS}s"
  sleep "$POLL_SECONDS"
done
