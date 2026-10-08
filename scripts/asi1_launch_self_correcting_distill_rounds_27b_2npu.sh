#!/usr/bin/env bash
# ASI1 launcher: multi-round self-correcting distillation for Qwen3.6-27B.
#
# Architecture
# ------------
#   NPU 0,1  -> vLLM student server (Qwen3.6-27B + LoRA adapter, port 8007)
#   CPU      -> self_correcting_distill_rounds.py
#                (teacher GLM5.2 is called via $GLM52_API_BASE, which can be
#                 a remote endpoint or the local aihuanxin proxy)
#
# The orchestrator runs `max_rounds` rounds of `batch_size` questions each.
# Each round:
#   1. Teacher (GLM5.2) generates `batch_size` questions targeted at the
#      student's weakest (framework, topic, difficulty) cells.
#   2. Student adapter attempts each question.
#   3. Teacher grades + corrects, preserving top-20 logprobs per token.
#   4. Weakness report is written for the next round.
#
# Output goes to $OUT_DIR/rounds/round_NNN/{questions_pool.jsonl,
# student_answers.jsonl, teacher_evals.jsonl, train_chatml_with_logits.jsonl,
# weakness_report.json, state.json}.
#
# Usage:
#   bash scripts/asi1_launch_self_correcting_distill_rounds_27b_2npu.sh
#   bash scripts/asi1_launch_self_correcting_distill_rounds_27b_2npu.sh stop
#
# Env knobs (all have defaults):
#   MAX_ROUNDS=10         number of rounds
#   BATCH_SIZE=100        questions per round
#   WORKERS=4             concurrent student+teacher calls within a round
#   VLLM_PORT=8007        student server port
#   GLM52_API_BASE        teacher endpoint (REQUIRED if not in env already)
#   GLM52_API_KEY         teacher API key (REQUIRED if not in env already)
#   STUDENT_27B_API_KEY   student API key (any non-empty string for local vLLM)
#   ADAPTER_INIT          path to initial LoRA adapter (optional)
#   NO_GIT_PUSH=1         commit but don't push
#   NO_GIT_SYNC=1         disable git checkpointing entirely

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

# ---- config ----
VISIBLE_DEVICES="${VISIBLE_DEVICES:-0,1}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-2}"
VLLM_PORT="${VLLM_PORT:-8007}"
VLLM_MODEL="${VLLM_MODEL:-/root/work/filestorage/Qwen3.8-27B}"
VLLM_LORA_ADAPTER_NAME="${VLLM_LORA_ADAPTER_NAME:-qwen36-27b-student}"
ADAPTER_INIT="${ADAPTER_INIT:-}"
LORA_RANK="${LORA_RANK:-16}"
MAX_LENGTH="${MAX_LENGTH:-4096}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-32}"

MAX_ROUNDS="${MAX_ROUNDS:-10}"
BATCH_SIZE="${BATCH_SIZE:-100}"
WORKERS="${WORKERS:-4}"

CONFIG="${CONFIG:-configs/distill/self_correcting_distill_27b_v1.json}"
OUT_DIR="${OUT_DIR:-data/generated/self_correcting_distill_27b_v1}"

OUT="$ROOT/$OUT_DIR"
mkdir -p "$OUT/logs"

VLLM_PID_FILE="$OUT/vllm.pid"
VLLM_LOG="$OUT/logs/vllm.log"
ORCHESTRATOR_LOG="$OUT/logs/orchestrator.log"
ORCHESTRATOR_PID_FILE="$OUT/orchestrator.pid"

log() { printf '[%s] %s\n' "$(date -Is)" "$*" | tee -a "$ORCHESTRATOR_LOG"; }

# ---- stop subcommand ----
if [[ "${1:-}" == "stop" ]]; then
  log "stop requested"
  for pf in "$ORCHESTRATOR_PID_FILE" "$VLLM_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        log "killing $pf pid=$pid"
        kill -TERM "$pid" 2>/dev/null || true
      fi
    fi
  done
  sleep 3
  exit 0
fi

