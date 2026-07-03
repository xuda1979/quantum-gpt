#!/usr/bin/env bash
# ONE-SHOT: run this INSIDE the Huanxin ASI1 environment.
# Pulls the GLM5.2 distillation SFT code+data from INER S3 onto the persistent NAS,
# then launches the 4-NPU Qwen3.6-27B LoRA SFT.
#
# Usage (inside ASI1 webshell):
#   bash /root/work/software/quantum-gpt/scripts/asi1_pull_and_launch_glm52_distill_27b.sh
#
# Optional env:
#   ADAPTER_INIT  - path to an existing adapter to continue training from (default: none)
#   INER_S3_BUCKET, S3_SYNC_PREFIX

set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
S3_ROOT_PATH="software/quantum-gpt"
S3_SYNC_PREFIX="${S3_SYNC_PREFIX:-_pull/glm52-distill-v1}"
RCLONE_CONF="/tmp/iner-rclone.conf"

echo "== [1/4] writing rclone config =="
umask 077
cat > "$RCLONE_CONF" <<'__CONF__'
[iner]
type = s3
provider = Other
access_key_id = OXF5ar4y
secret_access_key = tSd2jD1eRx
endpoint = https://iner.aihuanxin.cn
acl = private
force_path_style = true
__CONF__

RCLONE_BIN="$(command -v rclone || echo /root/work/filestorage/Qwen3.6-27B/rclone-current-linux-arm64/rclone)"
test -x "$RCLONE_BIN" || { echo "rclone not found" >&2; exit 4; }

SRC="iner:${S3_BUCKET}/${S3_ROOT_PATH}/${S3_SYNC_PREFIX}"
echo "== [2/4] pulling code+data from ${SRC} -> ${NAS_ROOT} =="
mkdir -p "$NAS_ROOT"
"$RCLONE_BIN" --config "$RCLONE_CONF" copy "$SRC" "$NAS_ROOT" \
  --s3-force-path-style --progress --transfers 8 --checkers 8

echo "== [3/4] verifying pulled files =="
for f in training/qwen_sft_peft.py \
         training/dequantize_moe_w8a8_to_bf16.py \
         scripts/patch_qwen3_5_npu_modeling.py \
         scripts/asi1_launch_glm52_distill_sft_27b.sh \
         data/generated/glm52_soft_distill_sft_100/train_chatml.jsonl \
         data/generated/glm52_soft_distill_sft_100/eval_chatml.jsonl \
         data/generated/glm52_soft_distill_sft_100/manifest.json; do
  test -s "$NAS_ROOT/$f" || { echo "MISSING after pull: $f" >&2; exit 5; }
  echo "  ok $f"
done
chmod +x "$NAS_ROOT/scripts/asi1_launch_glm52_distill_sft_27b.sh" 2>/dev/null || true

echo "== [4/4] launching 4-NPU 27B GLM5.2 distill SFT =="
cd "$NAS_ROOT"
RUN_ID="glm52-distill-27b-$(date -u +%Y%m%dT%H%M%SZ)" \
  bash scripts/asi1_launch_glm52_distill_sft_27b.sh launch
