#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PKG="${ASI1_PACKAGE_PATH:-/tmp/asi1_verified10k_package.tgz}"
REMOTE_ENV="${ASI1_ENV_NAME:-ASI1}"
REMOTE_ROOT="${ASI1_REMOTE_ROOT:-/workspace}"
S3_ROOT="${ASI1_S3_ROOT:-iner:jtdlp-21b4208dde424e96b159362ef49c9c96}"
S3_OBJ="${ASI1_S3_OBJECT:-asi1_verified10k_package.tgz}"

run_remote() {
  local cmd="$1"
  HUANXIN_USE_DAEMON=0 HUANXIN_ALLOW_STANDALONE_FALLBACK=1 \
    bash "$ROOT_DIR/scripts/huanxin_env_shell.sh" --env "$REMOTE_ENV" "$cmd"
}

build_package() {
  local stage
  stage="$(mktemp -d /tmp/asi1-verified10k-stage.XXXXXX)"
  mkdir -p "$stage/scripts" "$stage/data/generated" "$stage/artifacts/runtime-overlays/qwen35-moe-min/transformers/models" "$stage/artifacts/runtime-overlays/qwen35-moe-min/transformers/utils"
  cp "$ROOT_DIR/scripts/run_asi1_verified10k_finetune.sh" "$stage/scripts/"
  cp "$ROOT_DIR/scripts/preflight_qwen36_ascend_hf_training.py" "$stage/scripts/"
  rsync -a --delete "$ROOT_DIR/training/" "$stage/training/"
  rsync -a --delete "$ROOT_DIR/data/generated/quantum_finetune_verified_chat_sft/" "$stage/data/generated/quantum_finetune_verified_chat_sft/"
  rsync -a --delete "$ROOT_DIR/artifacts/runtime-overlays/qwen35-moe-min/transformers/models/qwen3_5_moe/" "$stage/artifacts/runtime-overlays/qwen35-moe-min/transformers/models/qwen3_5_moe/"
  cp "$ROOT_DIR/artifacts/runtime-overlays/qwen35-moe-min/transformers/modeling_rope_utils.py" "$stage/artifacts/runtime-overlays/qwen35-moe-min/transformers/"
  cp "$ROOT_DIR/artifacts/runtime-overlays/qwen35-moe-min/transformers/initialization.py" "$stage/artifacts/runtime-overlays/qwen35-moe-min/transformers/"
  cp "$ROOT_DIR/artifacts/runtime-overlays/qwen35-moe-min/transformers/utils/output_capturing.py" "$stage/artifacts/runtime-overlays/qwen35-moe-min/transformers/utils/"
  find "$stage" -name '__pycache__' -type d -prune -exec rm -rf {} +
  tar -C "$stage" -czf "$PKG" .
  rm -rf "$stage"
}

source "$ROOT_DIR/scripts/iner_s3_env.sh"
if [[ ! -f "$PKG" ]]; then
  build_package
fi
CFG="${INER_RCLONE_CONFIG:-/tmp/iner-rclone-asi1-launch.conf}"
iner_write_rclone_config "$CFG"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi
if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo "missing rclone" >&2
  exit 1
fi
[ -f "$PKG" ] || build_package
"$RCLONE_BIN" copyto "$PKG" "$S3_ROOT/$S3_OBJ" --config "$CFG" --s3-no-check-bucket --progress
run_remote "
cd /workspace &&
cat > /tmp/iner-rclone-asi1.conf <<'__CFG__'
[iner]
type = s3
provider = Other
access_key_id = $INER_ACCESS_KEY_ID
secret_access_key = $INER_SECRET_ACCESS_KEY
endpoint = $INER_S3_ENDPOINT
acl = private
force_path_style = true
__CFG__
if [ -x /root/work/filestorage/rclone-bin ]; then RCLONE=/root/work/filestorage/rclone-bin; else RCLONE=\$(command -v rclone); fi &&
\$RCLONE copyto \"$S3_ROOT/$S3_OBJ\" /tmp/asi1_verified10k_package.tgz --config /tmp/iner-rclone-asi1.conf --s3-no-check-bucket --timeout 180s --low-level-retries 1 --retries 1 &&
tar -xzf /tmp/asi1_verified10k_package.tgz -C /workspace &&
chmod +x /workspace/scripts/run_asi1_verified10k_finetune.sh &&
ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1 ASI1_SKIP_SYNC=1 bash /workspace/scripts/run_asi1_verified10k_finetune.sh
"
