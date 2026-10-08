#!/usr/bin/env bash
# ASI1 launcher: Doubly-Robust GRPO for Qwen3.6-27B on 2 NPUs.
#
# This wraps the existing GRPO trainer (training/grpo_trainer.py) with
# the `doubly_robust_quantum_grpo` research-method plugin. It does NOT
# use the RL-distill loop (scripts/asi1_launch_rl_distill_27b_2npu.sh);
# it is a single-phase GRPO run on the existing quantum-coding
# benchmark, which is the right shape for a controlled A/B against
# base GRPO.
#
# Architecture
# ------------
#   NPU 0,1  -> torchrun --nproc_per_node=2 training/grpo_trainer.py
#   (no vLLM server; the trainer loads the model directly with LoRA)
#
# Inputs
# ------
#   MODEL                       : path to Qwen3.6-27B (or compatible) base
#   BENCHMARK_FILE              : path to a quantum GRPO training benchmark
#   OUTPUT_DIR                  : where to write checkpoints + metrics
#   ADAPTER_INIT (optional)     : warm-start from a prior LoRA adapter
#   RESEARCH_METHODS            : defaults to "doubly_robust_quantum_grpo"
#   DR_DPO_BETA                 : DPO inverse temperature (default 0.07)
#   DR_PAIR_LOSS_WEIGHT         : weight on the DPO pair loss (default 0.3)
#   DR_PAIR_MIN_REWARD_GAP      : min reward gap to mine a pair (default 0.4)
#   GRPO_STEPS                  : number of GRPO steps (default 200)
#   GROUP_SIZE                  : candidates per prompt (default 4)
#   MAX_NEW_TOKENS              : generation budget (default 1024)
#   MAX_SEQ_LENGTH              : context budget (default 2048)
#   LORA_RANK / LORA_ALPHA      : LoRA shape (default 16 / 32)
#   LEARNING_RATE               : default 5e-6
#   VISIBLE_DEVICES             : default 0,1
#
# Usage
# -----
#   bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh
#   bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh dry-run
#   bash research/papers/doubly_robust_quantum_grpo/code/asi1_dr_grpo_2npu.sh status
#
# Operator runbook: see README.md in this directory.

set -euo pipefail

ROOT_DIR="${ROOT_DIR:-/root/work/quantum-gpt}"
cd "$ROOT_DIR"

# ---- paths ----
MODEL="${MODEL:-/root/work/filestorage/Qwen3.6-27B}"
BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_grpo_training_v2_disjoint.txt}"
RUN_ID="${RUN_ID:-dr-grpo-27b-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/outputs/$RUN_ID}"
ADAPTER_INIT="${ADAPTER_INIT:-}"
LOG_DIR="$OUTPUT_DIR/logs"
TRAINER_LOG="$LOG_DIR/trainer.log"
TRAINER_PID_FILE="$OUTPUT_DIR/trainer.pid"
RUN_CONFIG_PATH="$OUTPUT_DIR/run_config.json"
RESEARCH_METHODS="${RESEARCH_METHODS:-doubly_robust_quantum_grpo}"

# ---- hardware ----
VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1}"
NPROC_PER_NODE="${NPROC_PER_NODE:-2}"
MASTER_PORT="${MASTER_PORT:-29512}"

# ---- GRPO hyperparameters (mirror the existing 27B GRPO defaults) ----
GRPO_STEPS="${GRPO_STEPS:-200}"
GROUP_SIZE="${GROUP_SIZE:-4}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-1024}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-2048}"
LEARNING_RATE="${LEARNING_RATE:-5e-6}"
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-32}"
LORA_DROPOUT="${LORA_DROPOUT:-0.05}"
LOG_STEPS="${LOG_STEPS:-5}"
CHECKPOINT_INTERVAL_SECONDS="${CHECKPOINT_INTERVAL_SECONDS:-600}"
TARGET_MODULES="${TARGET_MODULES:-q_proj v_proj o_proj gate_proj up_proj down_proj}"

# ---- reward weights (mirror the existing 27B GRPO defaults) ----
REWARD_PASS_WEIGHT="${REWARD_PASS_WEIGHT:-1.0}"
REWARD_SYNTAX_WEIGHT="${REWARD_SYNTAX_WEIGHT:-0.2}"
REWARD_INTERFACE_WEIGHT="${REWARD_INTERFACE_WEIGHT:-0.2}"
REWARD_VERIFIER_WEIGHT="${REWARD_VERIFIER_WEIGHT:-0.3}"
REWARD_BREVITY_WEIGHT="${REWARD_BREVITY_WEIGHT:-0.05}"
REWARD_IMPORT_HYGIENE_WEIGHT="${REWARD_IMPORT_HYGIENE_WEIGHT:-0.05}"

