#!/usr/bin/env bash
# ASI2 launcher: Qwen3.6-35B-A3B LoRA SFT on the iter-4 GLM5.2 soft-distillation 100-row set.
#
# Teacher: glm5.2 (top-20 logprobs preserved in source file for future soft-KL trainer).
# Student: Qwen3.6-35B-A3B (W8A8 decompressed to bf16) with LoRA (rank 16, alpha 32).
# Dataset: data/generated/glm52_soft_distill_sft_iter4_35b/ (100 rows targeting verified gaps)
# adapter_init: iter-2 weights (continuous improvement)
#
# Usage:
#   scripts/asi2_launch_iter4_distill_sft_35b.sh launch   # start training
#   scripts/asi2_launch_iter4_distill_sft_35b.sh status   # check status
#
# Environment overrides:
#   NPROC=2 (default 2 NPUs)
#   ADAPTER_INIT=outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter
#   MAX_LENGTH=2048
#   DATA=data/generated/glm52_soft_distill_sft_iter4_35b

set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"
MODEL="${MODEL:-/root/work/filestorage/Qwen3.6-35B-A3B}"
DATA="${DATA:-data/generated/glm52_soft_distill_sft_iter4_35b}"
RUN_ID="${RUN_ID:-iter4-distill-35b-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$NAS_ROOT/outputs/qg-35b-iter4-distill-sft-${RUN_ID}}"
LOG="${LOG:-$NAS_ROOT/logs/qg-35b-iter4-distill-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_35b_iter4_distill_sft.pid}"
MASTER_PORT="${MASTER_PORT:-29626}"
NPROC="${NPROC:-2}"
ADAPTER_INIT="${ADAPTER_INIT:-outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter}"
MAX_LENGTH="${MAX_LENGTH:-2048}"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd 2>/dev/null || echo NO_PROCESS
  echo '--- log tail ---'; tail -n 60 "$LOG" 2>/dev/null || echo NO_LOG
  echo '--- checkpoints ---'; ls -la "$OUT/checkpoints" 2>/dev/null || echo NONE
  echo '--- adapter ---'; ls -la "$OUT/adapter" 2>/dev/null || echo NONE
  exit 0
fi

# --- DURABILITY GUARDRAIL ---
case "$OUT" in
  /root/work/*) : ;;
  *) echo "REFUSING: output dir '$OUT' is not on persistent NAS (/root/work/*)." >&2; exit 2 ;;
esac

mkdir -p "$OUT" "$(dirname "$LOG")"

# Preflight: transformers + NPU modeling patch
python3 -c "import transformers; print('transformers', transformers.__version__)" \
  || { echo "FATAL: transformers not installed" >&2; exit 2; }

# Apply the NPU depthwise-conv backward fix to the installed transformers package.
python3 scripts/patch_qwen3_5_npu_modeling.py

# Preflight files
test -d "$MODEL" || { echo "MISSING model $MODEL" >&2; exit 2; }
test -s training/qwen_sft_peft.py || { echo "MISSING trainer" >&2; exit 2; }
test -s "$DATA/train_chatml.jsonl" || { echo "MISSING train file" >&2; exit 2; }
test -s "$DATA/eval_chatml.jsonl" || { echo "MISSING eval file" >&2; exit 2; }
if [[ -n "$ADAPTER_INIT" ]]; then
  test -f "$ADAPTER_INIT/adapter_config.json" || { echo "MISSING adapter_init $ADAPTER_INIT/adapter_config.json" >&2; exit 2; }
fi
echo "__PREFLIGHT_OK__ train=$(wc -l < "$DATA/train_chatml.jsonl") eval=$(wc -l < "$DATA/eval_chatml.jsonl") out=$OUT adapter_init=${ADAPTER_INIT:-none}"

# Durable record of exactly what we ran.
cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-35b-iter4-distill-sft-${RUN_ID}",
  "model": "$MODEL",
  "dataset": "$DATA (100 rows, GLM5.2 teacher, iter-4 soft-distillation)",
  "iteration": 4,
  "teacher": "glm5.2",
  "teacher_logprobs": true,
  "teacher_top_logprobs": 20,
  "adapter_init": "$ADAPTER_INIT",
  "lora_rank": 16,
  "lora_alpha": 32,
  "lora_dropout": 0.05,
  "target_modules": "q_proj k_proj v_proj o_proj gate_proj up_proj down_proj",
  "learning_rate": 5e-6,
  "lr_scheduler": "cosine",
  "warmup_steps": 4,
  "max_length": $MAX_LENGTH,
  "per_device_batch_size": 1,
  "grad_accum": 4,
  "train_on_completions_only": true,
  "checkpoint_interval_seconds": 900,
  "attn_implementation": "eager",
  "npu_conv_patch": "scripts/patch_qwen3_5_npu_modeling.py",
  "transformers": "5.6.0",
  "source_gap_report": "docs/iter4-comprehensive-eval-report-2026-07-16.md",
  "plan": "docs/iter4-distill-sft-plan-2026-07-16.md"
}
CFG

# Launch training in the background
nohup torchrun --nproc_per_node="$NPROC" --master_port="$MASTER_PORT" \
  training/qwen_sft_peft.py \
  --model "$MODEL" \
  --train_file "$DATA/train_chatml.jsonl" \
  --eval_file "$DATA/eval_chatml.jsonl" \
  --output_dir "$OUT/adapter" \
  --checkpoints_dir "$OUT/checkpoints" \
  --adapter_init "$ADAPTER_INIT" \
  --lora_rank 16 \
  --lora_alpha 32 \
  --lora_dropout 0.05 \
  --target_modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --learning_rate 5e-6 \
  --lr_scheduler cosine \
  --warmup_steps 4 \
  --max_length "$MAX_LENGTH" \
  --per_device_batch_size 1 \
  --grad_accum 4 \
  --train_on_completions_only \
  --checkpoint_interval_seconds 900 \
  --attn_implementation eager \
  > "$LOG" 2>&1 &

pid=$!
echo "$pid" > "$PIDFILE"
echo "__LAUNCHED__ pid=$pid out=$OUT"
echo "__LOG__ $LOG"
echo "Monitor: tail -f $LOG"
echo "Status: scripts/asi2_launch_iter4_distill_sft_35b.sh status"
