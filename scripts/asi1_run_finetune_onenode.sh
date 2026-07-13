#!/usr/bin/env bash
# Single self-contained launcher to run INSIDE the ASI1 train-dev shell.
# Assumes the payload is already extracted under /workspace:
#   /workspace/training/qwen_sft_peft.py
#   /workspace/data/generated/quantum_finetune_verified_chat_sft/{train,eval}_chatml.jsonl
#   /workspace/artifacts/runtime-overlays/qwen35-moe-slim
#   model: /root/work/filestorage/Qwen3.6-35B-A3B-W8A8
#
# Usage (on ASI1):
#   bash /workspace/run_asi1_finetune.sh            # install deps (if needed) + launch
#   bash /workspace/run_asi1_finetune.sh status     # tail log + show process
set -euo pipefail

REMOTE_ROOT=/workspace
# Qwen3.6-27B is a non-quantized bf16 checkpoint (model_type qwen3_5). The
# 35B-A3B-W8A8 variant cannot train on Ascend because its int8 MoE experts hit
# aclnnMm (DT_INT8 unsupported). 27B trains cleanly via the same runtime stack.
MODEL="${ASI1_MODEL:-/root/work/filestorage/Qwen3.6-27B}"
SPLIT_DIR=data/generated/quantum_finetune_verified_chat_sft
RUNTIME_SRC="${ASI1_RUNTIME_SRC:-artifacts/runtime-full}"
RUN_ID="${ASI1_RUN_ID:-20260616}"
OUT="${ASI1_OUTPUT_DIR:-outputs/qwen36-27b-verified10k-sft-${RUN_ID}}"
LOG="${ASI1_LOG_PATH:-logs/asi1_qwen36_27b_verified10k_${RUN_ID}.log}"
PIDFILE=/tmp/asi1_qwen36_27b_sft.pid
VIS="${ASI1_VISIBLE_DEVICES:-0,1,2,3}"

cd "$REMOTE_ROOT"

cmd="${1:-launch}"

if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd || echo NO_PROCESS
  echo '--- log tail ---'
  tail -n 80 "$LOG" 2>/dev/null || echo NO_LOG
  exit 0
fi

mkdir -p logs reports outputs "$OUT"

# Strip macOS AppleDouble files baked into the Mac tar. transformers'
# define_import_structure() reads every *.py in a model dir, and the binary
# ._*.py files cause UnicodeDecodeError, blocking qwen3_5_moe registration.
find /workspace -name '._*' -delete 2>/dev/null || true
find /workspace/artifacts -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true

# Preflight: required files
test -d "$MODEL"                          || { echo "MISSING model: $MODEL" >&2; exit 2; }
test -s training/qwen_sft_peft.py         || { echo "MISSING training/qwen_sft_peft.py" >&2; exit 2; }
test -s "$SPLIT_DIR/train_chatml.jsonl"   || { echo "MISSING $SPLIT_DIR/train_chatml.jsonl" >&2; exit 2; }
test -s "$SPLIT_DIR/eval_chatml.jsonl"    || { echo "MISSING $SPLIT_DIR/eval_chatml.jsonl" >&2; exit 2; }
test -d "$RUNTIME_SRC/transformers/models/qwen3_5_moe" || { echo "MISSING full transformers runtime at $RUNTIME_SRC" >&2; exit 2; }
echo "__PREFLIGHT_OK__ train=$(wc -l < "$SPLIT_DIR/train_chatml.jsonl") eval=$(wc -l < "$SPLIT_DIR/eval_chatml.jsonl")"

# Runtime env: use the full transformers 5.6.0.dev0 source tree (native
# qwen3_5_moe + dataclass PreTrainedConfig). The slim overlay only swapped model
# files onto the incompatible released transformers 4.57.1 base and failed at
# @strict/dataclass registration. Decompress W8A8 -> bf16 at load, shard
# balanced layers across 4 NPUs.
export QUANTUM_TRANSFORMERS_RUNTIME_SRC="$RUNTIME_SRC"
export QUANTUM_HF_HUB_COMPAT_VERSION=1.8.0
export ASCEND_RT_VISIBLE_DEVICES="$VIS"
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1
export QWEN_SFT_DECOMPRESS_COMPRESSED_TENSORS=1

# Dependencies. peft/accelerate are normally already installed. IMPORTANT: do
# NOT let pip auto-resolve them again here -- peft depends on huggingface_hub
# and pip will downgrade hub back to 0.36.x, which breaks the full-source
# @strict config load. So: (1) verify peft/accelerate import *under the runtime
# overlay* (full transformers 5.6.0.dev0, compatible with hub 1.8.0); only
# install with --no-deps if genuinely missing; (2) pin hub 1.8.0 LAST with
# --no-deps so nothing can undo it.
if ! python3 -c "import sys; sys.path.insert(0, '$RUNTIME_SRC'); import peft, accelerate" 2>/dev/null; then
  echo "__INSTALLING_DEPS__"
  python3 -m pip install --no-input --disable-pip-version-check --no-deps peft accelerate 2>&1 | tail -8
fi
# compressed-tensors is required to dequantize the W8A8 (int-quantized) checkpoint
# to bf16 at load (run_compressed=False). Without it the int8 weights reach
# Ascend aclnnMm which rejects DT_INT8.
if ! python3 -c "import sys; sys.path.insert(0, '$RUNTIME_SRC'); import compressed_tensors" 2>/dev/null; then
  echo "__INSTALLING_COMPRESSED_TENSORS__"
  python3 -m pip install --no-input --disable-pip-version-check 'compressed-tensors' 2>&1 | tail -6
fi
# Pin hub 1.8.0 last so any earlier resolver churn cannot leave a downgraded hub.
if [ "$(python3 -c 'import huggingface_hub as h; print(h.__version__)' 2>/dev/null)" != "1.8.0" ]; then
  echo "__INSTALLING_HUB_1_8_0__"
  python3 -m pip install --no-input --disable-pip-version-check --no-deps 'huggingface_hub==1.8.0' 2>&1 | tail -6
fi
python3 -c "import sys; sys.path.insert(0, '$RUNTIME_SRC'); import peft, accelerate, huggingface_hub as h; print('__DEPS_OK__ peft', peft.__version__, 'accelerate', accelerate.__version__, 'hub', h.__version__)"


nohup python3 training/qwen_sft_peft.py \
  --model-name "$MODEL" \
  --train-file "$SPLIT_DIR/train_chatml.jsonl" \
  --eval-file "$SPLIT_DIR/eval_chatml.jsonl" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib 54 \
  --max-length 512 \
  --max-steps 2500 \
  --num-epochs 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 2e-5 \
  --eval-steps 50 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters 5000000 \
  --max-trainable-parameters 2000000000 \
  > "$LOG" 2>&1 &

echo "$!" > "$PIDFILE"
sleep 6
echo "__ASI1_LAUNCHED__ pid=$(cat "$PIDFILE")"
ps -p "$(cat "$PIDFILE")" -o pid,stat,etime,cmd || true
echo '--- initial log tail ---'
tail -n 30 "$LOG" || true
