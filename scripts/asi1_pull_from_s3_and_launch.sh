#!/usr/bin/env bash
# ONE-SHOT: run this INSIDE the Huanxin ASI1 environment.
# Pulls the latest code+data changes from INER S3 onto the persistent NAS, then
# launches the 4-NPU Qwen3.6-27B LoRA SFT on the deduped 1k dataset.
#
# Usage (inside ASI1 webshell):
#   bash /root/work/software/quantum-gpt/scripts/asi1_pull_from_s3_and_launch.sh
set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
S3_ROOT_PATH="software/quantum-gpt"          # bucket-relative root
S3_SYNC_PREFIX="${S3_SYNC_PREFIX:-_pull/npu-sft-fix}"  # where the Mac uploaded the bundle
RCLONE_CONF="/tmp/iner-rclone.conf"

echo "== [1/4] writing rclone config =="
umask 077
cat > "$RCLONE_CONF" <<'__CONF__'
[iner]
type = s3
provider = Other
access_key_id = OXF5ar4y
secret_access_key = __INER_SECRET__
endpoint = https://iner.aihuanxin.cn
acl = private
force_path_style = true
__CONF__
# Secret is injected by the Mac-side packager into this file before upload; if it
# is still the placeholder, fail loudly.
if grep -q '__INER_SECRET__' "$RCLONE_CONF"; then
  echo "ERROR: rclone secret placeholder not filled. Re-run the Mac packager." >&2
  exit 3
fi

RCLONE_BIN="$(command -v rclone || echo /root/work/filestorage/Qwen3.6-27B/rclone-current-linux-arm64/rclone)"
test -x "$RCLONE_BIN" || { echo "rclone not found" >&2; exit 4; }

SRC="iner:${S3_BUCKET}/${S3_ROOT_PATH}/${S3_SYNC_PREFIX}"
echo "== [2/4] pulling code+data from ${SRC} -> ${NAS_ROOT} =="
mkdir -p "$NAS_ROOT"
"$RCLONE_BIN" --config "$RCLONE_CONF" copy "$SRC" "$NAS_ROOT" \
  --s3-force-path-style --progress --transfers 8 --checkers 8

echo "== [3/4] verifying pulled files =="
for f in training/qwen_sft_peft.py \
         scripts/patch_qwen3_5_npu_modeling.py \
         scripts/asi1_launch_1k_sft_4npu.sh \
         data/generated/quantum_finetune_verified_chat_sft_dedup_1k/train_chatml.jsonl \
         data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl; do
  test -s "$NAS_ROOT/$f" || { echo "MISSING after pull: $f" >&2; exit 5; }
  echo "  ok $f"
done
chmod +x "$NAS_ROOT/scripts/asi1_launch_1k_sft_4npu.sh" 2>/dev/null || true

echo "== [4/4] launching 4-NPU SFT =="
cd "$NAS_ROOT"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)" bash scripts/asi1_launch_1k_sft_4npu.sh launch
