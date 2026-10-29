#!/usr/bin/env bash
# C-10606 (v25): ASI2 LoRA SFT warm-continue from the BANKED CHAMPION adapter
# (v22-resume step-1941, two-leg 18/18 on the old v1 holdout, adapter sha
# 373b6e6d...) — training on the C-10606 v25 NEW-50 corpus:
#   outputs/C10606_v25_train_chatml.jsonl (232 rows, 50 tasks)
#   - train-50 = devslice_v1_55 minus 5 sha-partitioned held-out tasks
#   - ZERO overlap with holdout_v2_18 (the eval gate), holdout_v1_18, and
#     the 5 held-out devslice tasks (gates G1-G5 in c10606_build_v25_corpus.py)
#   - all rows exec-verified against their own frozen tests.py
# Eval for this cycle: sapo_promotion_holdout_v2_18.txt (18 tasks) — the
# clean, frozen, training-disjoint gate — plus the 5 held-out devslice
# tasks as secondary signal. No v1-holdout tasks anywhere in training.
#
# LAUNCH MODE = the champion's mode (v22-resume run_config: world_size=1,
# balanced_npu_device_map over all 8 NPUs, max_length 1536): SINGLE-PROCESS
# python3 with --npu-device-map balanced-layers — NOT 8x torchrun DDP
# (which replicates the full model per NPU and OOMs at max_length 1536).
set -euo pipefail

ROOT=/root/work/quantum-gpt
MODEL_PATH=/root/work/filestorage/Qwen3.8-27B
TRAIN_FILE="$ROOT/outputs/C10606_v25_train_chatml.jsonl"
ADAPTER_INIT="$ROOT/outputs/sft-27b-q38-v22-resume-20261023T081500Z/checkpoints/step-1941/adapter"
RUN_ID="sft-27b-q38-v25-new50-$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_DIR="$ROOT/outputs/$RUN_ID"
LOG_PATH="$ROOT/logs/$RUN_ID.log"
PID_FILE="$OUTPUT_DIR/trainer.pid"
NPU_MAX_MEMORY_GIB_VAL="${NPU_MAX_MEMORY_GIB:-54}"

for f in "$TRAIN_FILE" "$ADAPTER_INIT/adapter_config.json" "$ADAPTER_INIT/adapter_model.safetensors"; do
  [[ -f "$f" ]] || { echo "ERROR: missing $f" >&2; exit 1; }
done
[[ -d "$MODEL_PATH" ]] || { echo "ERROR: model dir missing" >&2; exit 1; }

mkdir -p "$OUTPUT_DIR" "$(dirname "$LOG_PATH")"
echo "$TRAIN_FILE" > "$OUTPUT_DIR/train_data_path.txt"
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

cd "$ROOT"
setsid nohup python3 training/qwen_sft_peft.py \
  --model-name "$MODEL_PATH" \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib "$NPU_MAX_MEMORY_GIB_VAL" \
  --adapter-init "$ADAPTER_INIT" \
  --train-file "$TRAIN_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --max-length 1536 \
  --num-epochs 6 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --max-steps 0 \
  --log-steps 1 \
  --learning-rate 1e-5 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --lora-backend peft \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --max-trainable-parameters 500000000 \
  --min-rms-for-update 0.01 \
  --checkpoint-interval-seconds 300 \
  --overwrite-output-dir \
  > "$LOG_PATH" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"
echo "[launch] run=$RUN_ID pid=$PID"
echo "[launch] log=$LOG_PATH"
echo "[launch] mode=single-proc balanced-layers sharded (world_size=1)"
echo "[launch] adapter_init=$ADAPTER_INIT"
echo "[launch] train_file=$TRAIN_FILE"