# ---- env validation ----
: "${GLM52_API_BASE:?GLM52_API_BASE must be set (teacher endpoint)}"
: "${GLM52_API_KEY:?GLM52_API_KEY must be set (teacher API key)}"
: "${STUDENT_27B_API_KEY:?STUDENT_27B_API_KEY must be set (any non-empty string for local vLLM)}"
export GLM52_API_BASE GLM52_API_KEY STUDENT_27B_API_KEY

log "=== multi-round self-correcting distillation (27B) ==="
log "config=$CONFIG out=$OUT rounds=$MAX_ROUNDS batch=$BATCH_SIZE workers=$WORKERS"
log "vLLM: model=$VLLM_MODEL tp=$TENSOR_PARALLEL_SIZE port=$VLLM_PORT adapter=$ADAPTER_INIT"
log "teacher: $GLM52_API_BASE"

# ---- 1. Start vLLM student server ----
if [[ -f "$VLLM_PID_FILE" ]] && kill -0 "$(cat "$VLLM_PID_FILE" 2>/dev/null)" 2>/dev/null; then
  log "vLLM already running pid=$(cat "$VLLM_PID_FILE")"
else
  log "launching vLLM student server on NPUs=$VISIBLE_DEVICES tp=$TENSOR_PARALLEL_SIZE port=$VLLM_PORT"
  export ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES"
  ADAPTER_ARGS=()
  if [[ -n "$ADAPTER_INIT" ]]; then
    ADAPTER_ARGS=(--enable-lora --lora-modules "$VLLM_LORA_ADAPTER_NAME=$ADAPTER_INIT" --max-loras 1 --max-lora-rank "$LORA_RANK")
  fi
  nohup python3 -m vllm.entrypoints.openai.api_server \
    --model "$VLLM_MODEL" \
    --served-model-name "$VLLM_LORA_ADAPTER_NAME" \
    --tensor-parallel-size "$TENSOR_PARALLEL_SIZE" \
    --port "$VLLM_PORT" \
    --max-model-len "$MAX_LENGTH" \
    --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
    --max-num-seqs "$MAX_NUM_SEQS" \
    --trust-remote-code \
    --dtype bfloat16 \
    "${ADAPTER_ARGS[@]}" \
    >> "$VLLM_LOG" 2>&1 &
  VLLM_PID=$!
  echo "$VLLM_PID" > "$VLLM_PID_FILE"
  log "vLLM launched pid=$VLLM_PID; waiting for /v1/models to respond..."
  for i in $(seq 1 120); do
    if curl -sf "http://127.0.0.1:$VLLM_PORT/v1/models" >/dev/null 2>&1; then
      log "vLLM is ready (took ${i}0s)"
      break
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
      log "ERROR: vLLM died during startup; see $VLLM_LOG"
      tail -30 "$VLLM_LOG" || true
      exit 1
    fi
    sleep 10
  done
  if ! curl -sf "http://127.0.0.1:$VLLM_PORT/v1/models" >/dev/null 2>&1; then
    log "ERROR: vLLM did not become ready in 20min; see $VLLM_LOG"
    exit 1
  fi
fi

# ---- 2. Launch the multi-round orchestrator ----
log "launching self_correcting_distill_rounds.py"
GIT_ARGS=()
[[ "${NO_GIT_PUSH:-0}" == "1" ]] && GIT_ARGS+=(--no-git-push)
[[ "${NO_GIT_SYNC:-0}" == "1" ]] && GIT_ARGS+=(--no-git-sync)

nohup python3 scripts/self_correcting_distill_rounds.py \
  --config "$CONFIG" \
  --max-rounds "$MAX_ROUNDS" \
  --batch-size "$BATCH_SIZE" \
  --workers "$WORKERS" \
  --resume \
  "${GIT_ARGS[@]}" \
  >> "$ORCHESTRATOR_LOG" 2>&1 &
ORCH_PID=$!
echo "$ORCH_PID" > "$ORCHESTRATOR_PID_FILE"
log "orchestrator launched pid=$ORCH_PID"
log "monitor with: tail -f $ORCHESTRATOR_LOG"
log "stop with: bash scripts/asi1_launch_self_correcting_distill_rounds_27b_2npu.sh stop"
