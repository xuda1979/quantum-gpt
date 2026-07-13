#!/usr/bin/env bash
# =============================================================================
# ASI2 remote runner: pull code from the INER S3 relay, then run LoRA SFT
# finetuning on Qwen3.6-35B-A3B.
#
# RUN THIS INSIDE THE ASI2 TRAIN-DEV CONTAINER (8x NPU), e.g.:
#
#     bash scripts/asi2_pull_and_train_qwen36_lora.sh
#
# It is self-contained: it bootstraps an rclone config, syncs the latest code
# and data from S3 into the remote workspace, runs the Ascend preflight, then
# launches torchrun across all NPUs.
#
# Local code path proven on 2026-06-08 (CPU smoke, tiny model, real ChatML
# split): LoRA targeting + layernorm training + trainable-parameter budget
# enforcement + adapter/metrics save all succeed end-to-end.
# =============================================================================
set -euo pipefail

# ----------------------------------------------------------------------------
# Paths / environment (override via env vars if needed)
# ----------------------------------------------------------------------------
REMOTE_ROOT="${ASI2_REMOTE_ROOT:-/vllm-workspace/quantum-gpt}"
# Use unquantized version to avoid aclnnMm DT_INT8 fallback preflight blocker on Ascend NPU
MODEL_NAME="${ASI2_MODEL_NAME:-/root/work/filestorage/Qwen3.6-27B}"
SPLIT_DIR="${ASI2_SPLIT_DIR:-high_quality_data}"
OUTPUT_DIR="${ASI2_OUTPUT_DIR:-outputs/qwen36-27b-quantum-distill-lora-r32-broad-ln}"
LOG_PATH="${ASI2_LOG_PATH:-logs/asi2_qwen36_27b_lora_r32_broad_ln.log}"

# ----------------------------------------------------------------------------
# S3 relay (INER Huanxin S3-compatible endpoint)
# ----------------------------------------------------------------------------
INER_S3_ENDPOINT="${INER_S3_ENDPOINT:-https://iner.aihuanxin.cn}"
INER_ACCESS_KEY_ID="${INER_ACCESS_KEY_ID:-OXF5ar4y}"
INER_S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
INER_S3_ROOT="${INER_S3_ROOT:-iner:${INER_S3_BUCKET}/software/quantum-gpt}"
# Secret must be provided via env on the remote (do not commit it here).
INER_SECRET_ACCESS_KEY="${INER_SECRET_ACCESS_KEY:-}"

# ----------------------------------------------------------------------------
# Finetuning hyper-parameters — PROPER LoRA budget for a 35B-A3B MoE.
#   rank 32 / alpha 64 LoRA on all attention + MLP projections, plus the
#   per-layer norms. Floor of 40M trainable params ensures this is a
#   substantive finetune (not a token-sized one); ceiling of 600M fails fast
#   if discovery over the MoE expert stack explodes the budget.
# ----------------------------------------------------------------------------
NPROC_PER_NODE="${ASI2_NPROC_PER_NODE:-8}"
MAX_LENGTH="${ASI2_MAX_LENGTH:-2048}"
MAX_STEPS="${ASI2_MAX_STEPS:-400}"
NUM_EPOCHS="${ASI2_NUM_EPOCHS:-3}"
PER_DEVICE_BATCH_SIZE="${ASI2_PER_DEVICE_BATCH_SIZE:-1}"
GRAD_ACCUM="${ASI2_GRAD_ACCUM:-8}"
LEARNING_RATE="${ASI2_LEARNING_RATE:-1e-4}"
EVAL_STEPS="${ASI2_EVAL_STEPS:-25}"
LOG_STEPS="${ASI2_LOG_STEPS:-5}"
LORA_RANK="${ASI2_LORA_RANK:-32}"
LORA_ALPHA="${ASI2_LORA_ALPHA:-64}"
LORA_DROPOUT="${ASI2_LORA_DROPOUT:-0.05}"
TARGET_MODULES="${ASI2_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
MIN_TRAINABLE_PARAMETERS="${ASI2_MIN_TRAINABLE_PARAMETERS:-40000000}"
MAX_TRAINABLE_PARAMETERS="${ASI2_MAX_TRAINABLE_PARAMETERS:-600000000}"

TRAIN_FILE="${SPLIT_DIR%/}/merged_sft_dataset.jsonl"
QUESTIONS_FILE="${SPLIT_DIR%/}/quantum_100_questions_clean.txt"
EVAL_FILE=""

echo "__ASI2_QWEN36_LORA_START__"
date -u +"%Y-%m-%dT%H:%M:%SZ"
python3 --version

# ----------------------------------------------------------------------------
# 1) Bootstrap rclone + config
# ----------------------------------------------------------------------------
if [[ -z "$INER_SECRET_ACCESS_KEY" ]]; then
  echo "ERROR: INER_SECRET_ACCESS_KEY is not set. Export it before running:" >&2
  echo "  export INER_SECRET_ACCESS_KEY=<secret>   # from skills/iner-s3-transfer/SKILL.md" >&2
  exit 2
fi

RCLONE_CONFIG="/tmp/iner-rclone-asi2.conf"
cat > "$RCLONE_CONFIG" <<EOF
[iner]
type = s3
provider = Other
access_key_id = ${INER_ACCESS_KEY_ID}
secret_access_key = ${INER_SECRET_ACCESS_KEY}
endpoint = ${INER_S3_ENDPOINT}
acl = private
force_path_style = true
EOF
chmod 600 "$RCLONE_CONFIG"

if command -v rclone >/dev/null 2>&1; then
  RCLONE_BIN="rclone"
