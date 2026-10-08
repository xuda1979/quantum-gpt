#!/usr/bin/env bash
# Base-vs-adapter eval launcher for the ASI1 NPU box (native transformers 5.6.0).
#
# Assumes transformers>=5.6.0 + huggingface_hub>=1.8.0 are installed (qwen3_5_moe
# is native; NO runtime overlay needed). The 35B-A3B MoE base does not fit on one
# 60GB NPU in bf16, so we shard with device_map=auto across all visible NPUs.
#
# Env knobs: LIMIT (0=all 495), MAXNEW (max new tokens), ADAPTER, BASE.
set -uo pipefail
cd /root/work/software/quantum-gpt

# Native transformers ships qwen3_5_moe -> ensure overlay is NOT injected.
export QUANTUM_TRANSFORMERS_RUNTIME_SRC=""
export QG_DEVICE_MAP="${QG_DEVICE_MAP:-auto}"
export QWEN_SFT_ATTN_IMPL=eager
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

BASE="${BASE:-/root/work/filestorage/qwen35b_decompressed_for_training}"
ADAPTER="${ADAPTER:-outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-20260622T040010Z/checkpoints/step-162/adapter}"
EVAL_FILE="${EVAL_FILE:-data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl}"
LIMIT="${LIMIT:-0}"
MAXNEW="${MAXNEW:-768}"

TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT="outputs/eval_base_vs_adapter_${TS}.json"
LOG="logs/eval_base_vs_adapter_${TS}.log"
mkdir -p logs outputs
pkill -f eval_base_vs_adapter 2>/dev/null || true

nohup python3 scripts/eval_base_vs_adapter.py \
  --base "$BASE" --adapter "$ADAPTER" --eval-file "$EVAL_FILE" \
  --out "$OUT" --device npu:0 --max-new-tokens "$MAXNEW" --limit "$LIMIT" \
  > "$LOG" 2>&1 &
PID=$!
echo "$PID" > /tmp/eval_pid.txt
echo "$LOG" > /tmp/eval_log.txt
echo "EVAL_LAUNCHED pid=$PID log=$LOG out=$OUT limit=$LIMIT maxnew=$MAXNEW device_map=$QG_DEVICE_MAP"
