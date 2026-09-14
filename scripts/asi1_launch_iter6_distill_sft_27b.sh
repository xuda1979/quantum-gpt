#!/usr/bin/env bash
# ASI1 launcher: Qwen3.6-27B LoRA SFT on the iter-6 GLM5.2 soft-distillation 100-row set.
#
# Teacher: glm5.2 (logprobs not available from proxy; standard SFT loss used).
# Student: Qwen3.6-27B with LoRA (rank 16, alpha 32).
# Dataset: data/generated/glm52_soft_distill_sft_iter6_27b (100 diversified rows)
#
# Usage:
#   scripts/asi1_launch_iter6_distill_sft_27b.sh launch
#   scripts/asi1_launch_iter6_distill_sft_27b.sh status
#   scripts/asi1_launch_iter6_distill_sft_27b.sh log
#   scripts/asi1_launch_iter6_distill_sft_27b.sh kill

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
DATA="${DATA:-data/generated/glm52_soft_distill_sft_iter6_27b}"
OUT="${OUT:-outputs/qg-27b-iter6-distill-sft-${RUN_ID}}"
LOG="${LOG:-$ROOT/logs/qg-27b-iter6-distill-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_27b_iter6_distill_sft.pid}"
MASTER_PORT="${MASTER_PORT:-29626}"
NPROC="${NPROC:-4}"
ADAPTER_INIT="${ADAPTER_INIT:-outputs/qnt-sft-27b-asi3-r21-20260706T143739Z/adapter}"
MAX_LENGTH="${MAX_LENGTH:-2048}"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd 2>/dev/null || echo NO_PROCESS
  echo '--- log tail ---'; tail -n 60 "$LOG" 2>/dev/null || echo NO_LOG
  echo '--- checkpoints ---'; ls -la "$OUT/checkpoints" 2>/dev/null || echo NONE
  exit 0
elif [[ "$cmd" == "log" ]]; then
  tail -f "$LOG"
  exit 0
elif [[ "$cmd" == "kill" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  if [ -n "$pid" ]; then
    kill "$pid" 2>/dev/null || true
    rm -f "$PIDFILE"
    echo "Killed pid=$pid"
  else
    echo "No PID file"
  fi
  exit 0
fi

mkdir -p "$OUT" "$ROOT/logs"

# Verify dataset exists
if [[ ! -f "$DATA/train_chatml.jsonl" ]]; then
  echo "ERROR: $DATA/train_chatml.jsonl not found. Run scripts/prepare_iter6_distill_sft.py first."
  exit 1
fi

TRAIN_ROWS=$(wc -l < "$DATA/train_chatml.jsonl")
EVAL_ROWS=$(wc -l < "$DATA/eval_chatml.jsonl")
echo "Dataset: $DATA ($TRAIN_ROWS train, $EVAL_ROWS eval)"

# Durable record of exactly what we ran.
cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-27b-iter6-distill-sft-${RUN_ID}",
  "model": "$MODEL",
  "dataset": "$DATA (100 rows, GLM5.2 teacher, iter-6 soft-distillation, diversified)",
  "iteration": 6,
  "teacher": "glm5.2",
  "teacher_logprobs": "not available (proxy does not return logprobs; standard SFT loss)",
  "adapter_init": "$ADAPTER_INIT",
  "lora_rank": 16,
  "lora_alpha": 32,
  "max_length": $MAX_LENGTH,
  "learning_rate": 1e-4,
  "epochs": 3,
  "per_device_batch_size": 1,
  "grad_accum": 4
}
CFG

MODEL="${MODEL:-/root/work/filestorage/Qwen3.8-27B}"

echo "Launching iter-6 27B distillation SFT..."
echo "  model: $MODEL"
echo "  output: $OUT"
echo "  log: $LOG"
echo "  adapter_init: $ADAPTER_INIT"
echo "  max_length: $MAX_LENGTH"

# Launch in the background
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
  --target_modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --learning_rate 1e-4 \
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
echo "Status: scripts/asi1_launch_iter6_distill_sft_27b.sh status"