elif [[ -x /root/work/filestorage/rclone-bin ]]; then
  cp /root/work/filestorage/rclone-bin /tmp/rclone && chmod +x /tmp/rclone
  RCLONE_BIN="/tmp/rclone"
elif [[ -x "${REMOTE_ROOT}/tools/preseed/rclone-linux-arm64" ]]; then
  cp "${REMOTE_ROOT}/tools/preseed/rclone-linux-arm64" /tmp/rclone && chmod +x /tmp/rclone
  RCLONE_BIN="/tmp/rclone"
else
  echo "ERROR: rclone not found on remote." >&2
  exit 1
fi
echo "rclone: $RCLONE_BIN"

# ----------------------------------------------------------------------------
# 2) Pull code + data from S3 into the remote workspace
#    (NAS shortcut when the offline mirror is present, then S3 sync for freshness)
# ----------------------------------------------------------------------------
mkdir -p "$REMOTE_ROOT"
if [[ -d /root/work/filestorage/quantum-gpt ]]; then
  echo "NAS mirror detected — copying offline as base..."
  cp -r /root/work/filestorage/quantum-gpt/. "$REMOTE_ROOT"/
fi

# Bypass the container's outbound HTTP proxy for the internal S3 endpoint.
# Without this, Squid intercepts the request and returns HTTP 403 / StatusCode 0.
INER_S3_HOST="${INER_S3_ENDPOINT#*://}"
INER_S3_HOST="${INER_S3_HOST%%/*}"
export no_proxy="${INER_S3_HOST},192.168.0.0/16,127.0.0.1,localhost"
export NO_PROXY="$no_proxy"

echo "Pulling latest code changes and high quality data from S3: $INER_S3_ROOT -> $REMOTE_ROOT"
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
  "$RCLONE_BIN" copy "$INER_S3_ROOT" "$REMOTE_ROOT" \
  --config "$RCLONE_CONFIG" --s3-no-check-bucket --fast-list \
  --transfers 8 --checkers 16 \
  --exclude '.git/**' --exclude '.venv/**' --exclude '.local-python/**' \
  --exclude 'models/**' --exclude 'outputs/**' --exclude 'logs/**' \
  --exclude 'browser-automation/profile/**' \
  --exclude 'browser-automation/profile.last-known-good/**' \
  || [[ $? -eq 6 ]]

cd "$REMOTE_ROOT"

# ----------------------------------------------------------------------------
# 3) Sanity checks
# ----------------------------------------------------------------------------
test -d "$MODEL_NAME"            || { echo "ERROR: model dir missing: $MODEL_NAME" >&2; exit 1; }
test -s training/qwen_sft_peft.py || { echo "ERROR: trainer missing" >&2; exit 1; }
test -s "$TRAIN_FILE"            || { echo "ERROR: train file missing: $TRAIN_FILE" >&2; exit 1; }
test -s "$QUESTIONS_FILE"        || { echo "ERROR: questions file missing: $QUESTIONS_FILE" >&2; exit 1; }

EVAL_ARGS=()
if [[ -n "$EVAL_FILE" && -s "$EVAL_FILE" ]]; then
  EVAL_ARGS+=("--eval-file" "$EVAL_FILE")
fi

rm -rf "$OUTPUT_DIR"
mkdir -p logs reports

# ----------------------------------------------------------------------------
# 4) Ascend / HF training preflight
# ----------------------------------------------------------------------------
python3 scripts/preflight_qwen36_ascend_hf_training.py \
  --model-name "$MODEL_NAME" --device npu --json

# ----------------------------------------------------------------------------
# 5) Launch LoRA SFT finetuning across all NPUs
# ----------------------------------------------------------------------------
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false

echo "__ASI2_QWEN36_LORA_BEFORE_TORCHRUN__"
# shellcheck disable=SC2086
torchrun --nproc_per_node="$NPROC_PER_NODE" \
  training/qwen_sft_peft.py \
  --model-name "$MODEL_NAME" \
  --train-file "$TRAIN_FILE" \
  "${EVAL_ARGS[@]}" \
  --output-dir "$OUTPUT_DIR" \
  --device npu \
  --max-length "$MAX_LENGTH" \
  --max-steps "$MAX_STEPS" \
  --num-epochs "$NUM_EPOCHS" \
  --per-device-batch-size "$PER_DEVICE_BATCH_SIZE" \
  --gradient-accumulation-steps "$GRAD_ACCUM" \
  --learning-rate "$LEARNING_RATE" \
  --eval-steps "$EVAL_STEPS" \
  --log-steps "$LOG_STEPS" \
  --lora-rank "$LORA_RANK" \
  --lora-alpha "$LORA_ALPHA" \
  --lora-dropout "$LORA_DROPOUT" \
  --target-modules $TARGET_MODULES \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters "$MIN_TRAINABLE_PARAMETERS" \
  --max-trainable-parameters "$MAX_TRAINABLE_PARAMETERS" \
  2>&1 | tee "$LOG_PATH"
echo "__ASI2_QWEN36_LORA_AFTER_TORCHRUN__"

# ----------------------------------------------------------------------------
# 6) Verify outputs
# ----------------------------------------------------------------------------
test -f "$OUTPUT_DIR/metrics.json" || { echo "ERROR: metrics.json missing" >&2; exit 1; }
test -d "$OUTPUT_DIR/adapter"      || { echo "ERROR: adapter dir missing" >&2; exit 1; }
cp "$OUTPUT_DIR/metrics.json" reports/asi2_qwen36_27b_lora_metrics.json
echo "Trainable parameter count:"
python3 -c "import json; m=json.load(open('$OUTPUT_DIR/metrics.json')); print(m.get('trainable_parameter_count')); print('budget:', m.get('trainable_parameter_budget'))"
echo "__ASI2_QWEN36_LORA_DONE__"
