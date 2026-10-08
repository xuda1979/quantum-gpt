#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"

DESTINATION="${INER_S3_DESTINATION:-$INER_S3_ROOT}"
CONFIG_PATH="${INER_RCLONE_CONFIG:-}"

DRY_RUN=0
CHECK_EXCLUDES=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --check-excludes)
      CHECK_EXCLUDES=1
      shift
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: upload_quantum_gpt_to_iner_s3.sh [--dry-run] [--check-excludes] [destination]

Environment:
  INER_SECRET_ACCESS_KEY  Required for upload and rclone dry-run.
  INER_ACCESS_KEY_ID      Defaults to the workspace INER key id.
  INER_S3_ENDPOINT        Defaults to https://iner.aihuanxin.cn.
  INER_RCLONE_CONFIG      Optional path for the temporary rclone config.
USAGE
      exit 0
      ;;
    -*)
      echo "unknown option: $1" >&2
      exit 2
      ;;
    *)
      DESTINATION="$1"
      shift
      ;;
  esac
done

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

EXCLUDES=(
  "--exclude" ".git/**"
  "--exclude" ".git_ssh/**"
  "--exclude" ".agents/**"
  "--exclude" ".claude/**"
  "--exclude" ".env"
  "--exclude" ".env.*"
  "--exclude" ".*.env"
  "--exclude" ".DS_Store"
  "--exclude" "MEMORY.md"
  "--exclude" "USER.md"
  "--exclude" "TOOLS.md"
  "--exclude" ".openclaw/**"
  "--exclude" "memory/**"
  "--exclude" "skills/iner-s3-transfer/**"
  "--exclude" ".pytest_cache/**"
  "--exclude" ".mypy_cache/**"
  "--exclude" ".ruff_cache/**"
  "--exclude" ".tmp-home/**"
  "--exclude" ".tmp-rclone/**"
  "--exclude" ".venv/**"
  "--exclude" ".venv-*/**"
  "--exclude" ".local-python/**"
  "--exclude" ".huanxin_manual_mode"
  "--exclude" ".huanxin_automation_enabled"
  "--exclude" ".huanxin_automation_enabled.disabled-*"
  "--exclude" "browser-automation/profile/**"
  "--exclude" "browser-automation/profile.last-known-good/**"
  "--exclude" "browser-automation/*.png"
  "--exclude" "browser-automation/*.html"
  "--exclude" "browser-automation/*.json"
  "--exclude" "browser-automation/node_modules/**"
  "--exclude" "models/**"
  "--exclude" "outputs/**"
  "--exclude" "logs/**"
  "--exclude" "data/generated/**"
  "--exclude" "artifacts/ai2_code_docs_snapshot/**"
  "--exclude" "artifacts/runtime-bundles/**"
  "--exclude" "gemini.html"
  "--exclude" "gemini_content.txt"
  "--exclude" "page-shot.png"
  "--exclude" "**/__pycache__/**"
  "--exclude" "*.pyc"
  "--exclude" "*.npy"
  "--exclude" "*.pt"
  "--exclude" "*.pth"
  "--exclude" "*.bin"
  "--exclude" "*.safetensors"
  "--exclude" "*.ckpt"
  "--exclude" "*.tar"
  "--exclude" "*.zip"
  "--exclude" "*.pem"
  "--exclude" "*.key"
  "--exclude" "*secret*"
  "--exclude" "*credentials*"
)

if [[ $CHECK_EXCLUDES -eq 1 ]]; then
  printf '%s\n' "${EXCLUDES[@]}"
  exit 0
fi

iner_write_rclone_config "$CONFIG_PATH"

ARGS=(
  copy
  "$ROOT_DIR"
  "$DESTINATION"
  "--config" "$CONFIG_PATH"
  "--s3-no-check-bucket"
  "--fast-list"
  "--transfers" "8"
  "--checkers" "16"
  "--progress"
  "${EXCLUDES[@]}"
)

if [[ $DRY_RUN -eq 1 ]]; then
  ARGS+=("--dry-run")
fi

rclone "${ARGS[@]}"
if [[ $DRY_RUN -eq 0 ]]; then
  rclone lsf "$DESTINATION" --config "$CONFIG_PATH" --s3-no-check-bucket | head -50
fi
