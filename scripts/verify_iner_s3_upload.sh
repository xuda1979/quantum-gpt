#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"

DESTINATION="${INER_S3_DESTINATION:-$INER_S3_ROOT}"
CONFIG_PATH="${INER_RCLONE_CONFIG:-/tmp/iner-rclone.conf}"
LIST_LIMIT="${INER_VERIFY_LIST_LIMIT:-80}"

if [[ $# -gt 0 ]]; then
  DESTINATION="$1"
fi

iner_write_rclone_config "$CONFIG_PATH"

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
  "--exclude" ".pytest_cache/**"
  "--exclude" ".mypy_cache/**"
  "--exclude" ".ruff_cache/**"
  "--exclude" ".tmp-home/**"
  "--exclude" ".tmp-rclone/**"
  "--exclude" ".venv/**"
  "--exclude" ".venv-*/**"
  "--exclude" ".local-python/**"
  "--exclude" "skills/iner-s3-transfer/**"
  "--exclude" ".huanxin_manual_mode"
  "--exclude" ".huanxin_automation_enabled"
  "--exclude" ".huanxin_automation_enabled.disabled-*"
  "--exclude" "browser-automation/profile/**"
  "--exclude" "browser-automation/profile.last-known-good/**"
  "--exclude" "browser-automation/*.png"
  "--exclude" "browser-automation/*.html"
  "--exclude" "browser-automation/huanxin-probe.json"
  "--exclude" "models/**"
  "--exclude" "outputs/**"
  "--exclude" "logs/**"
  "--exclude" "data/generated/**"
  "--exclude" "artifacts/ai2_code_docs_snapshot/**"
  "--exclude" "artifacts/runtime-bundles/**"
  "--exclude" "**/__pycache__/**"
  "--exclude" "*.pyc"
  "--exclude" "*.pem"
  "--exclude" "*.key"
  "--exclude" "*secret*"
  "--exclude" "*credentials*"
)

echo "Remote destination: $DESTINATION"
echo
echo "Top-level remote entries:"
rclone lsf "$DESTINATION" \
  "--config" "$CONFIG_PATH" \
  "--s3-no-check-bucket" \
  | head -n "$LIST_LIMIT"

echo
echo "Remote file count and size:"
rclone size "$DESTINATION" \
  "--config" "$CONFIG_PATH" \
  "--s3-no-check-bucket"

echo
echo "Local-to-remote one-way check:"
rclone check "$ROOT_DIR" "$DESTINATION" \
  "--config" "$CONFIG_PATH" \
  "--s3-no-check-bucket" \
  "--one-way" \
  "--size-only" \
  "--fast-list" \
  "--checkers" "16" \
  "${EXCLUDES[@]}"
