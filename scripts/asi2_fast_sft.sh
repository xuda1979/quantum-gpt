#!/usr/bin/env bash
# =============================================================================
# Fast ASI2 SFT launcher: pull only code+data from S3, run LoRA SFT on all NPUs.
# No NAS mirror copy, no full-repo sync, proxy bypassed for the internal S3 host.
# Run inside the ASI2 train-dev container:
#     export INER_SECRET_ACCESS_KEY='<secret>'
#     bash scripts/asi2_fast_sft.sh
# =============================================================================
set -euo pipefail

REMOTE_ROOT="${ASI2_REMOTE_ROOT:-/vllm-workspace/quantum-gpt}"
MODEL_NAME="${ASI2_MODEL_NAME:-/root/work/filestorage/Qwen3.6-27B}"
SPLIT_DIR="${ASI2_SPLIT_DIR:-high_quality_data}"
TRAIN_FILE="${ASI2_TRAIN_FILE:-${SPLIT_DIR%/}/merged_sft_dataset.jsonl}"
EVAL_FILE="${ASI2_EVAL_FILE:-}"
OUTPUT_DIR="${ASI2_OUTPUT_DIR:-outputs/qwen36-27b-quantum-distill-lora-r32-broad-ln}"
LOG_PATH="${ASI2_LOG_PATH:-logs/asi2_qwen36_27b_lora_r32_broad_ln.log}"
METRICS_REPORT="${ASI2_METRICS_REPORT:-reports/asi2_qwen36_lora_metrics.json}"

ENDPOINT="${INER_S3_ENDPOINT:-https://iner.aihuanxin.cn}"
ACCESS_KEY="${INER_ACCESS_KEY_ID:-OXF5ar4y}"
BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
S3_ROOT="${INER_S3_ROOT:-iner:${BUCKET}/software/quantum-gpt}"

if [[ -z "${INER_SECRET_ACCESS_KEY:-}" ]]; then
  echo "ERROR: export INER_SECRET_ACCESS_KEY first" >&2; exit 2
fi

# --- proxy bypass for the internal S3 host (avoids 10x retry stall) ---
HOST="${ENDPOINT#*://}"; HOST="${HOST%%/*}"
export no_proxy="${HOST},192.168.0.0/16,127.0.0.1,localhost"
export NO_PROXY="$no_proxy"
NOPROXY=(env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY)

# --- rclone (use installed binary, else preseed copy) ---
RCLONE="$(command -v rclone || true)"
[[ -z "$RCLONE" && -x /root/work/filestorage/rclone-bin ]] && RCLONE=/root/work/filestorage/rclone-bin
[[ -z "$RCLONE" && -x "${REMOTE_ROOT}/tools/preseed/rclone-linux-arm64" ]] && RCLONE="${REMOTE_ROOT}/tools/preseed/rclone-linux-arm64"
[[ -z "$RCLONE" ]] && { echo "ERROR: rclone not found" >&2; exit 1; }

CONF="/tmp/iner-rclone-asi2.conf"
cat > "$CONF" <<EOF
[iner]
type = s3
provider = Other
access_key_id = ${ACCESS_KEY}
secret_access_key = ${INER_SECRET_ACCESS_KEY}
endpoint = ${ENDPOINT}
acl = private
force_path_style = true
EOF
chmod 600 "$CONF"

echo "__ASI2_FAST_SFT_START__"; date -u +"%Y-%m-%dT%H:%M:%SZ"

# --- get code + data: try S3 (fail-fast), else fall back to local NAS mirror ---
# S3 is often unreachable from inside ASI2 (proxy 403 / direct 443 timeout), so
# we cap every S3 call hard and never block training on it.
mkdir -p "$REMOTE_ROOT"
NAS_MIRROR="/root/work/filestorage/quantum-gpt"
S3_OK=0
for sub in training scripts "$SPLIT_DIR"; do
  echo "pull $sub from S3 (fail-fast) ..."
  if "${NOPROXY[@]}" "$RCLONE" copy "${S3_ROOT}/${sub}" "${REMOTE_ROOT}/${sub}" \
       --config "$CONF" --s3-no-check-bucket --no-traverse \
       --transfers 16 --checkers 32 \
       --low-level-retries 1 --retries 1 --contimeout 5s --timeout 10s \
       --exclude '*.png' --exclude '*.html' --exclude '__pycache__/**' --exclude '*.pyc'; then
    S3_OK=1
  else
    echo "S3 pull of $sub failed/timeout — will use NAS mirror." >&2
  fi
