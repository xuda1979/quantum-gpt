#!/usr/bin/env bash
set -euo pipefail

ROOT="${ASI1_REMOTE_ROOT:-/workspace}"
MODEL="${ASI1_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
SPLIT_DIR="${ASI1_SPLIT_DIR:-data/generated/quantum_finetune_verified_chat_sft}"
RUN_ID="${ASI1_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${ASI1_OUTPUT_DIR:-outputs/qwen36-35b-w8a8-verified10k-sft-asi1-5n-${RUN_ID}}"
LOG="${ASI1_LOG_PATH:-logs/asi1_verified10k_sft_5n_${RUN_ID}.log}"
STATUS_JSON="${ASI1_STATUS_JSON:-reports/asi1_verified10k_sft_5n_${RUN_ID}_launch.json}"
RCLONE_CONFIG="${ASI1_RCLONE_CONFIG:-/tmp/iner-rclone-asi1.conf}"
S3_ROOT="${ASI1_S3_ROOT:-iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt}"
REMOTE_RCLONE_BIN="${ASI1_REMOTE_RCLONE_BIN:-/root/work/filestorage/rclone-bin}"
NPROC_PER_NODE="${ASI1_NPROC_PER_NODE:-5}"
VISIBLE_DEVICES="${ASI1_VISIBLE_DEVICES:-0,1,2,3,4}"
MASTER_PORT="${ASI1_MASTER_PORT:-29635}"
TARGET_MODULES="${ASI1_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
TARGET_MODULE_REGEX="${ASI1_TARGET_MODULE_REGEX:-}"
TRAINABLE_PARAM_REGEX="${ASI1_TRAINABLE_PARAM_REGEX:-}"
FREEZE_PARAM_REGEX="${ASI1_FREEZE_PARAM_REGEX:-}"
EXTRA_TRAIN_ARGS="${ASI1_EXTRA_TRAIN_ARGS:-}"
RCLONE_PATHS=(
  training
  scripts/preflight_qwen36_ascend_hf_training.py
  "$SPLIT_DIR"
  artifacts/runtime-overlays/qwen35-moe-min
)

mkdir -p "$ROOT"
cd "$ROOT"
mkdir -p logs reports outputs

if [[ "${ASI1_SKIP_SYNC:-0}" != "1" && ! -x "$REMOTE_RCLONE_BIN" ]]; then
  echo "missing remote rclone binary: $REMOTE_RCLONE_BIN" >&2
  exit 1
fi

if [[ "${ASI1_BYPASS_PROXY:-0}" == "1" ]]; then
  export no_proxy=iner.aihuanxin.cn,192.168.0.0/16,127.0.0.1,localhost
  export NO_PROXY="$no_proxy"
  RCLONE_ENV=(env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY)
else
  RCLONE_ENV=(env)
fi

if [[ "${ASI1_SKIP_SYNC:-0}" == "1" ]]; then
  echo "__ASI1_ISQ_DIRECT_SYNC_SKIPPED__ $(date -u +%FT%TZ)"
else
  echo "__ASI1_ISQ_DIRECT_SYNC_START__ $(date -u +%FT%TZ)"
  for sub in "${RCLONE_PATHS[@]}"; do
    mkdir -p "$(dirname "$sub")"
    "${RCLONE_ENV[@]}" \
      "$REMOTE_RCLONE_BIN" copy "${S3_ROOT}/${sub}" "$sub" \
        --config "$RCLONE_CONFIG" --s3-no-check-bucket --no-traverse \
        --transfers 8 --checkers 16 --low-level-retries 1 --retries 1 \
        --contimeout 10s --timeout 60s
  done
  echo "__ASI1_ISQ_DIRECT_SYNC_DONE__ $(date -u +%FT%TZ)"
fi

test -d "$MODEL"
test -s training/qwen_sft_peft.py
test -s "$SPLIT_DIR/train_chatml.jsonl"
test -s "$SPLIT_DIR/eval_chatml.jsonl"
test -s scripts/preflight_qwen36_ascend_hf_training.py
test -d artifacts/runtime-overlays/qwen35-moe-min
python3 - <<'PY'
from pathlib import Path
import json
split = Path("data/generated/quantum_finetune_verified_chat_sft")
train = sum(1 for _ in (split / "train_chatml.jsonl").open())
eval_ = sum(1 for _ in (split / "eval_chatml.jsonl").open())
manifest = json.loads((split / "manifest.json").read_text())
assert train == 10000, train
assert eval_ == 495, eval_
assert manifest.get("source") == "/Users/daxu/quantum_dataset/gen/quantum_finetune_verified.jsonl", manifest.get("source")
assert manifest.get("no_overlap") is True
print(json.dumps({"stage": "dataset_verified", "train_examples": train, "eval_examples": eval_, "no_overlap": True}, ensure_ascii=False), flush=True)
PY
export QUANTUM_TRANSFORMERS_RUNTIME_SRC="${QUANTUM_TRANSFORMERS_RUNTIME_SRC:-artifacts/runtime-overlays/qwen35-moe-min}"
export QUANTUM_HF_HUB_COMPAT_VERSION="${QUANTUM_HF_HUB_COMPAT_VERSION:-0.35.3}"
python3 scripts/preflight_qwen36_ascend_hf_training.py --model-name "$MODEL" --device npu --json

export ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-$VISIBLE_DEVICES}"
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1

