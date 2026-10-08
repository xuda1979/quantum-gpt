#!/usr/bin/env bash
set -euo pipefail

cd /root/work/software/quantum-gpt

export QUANTUM_TRANSFORMERS_RUNTIME_SRC=artifacts/runtime-overlays/qwen35-moe-min
python3 - <<'PY'
from training.runtime_overlay import configure_runtime_overlay_from_env, register_qwen35_moe_runtime

configure_runtime_overlay_from_env()
print("REG_OK", bool(register_qwen35_moe_runtime()), flush=True)
PY

LOG=logs/qwen36_35b_w8a8_verified10k_sft_4n_0615.log
OUT=outputs/qwen36-35b-a3b-w8a8-verified10k-sft-4n-0615
MODEL=/root/work/filestorage/Qwen3.6-35B-A3B-W8A8
rm -f "$LOG"

export ASCEND_RT_VISIBLE_DEVICES=0,5,6,7
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1

nohup torchrun --nproc_per_node=4 --master_port=29720 training/qwen_sft_peft.py \
  --model-name "$MODEL" \
  --train-file data/generated/quantum_finetune_verified_chat_sft/train_chatml.jsonl \
  --eval-file data/generated/quantum_finetune_verified_chat_sft/eval_chatml.jsonl \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --max-length 512 \
  --max-steps 400 \
  --num-epochs 3 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 2e-5 \
  --eval-steps 25 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --lora-backend native \
  --target-modules q_proj v_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --min-trainable-parameters 500000 \
  --max-trainable-parameters 10000000 \
  > "$LOG" 2>&1 &

echo $! > /tmp/asi1_verified10k_sft_4n.pid
echo "__ASI1_VERIFY10K_SCRIPT_LAUNCHED__ pid=$(cat /tmp/asi1_verified10k_sft_4n.pid)"
