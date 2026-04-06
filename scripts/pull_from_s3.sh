#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_ROOT="${SYNC_DEST_ROOT:-$ROOT_DIR}"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

mkdir -p "$DEST_ROOT"
cd "$DEST_ROOT"

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

DRY_RUN=0
ALLOW_BULKY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --all)
      ALLOW_BULKY=1
      shift
      ;;
    *)
      break
      ;;
  esac
done

REMOTE_PATHS=("$@")
if [[ ${#REMOTE_PATHS[@]} -eq 0 ]]; then
  REMOTE_PATHS=(.)
fi

BASE_ARGS=(
  --exclude ".git/**"
  --exclude "__pycache__/**"
  --exclude ".pytest_cache/**"
  --exclude ".mypy_cache/**"
  --exclude ".ruff_cache/**"
  --exclude "*.pyc"
  --exclude "*.npy"
  --exclude "node_modules/**"
  --exclude ".venv/**"
  --exclude "venv/**"
  --fast-list
  --inplace
  --progress
  --transfers 8
)

BULKY_ARGS=(
  --exclude "outputs/**"
  --exclude "models/**"
  --exclude "artifacts/**"
  --exclude "memory/**"
  --exclude "logs/**"
  --exclude "browser-automation/profile/**"
  --exclude "browser-automation/*.png"
  --exclude "browser-automation/*.html"
  --exclude "browser-automation/*.json"
  --exclude "*.pt"
  --exclude "*.pth"
  --exclude "*.bin"
  --exclude "*.safetensors"
  --exclude "*.ckpt"
  --exclude "*.tar"
  --exclude "*.zip"
)

if [[ $DRY_RUN -eq 1 ]]; then
  BASE_ARGS+=(--dry-run)
fi

for remote_path in "${REMOTE_PATHS[@]}"; do
  COPY_ARGS=("${BASE_ARGS[@]}")

  if [[ "$remote_path" == "." && $ALLOW_BULKY -eq 0 ]]; then
    COPY_ARGS+=("${BULKY_ARGS[@]}")
    "$RCLONE_BIN" copy "$S3_ROOT" . "${COPY_ARGS[@]}"
    continue
  fi

  DEST_PATH="${remote_path#./}"
  if [[ "$DEST_PATH" == */*.* || "$DEST_PATH" == *.* ]]; then
    DEST_DIR="$(dirname "$DEST_PATH")"
    mkdir -p "$DEST_DIR"
    "$RCLONE_BIN" copy "$S3_ROOT/$DEST_PATH" "$DEST_DIR" "${COPY_ARGS[@]}"
  else
    mkdir -p "$(dirname "$DEST_PATH")"
    "$RCLONE_BIN" copy "$S3_ROOT/$DEST_PATH" "$DEST_PATH" "${COPY_ARGS[@]}"
  fi
done