echo "__ASI1_ISQ_DIRECT_BEFORE_TRAIN__ $(date -u +%FT%TZ)"
TARGET_MODULE_ARGS=(--target-modules $TARGET_MODULES)
TARGET_MODULE_REGEX_ARGS=()
TRAINABLE_PARAM_REGEX_ARGS=()
FREEZE_PARAM_REGEX_ARGS=()
EXTRA_TRAIN_ARGS_ARRAY=()
if [[ -n "$TARGET_MODULE_REGEX" ]]; then
  # shellcheck disable=SC2206
  TARGET_MODULE_REGEX_ARGS=(--target-module-regex $TARGET_MODULE_REGEX)
fi
if [[ -n "$TRAINABLE_PARAM_REGEX" ]]; then
  # shellcheck disable=SC2206
  TRAINABLE_PARAM_REGEX_ARGS=(--trainable-param-regex $TRAINABLE_PARAM_REGEX)
fi
if [[ -n "$FREEZE_PARAM_REGEX" ]]; then
  # shellcheck disable=SC2206
  FREEZE_PARAM_REGEX_ARGS=(--freeze-param-regex $FREEZE_PARAM_REGEX)
fi
if [[ -n "$EXTRA_TRAIN_ARGS" ]]; then
  # shellcheck disable=SC2206
  EXTRA_TRAIN_ARGS_ARRAY=($EXTRA_TRAIN_ARGS)
fi
mkdir -p "$(dirname "$LOG")" "$(dirname "$STATUS_JSON")" "$OUT"
{
  echo "__ASI1_ISQ_DIRECT_TORCHRUN__ $(date -u +%FT%TZ)"
  echo "root=$ROOT"
  echo "model=$MODEL"
  echo "train_file=$SPLIT_DIR/train_chatml.jsonl"
  echo "eval_file=$SPLIT_DIR/eval_chatml.jsonl"
  echo "visible_devices=$ASCEND_RT_VISIBLE_DEVICES"
  echo "nproc_per_node=$NPROC_PER_NODE"
  echo "output_dir=$OUT"
} >> "$LOG"

nohup torchrun --nproc_per_node="$NPROC_PER_NODE" --master_port="$MASTER_PORT" training/qwen_sft_peft.py \
  --model-name "$MODEL" \
  --train-file "$SPLIT_DIR/train_chatml.jsonl" \
  --eval-file "$SPLIT_DIR/eval_chatml.jsonl" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib 54 \
  --max-length "${ASI1_MAX_LENGTH:-512}" \
  --max-steps "${ASI1_MAX_STEPS:-400}" \
  --num-epochs "${ASI1_NUM_EPOCHS:-3}" \
  --per-device-batch-size "${ASI1_PER_DEVICE_BATCH_SIZE:-1}" \
  --gradient-accumulation-steps "${ASI1_GRAD_ACCUM:-4}" \
  --learning-rate "${ASI1_LEARNING_RATE:-2e-5}" \
  --eval-steps "${ASI1_EVAL_STEPS:-25}" \
  --log-steps "${ASI1_LOG_STEPS:-1}" \
  --lora-rank "${ASI1_LORA_RANK:-64}" \
  --lora-alpha "${ASI1_LORA_ALPHA:-128}" \
  --lora-dropout "${ASI1_LORA_DROPOUT:-0.0}" \
  "${TARGET_MODULE_ARGS[@]}" \
  "${TARGET_MODULE_REGEX_ARGS[@]}" \
  "${TRAINABLE_PARAM_REGEX_ARGS[@]}" \
  "${FREEZE_PARAM_REGEX_ARGS[@]}" \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters "${ASI1_MIN_TRAINABLE_PARAMETERS:-200000000}" \
  --max-trainable-parameters "${ASI1_MAX_TRAINABLE_PARAMETERS:-1000000000}" \
  "${EXTRA_TRAIN_ARGS_ARRAY[@]}" \
  >> "$LOG" 2>&1 &
PID="$!"
echo "$PID" > /tmp/asi1_verified10k_sft_5n.pid
python3 - <<PY
import json
from pathlib import Path
status = {
    "stage": "launched",
    "pid": $PID,
    "run_id": "$RUN_ID",
    "root": "$ROOT",
    "model": "$MODEL",
    "train_file": "$SPLIT_DIR/train_chatml.jsonl",
    "eval_file": "$SPLIT_DIR/eval_chatml.jsonl",
    "train_examples": 10000,
    "eval_examples": 495,
    "visible_devices": "$ASCEND_RT_VISIBLE_DEVICES",
    "nproc_per_node": int("$NPROC_PER_NODE"),
    "log": "$LOG",
    "output_dir": "$OUT",
}
Path("$STATUS_JSON").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\\n")
print(json.dumps(status, ensure_ascii=False), flush=True)
PY
sleep 5
ps -p "$PID" -o pid,ppid,stat,etime,cmd || true
tail -n 80 "$LOG" || true
echo "__ASI1_ISQ_DIRECT_LAUNCHED__ $(date -u +%FT%TZ)"
exit 0

echo "__ASI1_ISQ_DIRECT_AFTER_TRAIN__ $(date -u +%FT%TZ)"

test -f "$OUT/metrics.json"
test -d "$OUT/adapter"
cp "$OUT/metrics.json" reports/asi1_isq_cot_sft_direct_metrics.json
echo "__ASI1_ISQ_DIRECT_DONE__ $(date -u +%FT%TZ)"
