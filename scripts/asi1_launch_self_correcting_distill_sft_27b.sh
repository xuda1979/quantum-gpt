#!/usr/bin/env bash
# ASI1 launcher: Qwen3.6-27B LoRA SFT on the self-correcting-distillation v1 set
# with soft-KL distillation against GLM5.2 teacher top-k logprobs.
#
# Teacher: glm5.2 (per-token top-20 logprobs re-emitted via the OpenAI-compat
#          proxy and captured in data/generated/self_correcting_distill_27b_v1
#          by scripts/self_correcting_distill_27b_iter5.py).
# Student: Qwen3.6-27B with LoRA (rank 16, alpha 32).
# Trainer: training/qwen_sft_peft_kl.py
#   Loss = (1 - kl_coeff) * NLL(student, target_tokens)
#        + kl_coeff * KL(student_top_k || teacher_top_k)
#
# Dataset rows carry a top-level "teacher_logits" field; rows where that field
# is empty (positive samples or re-emit failures) fall back to plain NLL.
#
# Usage:
#   scripts/asi1_launch_self_correcting_distill_sft_27b.sh launch
#   scripts/asi1_launch_self_correcting_distill_sft_27b.sh status
#   scripts/asi1_launch_self_correcting_distill_sft_27b.sh log
#   scripts/asi1_launch_self_correcting_distill_sft_27b.sh kill

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
DATA="${DATA:-data/generated/self_correcting_distill_27b_v1}"
OUT="${OUT:-outputs/qg-27b-self-correcting-distill-sft-${RUN_ID}}"
LOG="${LOG:-$ROOT/logs/qg-27b-self-correcting-distill-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_27b_self_correcting_distill_sft.pid}"
MASTER_PORT="${MASTER_PORT:-29627}"
NPROC="${NPROC:-4}"
ADAPTER_INIT="${ADAPTER_INIT:-outputs/qnt-sft-27b-asi3-r21-20260706T143739Z/adapter}"
MAX_LENGTH="${MAX_LENGTH:-2048}"

# KL hyperparameters (mirror rl_distill_27b_v1 defaults)
KL_COEFF="${KL_COEFF:-0.5}"
NLL_COEFF="${NLL_COEFF:-0.5}"
KL_TEMPERATURE="${KL_TEMPERATURE:-1.0}"
MIN_TEACHER_LOGPROB_TOKENS="${MIN_TEACHER_LOGPROB_TOKENS:-4}"

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
  echo "ERROR: $DATA/train_chatml.jsonl not found. Run the self-correcting distillation pipeline first." >&2
  exit 2
fi

cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-27b-self-correcting-distill-sft-${RUN_ID}",
  "model": "$MODEL",
  "dataset": "$DATA (self-correcting distillation v1, GLM5.2 teacher, per-token top-20 logprobs)",
  "distillation_strategy": "self_correcting_distill_v1",
  "iteration": 5,
  "teacher": "glm5.2",
  "teacher_logprobs": "top-20 per-token, captured via OpenAI-compat re-emit (GLM52_OPENAI_API_BASE)",
  "trainer": "training/qwen_sft_peft_kl.py",
  "kl_coeff": $KL_COEFF,
  "nll_coeff": $NLL_COEFF,
  "kl_temperature": $KL_TEMPERATURE,
  "min_teacher_logprob_tokens": $MIN_TEACHER_LOGPROB_TOKENS,
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

MODEL="${MODEL:-Qwen/Qwen3.6-27B}"

echo "Launching 27B self-correcting-distillation KL-SFT..."
echo "  model: $MODEL"
echo "  output: $OUT"
echo "  log: $LOG"
echo "  adapter_init: $ADAPTER_INIT"
echo "  max_length: $MAX_LENGTH"
echo "  kl_coeff: $KL_COEFF  nll_coeff: $NLL_COEFF  temperature: $KL_TEMPERATURE"

# Launch in the background
nohup torchrun --nproc_per_node="$NPROC" --master_port="$MASTER_PORT" \
  training/qwen_sft_peft_kl.py \
  --model-name "$MODEL" \
  --train-file "$DATA/train_chatml.jsonl" \
  --eval-file "$DATA/eval_chatml.jsonl" \
  --output-dir "$OUT/adapter" \
  --checkpoints-dir "$OUT/checkpoints" \
  --adapter-init "$ADAPTER_INIT" \
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
  --kl_coeff "$KL_COEFF" \
  --nll_coeff "$NLL_COEFF" \
  --temperature "$KL_TEMPERATURE" \
  --teacher_logits_field teacher_logits \
  --min_teacher_logprob_tokens "$MIN_TEACHER_LOGPROB_TOKENS" \
  > "$LOG" 2>&1 &

pid=$!
echo "$pid" > "$PIDFILE"
echo "__LAUNCHED__ pid=$pid out=$OUT"
echo "__LOG__ $LOG"
echo "Monitor: tail -f $LOG"
echo "Status: scripts/asi1_launch_self_correcting_distill_sft_27b.sh status"