# ---- DR plugin hyperparameters (see paper.md) ----
DR_DPO_BETA="${DR_DPO_BETA:-0.07}"
DR_PAIR_LOSS_WEIGHT="${DR_PAIR_LOSS_WEIGHT:-0.3}"
DR_PAIR_MIN_REWARD_GAP="${DR_PAIR_MIN_REWARD_GAP:-0.4}"
DR_PAIR_MAX_PER_STEP="${DR_PAIR_MAX_PER_STEP:-1}"
DR_PSI_INIT="${DR_PSI_INIT:-0.5}"

# ---- helper ----
log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

# ---- dry-run subcommand ----
if [[ "${1:-}" == "dry-run" ]]; then
  echo "=== DRY RUN: would launch with the following config ==="
  echo "MODEL=$MODEL"
  echo "BENCHMARK_FILE=$BENCHMARK_FILE"
  echo "OUTPUT_DIR=$OUTPUT_DIR"
  echo "ADAPTER_INIT=${ADAPTER_INIT:-(none)}"
  echo "VISIBLE_DEVICES=$VISIBLE_DEVICES"
  echo "NPROC_PER_NODE=$NPROC_PER_NODE"
  echo "GRPO_STEPS=$GRPO_STEPS"
  echo "GROUP_SIZE=$GROUP_SIZE"
  echo "RESEARCH_METHODS=$RESEARCH_METHODS"
  echo "DR_DPO_BETA=$DR_DPO_BETA"
  echo "DR_PAIR_LOSS_WEIGHT=$DR_PAIR_LOSS_WEIGHT"
  echo "DR_PAIR_MIN_REWARD_GAP=$DR_PAIR_MIN_REWARD_GAP"
  echo "DR_PSI_INIT=$DR_PSI_INIT"
  exit 0
fi

# ---- status subcommand ----
if [[ "${1:-}" == "status" ]]; then
  echo "OUTPUT_DIR=$OUTPUT_DIR"
  if [[ -f "$TRAINER_PID_FILE" ]]; then
    pid="$(cat "$TRAINER_PID_FILE" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "trainer: RUNNING pid=$pid"
    else
      echo "trainer: STOPPED (stale pid file)"
    fi
  else
    echo "trainer: NOT_STARTED"
  fi
  if [[ -f "$TRAINER_LOG" ]]; then
    echo '--- trainer log tail ---'
    tail -n 20 "$TRAINER_LOG" 2>/dev/null || true
  fi
  exit 0
fi

# ---- stop subcommand ----
if [[ "${1:-}" == "stop" ]]; then
  log "stop requested"
  if [[ -f "$TRAINER_PID_FILE" ]]; then
    pid="$(cat "$TRAINER_PID_FILE" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      log "killing trainer pid=$pid"
      kill -TERM "$pid" 2>/dev/null || true
      sleep 5
      kill -KILL "$pid" 2>/dev/null || true
    fi
    rm -f "$TRAINER_PID_FILE"
  fi
  exit 0
fi