done

if [[ "$S3_OK" -ne 1 ]]; then
  if [[ -d "$NAS_MIRROR" ]]; then
    echo "Using NAS mirror: $NAS_MIRROR -> $REMOTE_ROOT"
    for sub in training scripts "$SPLIT_DIR"; do
      [[ -d "${NAS_MIRROR}/${sub}" ]] && cp -ru "${NAS_MIRROR}/${sub}/." "${REMOTE_ROOT}/${sub}/" 2>/dev/null || true
    done
  else
    echo "WARN: S3 unreachable and no NAS mirror at $NAS_MIRROR. Using whatever is already in $REMOTE_ROOT." >&2
  fi
fi

cd "$REMOTE_ROOT"
test -d "$MODEL_NAME"             || { echo "ERROR: model missing: $MODEL_NAME" >&2; exit 1; }
test -s training/qwen_sft_peft.py || { echo "ERROR: trainer missing" >&2; exit 1; }
test -s "$TRAIN_FILE"             || { echo "ERROR: train file missing: $TRAIN_FILE" >&2; exit 1; }
EVAL_ARGS=()
if [[ -n "$EVAL_FILE" ]]; then
  test -s "$EVAL_FILE" || { echo "ERROR: eval file missing: $EVAL_FILE" >&2; exit 1; }
  EVAL_ARGS=(--eval-file "$EVAL_FILE")
fi

rm -rf "$OUTPUT_DIR"; mkdir -p logs reports
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false

echo "__ASI2_FAST_SFT_BEFORE_TORCHRUN__"
torchrun --nproc_per_node="${ASI2_NPROC_PER_NODE:-8}" \
  training/qwen_sft_peft.py \
  --model-name "$MODEL_NAME" \
  --train-file "$TRAIN_FILE" \
  "${EVAL_ARGS[@]}" \
  --output-dir "$OUTPUT_DIR" \
  --device npu \
  --max-length "${ASI2_MAX_LENGTH:-2048}" \
  --max-steps "${ASI2_MAX_STEPS:-400}" \
  --num-epochs "${ASI2_NUM_EPOCHS:-3}" \
  --per-device-batch-size "${ASI2_PER_DEVICE_BATCH_SIZE:-1}" \
  --gradient-accumulation-steps "${ASI2_GRAD_ACCUM:-8}" \
  --learning-rate "${ASI2_LEARNING_RATE:-1e-4}" \
  --eval-steps "${ASI2_EVAL_STEPS:-25}" \
  --log-steps "${ASI2_LOG_STEPS:-5}" \
  --lora-rank "${ASI2_LORA_RANK:-32}" \
  --lora-alpha "${ASI2_LORA_ALPHA:-64}" \
  --lora-dropout "${ASI2_LORA_DROPOUT:-0.05}" \
  --target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters "${ASI2_MIN_TRAINABLE_PARAMETERS:-40000000}" \
  --max-trainable-parameters "${ASI2_MAX_TRAINABLE_PARAMETERS:-600000000}" \
  2>&1 | tee "$LOG_PATH"
echo "__ASI2_FAST_SFT_AFTER_TORCHRUN__"

test -f "$OUTPUT_DIR/metrics.json" || { echo "ERROR: metrics.json missing" >&2; exit 1; }
test -d "$OUTPUT_DIR/adapter"      || { echo "ERROR: adapter dir missing" >&2; exit 1; }
cp "$OUTPUT_DIR/metrics.json" "$METRICS_REPORT"
echo "__ASI2_FAST_SFT_DONE__"
