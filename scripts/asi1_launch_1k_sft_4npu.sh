#!/usr/bin/env bash
# Hardened ASI1 launcher: Qwen3.6-27B LoRA SFT on the deduped 1k set, 4 NPUs (DDP).
#
# DURABILITY: output-dir MUST be on the persistent NAS (/root/work). The script
# refuses to launch if the output dir is under ephemeral /workspace. Logs and
# run_config also go to NAS. Hourly adapter checkpoints are written to NAS.
#
# NPU FIXES applied before launch:
#   * QWEN_SFT_ATTN_IMPL=eager  -> avoids aclnnFlashAttentionScoreGrad backward.
#   * scripts/patch_qwen3_5_npu_modeling.py -> replaces unsupported depthwise
#     Conv1d backward (Conv2DBackpropInput) with a manual causal conv.
set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"
MODEL="${MODEL:-/root/work/filestorage/Qwen3.6-27B}"
DATA="${DATA:-data/generated/quantum_finetune_verified_chat_sft_dedup_1k}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$NAS_ROOT/outputs/qg-27b-1k-sft-${RUN_ID}}"
LOG="${LOG:-$NAS_ROOT/logs/qg-27b-1k-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_27b_1k_sft_4npu.pid}"
MASTER_PORT="${MASTER_PORT:-29615}"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd 2>/dev/null || echo NO_PROCESS
  echo '--- log tail ---'; tail -n 60 "$LOG" 2>/dev/null || echo NO_LOG
  echo '--- checkpoints ---'; ls -la "$OUT/checkpoints" 2>/dev/null || echo NONE
  exit 0
fi

# --- DURABILITY GUARDRAIL ---
case "$OUT" in
  /root/work/*) : ;;
  *) echo "REFUSING: output dir '$OUT' is not on persistent NAS (/root/work/*)." >&2; exit 2 ;;
esac

mkdir -p "$NAS_ROOT/logs" "$OUT"

# Runtime: transformers 5.6.0 + huggingface_hub 1.8.0 give native qwen3_5.
python3 -c "import transformers,peft,accelerate,huggingface_hub as h; assert transformers.__version__=='5.6.0', transformers.__version__; assert h.__version__=='1.8.0', h.__version__; import transformers.models.qwen3_5; print('__RUNTIME_OK__', transformers.__version__, 'peft', peft.__version__, 'hub', h.__version__)"

# Apply the NPU depthwise-conv backward fix to the installed transformers package.
python3 scripts/patch_qwen3_5_npu_modeling.py

# Preflight files
test -d "$MODEL" || { echo "MISSING model $MODEL" >&2; exit 2; }
test -s training/qwen_sft_peft.py || { echo "MISSING trainer" >&2; exit 2; }
test -s "$DATA/train_chatml.jsonl" || { echo "MISSING train file" >&2; exit 2; }
test -s "$DATA/eval_chatml.jsonl" || { echo "MISSING eval file" >&2; exit 2; }
echo "__PREFLIGHT_OK__ train=$(wc -l < "$DATA/train_chatml.jsonl") eval=$(wc -l < "$DATA/eval_chatml.jsonl") out=$OUT"

# Durable record of exactly what we ran.
cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-27b-1k-sft-${RUN_ID}",
  "model": "$MODEL",
  "dataset": "$DATA (1000 train / 495 eval, deduped, seed 20260622)",
  "epochs": 1,
  "lora_rank": 16,
  "lora_alpha": 32,
  "lora_dropout": 0.05,
  "target_modules": "q_proj v_proj o_proj gate_proj up_proj down_proj (NO k_proj)",
  "learning_rate": 1e-4,
  "lr_scheduler": "cosine",
  "warmup_steps": 6,
  "max_length": 768,
  "per_device_batch_size": 1,
  "grad_accum": 4,
  "train_on_completions_only": true,
  "checkpoint_interval_seconds": 3600,
  "attn_implementation": "eager",
  "npu_conv_patch": "scripts/patch_qwen3_5_npu_modeling.py",
  "visible_devices": "torchrun nproc_per_node=4 DDP (logical 0-3)",
  "transformers": "5.6.0",
  "huggingface_hub": "1.8.0",
  "output_dir": "$OUT"
}
CFG

# NPU fix: eager attention avoids the failing flash-attention backward op.
export QWEN_SFT_ATTN_IMPL=eager
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

nohup torchrun --nproc_per_node=4 --master_port="$MASTER_PORT" training/qwen_sft_peft.py \
  --model-name "$MODEL" \
  --train-file "$DATA/train_chatml.jsonl" \
  --eval-file "$DATA/eval_chatml.jsonl" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --max-length 768 \
  --num-epochs 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 1e-4 \
  --warmup-steps 6 \
  --eval-steps 20 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.05 \
  --lora-backend peft \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --checkpoint-interval-seconds 3600 \
  > "$LOG" 2>&1 &
echo "$!" > "$PIDFILE"
sleep 8
echo "__ASI1_1K_LAUNCHED__ pid=$(cat "$PIDFILE") log=$LOG out=$OUT"
ps -p "$(cat "$PIDFILE")" -o pid,stat,etime,cmd 2>/dev/null || true
echo '--- initial log tail ---'; tail -n 25 "$LOG" 2>/dev/null || true