# ---- preflight ----
test -d "$MODEL" || { echo "FATAL: missing model $MODEL" >&2; exit 2; }
test -s "$BENCHMARK_FILE" || { echo "FATAL: missing benchmark $BENCHMARK_FILE" >&2; exit 2; }
test -s training/grpo_trainer.py || { echo "FATAL: missing trainer" >&2; exit 2; }
test -s research/papers/doubly_robust_quantum_grpo/code/plugin.py || { echo "FATAL: missing plugin" >&2; exit 2; }
test -s research/papers/doubly_robust_quantum_grpo/code/dr_pair_loss.py || { echo "FATAL: missing dr_pair_loss" >&2; exit 2; }

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# ---- write run config ----
cat > "$RUN_CONFIG_PATH" <<JSON
{
  "schema_version": 1,
  "run_id": "$RUN_ID",
  "environment": "ASI1",
  "model_name": "$MODEL",
  "benchmark_file": "$BENCHMARK_FILE",
  "output_dir": "$OUTPUT_DIR",
  "adapter_init": "${ADAPTER_INIT:-null}",
  "hardware": {
    "visible_devices": "$VISIBLE_DEVICES",
    "nproc_per_node": $NPROC_PER_NODE,
    "master_port": $MASTER_PORT
  },
  "grpo": {
    "steps": $GRPO_STEPS,
    "group_size": $GROUP_SIZE,
    "max_new_tokens": $MAX_NEW_TOKENS,
    "max_seq_length": $MAX_SEQ_LENGTH,
    "learning_rate": $LEARNING_RATE,
    "lora_rank": $LORA_RANK,
    "lora_alpha": $LORA_ALPHA,
    "lora_dropout": $LORA_DROPOUT,
    "target_modules": "$TARGET_MODULES"
  },
  "reward_weights": {
    "pass": $REWARD_PASS_WEIGHT,
    "syntax": $REWARD_SYNTAX_WEIGHT,
    "interface": $REWARD_INTERFACE_WEIGHT,
    "verifier": $REWARD_VERIFIER_WEIGHT,
    "brevity": $REWARD_BREVITY_WEIGHT,
    "import_hygiene": $REWARD_IMPORT_HYGIENE_WEIGHT
  },
  "research_methods": "$RESEARCH_METHODS",
  "doubly_robust_quantum_grpo": {
    "dr_dpo_beta": $DR_DPO_BETA,
    "dr_pair_loss_weight": $DR_PAIR_LOSS_WEIGHT,
    "dr_pair_min_reward_gap": $DR_PAIR_MIN_REWARD_GAP,
    "dr_pair_max_per_step": $DR_PAIR_MAX_PER_STEP,
    "dr_psi_init": $DR_PSI_INIT
  }
}
JSON
log "wrote run config to $RUN_CONFIG_PATH"

# ---- build the trainer command ----
ADAPTER_ARGS=()
if [[ -n "$ADAPTER_INIT" ]]; then
  ADAPTER_ARGS=(--adapter-init "$ADAPTER_INIT")
fi

# Convert TARGET_MODULES space-separated string into repeated --target-modules args.
TARGET_MODULE_ARGS=()
for m in $TARGET_MODULES; do
  TARGET_MODULE_ARGS+=(--target-modules "$m")
done

RESEARCH_METHOD_ARGS=()
for m in $RESEARCH_METHODS; do
  RESEARCH_METHOD_ARGS+=(--research-methods "$m")
done

log "launching trainer: $OUTPUT_DIR"
log "  model=$MODEL"
log "  benchmark=$BENCHMARK_FILE"
log "  research_methods=$RESEARCH_METHODS"
log "  dr_dpo_beta=$DR_DPO_BETA dr_pair_loss_weight=$DR_PAIR_LOSS_WEIGHT"

# ---- launch ----
ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES" \
PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 \
TOKENIZERS_PARALLELISM=false \
nohup torchrun --nproc_per_node "$NPROC_PER_NODE" --master_port "$MASTER_PORT" \
  training/grpo_trainer.py \
  --model-name "$MODEL" \
  --benchmark-file "$BENCHMARK_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --grpo-steps "$GRPO_STEPS" \
  --group-size "$GROUP_SIZE" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --max-seq-length "$MAX_SEQ_LENGTH" \
  --learning-rate "$LEARNING_RATE" \
  --lora-rank "$LORA_RANK" \
  --lora-alpha "$LORA_ALPHA" \
  --lora-dropout "$LORA_DROPOUT" \
  --lora-backend peft \
  "${TARGET_MODULE_ARGS[@]}" \
  --train-on-completions-only \
  --gradient-checkpointing \
  --checkpoint-interval-seconds "$CHECKPOINT_INTERVAL_SECONDS" \
  --reward-pass-weight "$REWARD_PASS_WEIGHT" \
  --reward-syntax-weight "$REWARD_SYNTAX_WEIGHT" \
  --reward-interface-weight "$REWARD_INTERFACE_WEIGHT" \
  --reward-verifier-weight "$REWARD_VERIFIER_WEIGHT" \
  --reward-brevity-weight "$REWARD_BREVITY_WEIGHT" \
  --reward-import-hygiene-weight "$REWARD_IMPORT_HYGIENE_WEIGHT" \
  --log-steps "$LOG_STEPS" \
  "${RESEARCH_METHOD_ARGS[@]}" \
  "${ADAPTER_ARGS[@]}" \
  > "$TRAINER_LOG" 2>&1 &

TRAINER_PID=$!
echo "$TRAINER_PID" > "$TRAINER_PID_FILE"
log "trainer launched pid=$TRAINER_PID log=$TRAINER_LOG"
log "monitor with: bash $0 status"
log "stop with:    bash $0 stop"
log "__ASI1_DR_GRPO_LAUNCHED__ out=$OUTPUT_DIR pid=$TRAINER_PID"
