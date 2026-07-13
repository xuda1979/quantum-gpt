#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"

S3_ROOT="${S3_ROOT:-${HUANXIN_S3_ROOT:-$INER_S3_ROOT}}"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

CONFIG_PATH="${INER_RCLONE_CONFIG:-}"
if [[ -z "$CONFIG_PATH" ]]; then
  TMP_BASE="${TMPDIR:-/tmp}"
  TMP_BASE="${TMP_BASE%/}"
  CONFIG_PATH="$(mktemp "$TMP_BASE/iner-rclone.XXXXXX")"
  CLEANUP_CONFIG=1
else
  CLEANUP_CONFIG=0
fi

cleanup() {
  if [[ "${CLEANUP_CONFIG:-0}" -eq 1 ]]; then
    rm -f "$CONFIG_PATH"
  fi
}
trap cleanup EXIT

cd "$ROOT_DIR"

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

iner_write_rclone_config "$CONFIG_PATH"

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

SOURCE_PATHS=("$@")
if [[ ${#SOURCE_PATHS[@]} -eq 0 ]]; then
  SOURCE_PATHS=(.)
fi

BASE_ARGS=(
  --config "$CONFIG_PATH"
  --s3-no-check-bucket
  --exclude ".git/**"
  --exclude ".git_ssh/**"
  --exclude ".agents/**"
  --exclude ".claude/**"
  --exclude ".env"
  --exclude ".env.*"
  --exclude ".*.env"
  --exclude ".DS_Store"
  --exclude "MEMORY.md"
  --exclude "USER.md"
  --exclude "TOOLS.md"
  --exclude ".openclaw/**"
  --exclude "__pycache__/**"
  --exclude ".pytest_cache/**"
  --exclude ".mypy_cache/**"
  --exclude ".ruff_cache/**"
  --exclude ".tmp-home/**"
  --exclude ".tmp-rclone/**"
  --exclude "*.pyc"
  --exclude "*.npy"
  --exclude "node_modules/**"
  --exclude ".venv/**"
  --exclude "venv/**"
  --exclude ".venv-*/**"
  --exclude ".local-python/**"
  --exclude "skills/iner-s3-transfer/**"
  --exclude "browser-automation/profile/**"
  --exclude "browser-automation/profile.last-known-good/**"
  --exclude ".huanxin_manual_mode"
  --exclude ".huanxin_automation_enabled"
  --exclude ".huanxin_automation_enabled.disabled-*"
  --fast-list
  --progress
  --transfers 8
)

BULKY_ARGS=(
  --exclude "outputs/**"
  --exclude "models/**"
  --exclude "artifacts/**"
  --exclude "memory/**"
  --exclude "logs/**"
  --exclude "data/generated/**"
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
  --exclude "*.pem"
  --exclude "*.key"
  --exclude "*secret*"
  --exclude "*credentials*"
)

if [[ $DRY_RUN -eq 1 ]]; then
  BASE_ARGS+=(--dry-run)
fi

for source_path in "${SOURCE_PATHS[@]}"; do
  if [[ ! -e "$source_path" ]]; then
    echo "missing path: $source_path" >&2
    exit 1
  fi

  REL_PATH="${source_path#./}"

  COPY_ARGS=("${BASE_ARGS[@]}")
  if [[ "$source_path" == "." && $ALLOW_BULKY -eq 0 ]]; then
    COPY_ARGS+=("${BULKY_ARGS[@]}")
  fi

  if [[ "$source_path" == "." ]]; then
    "$RCLONE_BIN" copy . "$S3_ROOT" "${COPY_ARGS[@]}"
  elif [[ -d "$source_path" ]]; then
    "$RCLONE_BIN" copy "$source_path" "$S3_ROOT/$REL_PATH" "${COPY_ARGS[@]}"
  else
    PARENT_REL="$(dirname "$REL_PATH")"
    if [[ "$PARENT_REL" == "." ]]; then
      DEST_DIR="$S3_ROOT"
    else
      DEST_DIR="$S3_ROOT/$PARENT_REL"
    fi
    "$RCLONE_BIN" copy "$source_path" "$DEST_DIR" "${COPY_ARGS[@]}"
  fi
done
