#!/usr/bin/env bash
# ASI1 launcher: RL + soft-distillation loop for Qwen3.6-27B on 2 NPUs.
#
# Architecture
# ------------
#   NPU 0,1  -> vLLM student server (Qwen3.6-27B + LoRA adapter, port 8007)
#   CPU      -> rl_distill_pipeline.py (question gen + teacher correct + logits)
#   NPU 0,1  -> qwen_sft_peft_kl.py (hourly soft-KL SFT on the accumulated buffer)
#
# The student server and the trainer SHARE the 2 NPUs (trainer runs in
# short bursts once per hour; the vLLM server is paused around the trainer
# step to avoid OOM). Between trainer bursts the pipeline keeps generating
# (question, teacher_correction, teacher_logits) tuples into a rolling
# JSONL buffer.
#
# Teacher (GLM5.2) is reached via the GLM52_API_BASE / GLM52_API_KEY env
# vars (a remote HTTP endpoint, no local NPU needed).
#
# Usage:
#   bash scripts/asi1_launch_rl_distill_27b_2npu.sh launch
#   bash scripts/asi1_launch_rl_distill_27b_2npu.sh status
#   bash scripts/asi1_launch_rl_distill_27b_2npu.sh stop
#
# Required env:
#   GLM52_API_BASE, GLM52_API_KEY
#   STUDENT_27B_API_KEY  (any non-empty string if vLLM is launched with --api-key dummy)
# Optional env:
#   MODEL, ADAPTER_INIT, NAS_ROOT, NPROC, RUN_ID, OUT, BUFFER_DIR,
#   VLLM_PORT, KL_COEFF, NLL_COEFF, TEMPERATURE, MAX_LENGTH,
#   LEARNING_RATE, LORA_RANK, LORA_ALPHA, BUFFER_TARGET_PER_ROUND

set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"

MODEL="${MODEL:-/root/work/filestorage/Qwen3.6-27B}"
ADAPTER_INIT="${ADAPTER_INIT:-}"
RUN_ID="${RUN_ID:-rl-distill-27b-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$NAS_ROOT/outputs/qg-27b-rl-distill-${RUN_ID}}"
BUFFER_DIR="${BUFFER_DIR:-$NAS_ROOT/data/generated/rl_distill_27b_v1}"
CONFIG="${CONFIG:-configs/distill/rl_distill_27b_v1.json}"
VLLM_PORT="${VLLM_PORT:-8007}"
VLLM_SERVED_NAME="${VLLM_SERVED_NAME:-qwen36-27b-rl-distill}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-2}"
VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"
KL_COEFF="${KL_COEFF:-0.5}"
NLL_COEFF="${NLL_COEFF:-0.5}"
TEMPERATURE="${TEMPERATURE:-1.0}"
MAX_LENGTH="${MAX_LENGTH:-2048}"
LEARNING_RATE="${LEARNING_RATE:-3e-5}"
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-32}"
BUFFER_TARGET_PER_ROUND="${BUFFER_TARGET_PER_ROUND:-100}"
TRAINER_CHECKPOINT_SECONDS="${TRAINER_CHECKPOINT_SECONDS:-7200}"
TRAINER_MAX_STEPS_PER_ROUND="${TRAINER_MAX_STEPS_PER_ROUND:-200}"
PIPELINE_MAX_WALLCLOCK_SECONDS="${PIPELINE_MAX_WALLCLOCK_SECONDS:-3300}"  # 55 min, leaves 5 min for trainer
PIPELINE_MAX_ROUNDS="${PIPELINE_MAX_ROUNDS:-0}"  # 0 = unbounded; set e.g. 20 for a fixed ablation budget
PIPELINE_CONCURRENCY="${PIPELINE_CONCURRENCY:-4}"
REWARD_FLOOR="${REWARD_FLOOR:-0.20}"
# Eval integration (closed-loop Stage 9). Set EVAL_EVERY_ROUNDS=0 to disable.
EVAL_EVERY_ROUNDS="${EVAL_EVERY_ROUNDS:-2}"
EVAL_TASKS="${EVAL_TASKS:-quantum}"
EVAL_K="${EVAL_K:-1}"
EVAL_MAX_NEW_TOKENS="${EVAL_MAX_NEW_TOKENS:-1024}"
EVAL_NPU_MAX_MEMORY_GIB="${EVAL_NPU_MAX_MEMORY_GIB:-58}"
# vLLM pause mode for the trainer burst:
#   sleep = keep vLLM process alive, POST /v1/sleep to free NPU memory, then
#           /v1/wake_up + /v1/load_lora_adapter to resume (fast; avoids
#           re-loading the 27B base weights from disk every round).
#   kill  = legacy behaviour: SIGTERM/SIGKILL vLLM and relaunch with
#           `vllm serve` after the trainer (slow; full cold start each round).
# Sleep mode auto-falls back to kill mode if the running vLLM does not
# expose /v1/sleep or /v1/load_lora_adapter.
VLLM_PAUSE_MODE="${VLLM_PAUSE_MODE:-sleep}"
VLLM_WAKE_TIMEOUT_SECONDS="${VLLM_WAKE_TIMEOUT_SECONDS:-300}"
VLLM_LORA_ADAPTER_NAME="${VLLM_LORA_ADAPTER_NAME:-rl_distill_latest}"

# Per-artifact reward-weighted distillation ablation preset.
# Maps a single name to the three trainer flags
# (--reward-weighted-nll / --per-artifact-kl-gate / --partial-credit-upweight).
#   A_legacy        -> off / off / 0.0   (current behaviour, default)
#   B_rw_nll        -> on  / off / 0.0
#   C_kl_gate       -> off / on  / 0.0
#   D_partial_up    -> off / off / 0.5
#   E_full          -> on  / on  / 0.5
#   F_full_no_up    -> on  / on  / 0.0
# See docs/per-artifact-scoring-rd-plan-2026-07-08.md §3.5.
ABLATION_PRESET="${ABLATION_PRESET:-A_legacy}"
case "$ABLATION_PRESET" in
  A_legacy)    ABLATION_RW_NLL=""; ABLATION_KL_GATE=""; ABLATION_PARTIAL_UP="0.0" ;;
  B_rw_nll)    ABLATION_RW_NLL="--reward-weighted-nll"; ABLATION_KL_GATE=""; ABLATION_PARTIAL_UP="0.0" ;;
  C_kl_gate)   ABLATION_RW_NLL=""; ABLATION_KL_GATE="--per-artifact-kl-gate"; ABLATION_PARTIAL_UP="0.0" ;;
  D_partial_up) ABLATION_RW_NLL=""; ABLATION_KL_GATE=""; ABLATION_PARTIAL_UP="0.5" ;;
  E_full)      ABLATION_RW_NLL="--reward-weighted-nll"; ABLATION_KL_GATE="--per-artifact-kl-gate"; ABLATION_PARTIAL_UP="0.5" ;;
  F_full_no_up) ABLATION_RW_NLL="--reward-weighted-nll"; ABLATION_KL_GATE="--per-artifact-kl-gate"; ABLATION_PARTIAL_UP="0.0" ;;
  *) echo "unknown ABLATION_PRESET=$ABLATION_PRESET (expected A_legacy|B_rw_nll|C_kl_gate|D_partial_up|E_full|F_full_no_up)" >&2; exit 3 ;;
esac

mkdir -p "$OUT" "$BUFFER_DIR" "$OUT/logs" "$OUT/checkpoints"

VLLM_LOG="$OUT/logs/vllm.log"
VLLM_PID_FILE="$OUT/vllm.pid"
PIPELINE_LOG="$OUT/logs/rl_distill_pipeline.log"
PIPELINE_PID_FILE="$OUT/rl_distill_pipeline.pid"
TRAINER_LOG="$OUT/logs/trainer.log"
TRAINER_PID_FILE="$OUT/trainer.pid"
ORCHESTRATOR_LOG="$OUT/logs/orchestrator.log"
ORCHESTRATOR_PID_FILE="$OUT/orchestrator.pid"

# ---- helper: log with timestamp ----
log() { printf '[%s] %s\n' "$(date -Is)" "$*" >> "$ORCHESTRATOR_LOG"; echo "[$(date -Is)] $*"; }

# ---- stop subcommand ----
if [[ "${1:-}" == "stop" ]]; then
  log "stop requested"
  for pf in "$ORCHESTRATOR_PID_FILE" "$PIPELINE_PID_FILE" "$TRAINER_PID_FILE" "$VLLM_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        log "killing $pf pid=$pid"
        kill -TERM "$pid" 2>/dev/null || true
      fi
    fi
  done
  sleep 5
  for pf in "$ORCHESTRATOR_PID_FILE" "$PIPELINE_PID_FILE" "$TRAINER_PID_FILE" "$VLLM_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        log "force killing $pf pid=$pid"
        kill -KILL "$pid" 2>/dev/null || true
      fi
      rm -f "$pf"
    fi
  done
  exit 0
fi

# ---- status subcommand ----
if [[ "${1:-}" == "status" ]]; then
  echo "OUT=$OUT"
  echo "BUFFER_DIR=$BUFFER_DIR"
  for pf in "$VLLM_PID_FILE" "$PIPELINE_PID_FILE" "$TRAINER_PID_FILE" "$ORCHESTRATOR_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || echo '?')"
      alive="DEAD"
      kill -0 "$pid" 2>/dev/null && alive="ALIVE"
      echo "$(basename "$pf"): pid=$pid $alive"
    else
      echo "$(basename "$pf"): NONE"
    fi
  done
  echo '--- vllm log tail ---'; tail -n 20 "$VLLM_LOG" 2>/dev/null || true
  echo '--- pipeline log tail ---'; tail -n 20 "$PIPELINE_LOG" 2>/dev/null || true
  echo '--- trainer log tail ---'; tail -n 20 "$TRAINER_LOG" 2>/dev/null || true
  echo '--- buffer manifest ---'; cat "$BUFFER_DIR/rl_distill_manifest.json" 2>/dev/null || echo NONE
  exit 0
fi

# ---- launch subcommand (default) ----
if [[ "${1:-launch}" != "launch" && -n "${1:-}" ]]; then
  echo "Usage: $0 {launch|status|stop}" >&2
  exit 2
fi

# ---- preflight ----
test -d "$MODEL" || { echo "missing MODEL=$MODEL" >&2; exit 3; }
test -f "$CONFIG" || { echo "missing CONFIG=$CONFIG" >&2; exit 3; }
test -n "${GLM52_API_BASE:-}" || { echo "GLM52_API_BASE is required" >&2; exit 3; }
test -n "${GLM52_API_KEY:-}" || { echo "GLM52_API_KEY is required" >&2; exit 3; }
export STUDENT_27B_API_KEY="${STUDENT_27B_API_KEY:-dummy}"
export GLM52_API_BASE GLM52_API_KEY

# ---- record run config ----
cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-27b-rl-distill-${RUN_ID}",
  "model": "$MODEL",
  "adapter_init": "${ADAPTER_INIT:-null}",
  "config": "$CONFIG",
  "buffer_dir": "$BUFFER_DIR",
  "tensor_parallel_size": $TENSOR_PARALLEL_SIZE,
  "visible_devices": "$VISIBLE_DEVICES",
  "vllm_port": $VLLM_PORT,
  "vllm_served_name": "$VLLM_SERVED_NAME",
  "kl_coeff": $KL_COEFF,
  "nll_coeff": $NLL_COEFF,
  "temperature": $TEMPERATURE,
  "max_length": $MAX_LENGTH,
  "learning_rate": "$LEARNING_RATE",
  "lora_rank": $LORA_RANK,
  "lora_alpha": $LORA_ALPHA,
  "buffer_target_per_round": $BUFFER_TARGET_PER_ROUND,
  "trainer_checkpoint_seconds": $TRAINER_CHECKPOINT_SECONDS,
  "trainer_max_steps_per_round": $TRAINER_MAX_STEPS_PER_ROUND,
  "pipeline_max_wallclock_seconds": $PIPELINE_MAX_WALLCLOCK_SECONDS,
  "pipeline_max_rounds": $PIPELINE_MAX_ROUNDS,
  "teacher_model": "glm5.2",
  "pipeline": "rl_distill_v1",
  "vllm_pause_mode": "$VLLM_PAUSE_MODE",
  "ablation_preset": "$ABLATION_PRESET",
  "ablation_reward_weighted_nll": "$([ -n "$ABLATION_RW_NLL" ] && echo true || echo false)",
  "ablation_per_artifact_kl_gate": "$([ -n "$ABLATION_KL_GATE" ] && echo true || echo false)",
  "ablation_partial_credit_upweight": $ABLATION_PARTIAL_UP
}
CFG

# ---- 1. Start vLLM student server on 2 NPUs ----
if [[ -f "$VLLM_PID_FILE" ]] && kill -0 "$(cat "$VLLM_PID_FILE" 2>/dev/null)" 2>/dev/null; then
  log "vLLM already running pid=$(cat "$VLLM_PID_FILE")"
else
  log "launching vLLM student server on NPUs=$VISIBLE_DEVICES tp=$TENSOR_PARALLEL_SIZE port=$VLLM_PORT"
  export ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES"
  ADAPTER_ARGS=()
  if [[ -n "$ADAPTER_INIT" ]]; then
    ADAPTER_ARGS=(--enable-lora --lora-modules "$VLLM_LORA_ADAPTER_NAME=$ADAPTER_INIT" --max-loras 1 --max-lora-rank "$LORA_RANK")
  fi
  nohup vllm serve "$MODEL" \
    --host 127.0.0.1 --port "$VLLM_PORT" \
    --served-model-name "$VLLM_SERVED_NAME" \
    --tensor-parallel-size "$TENSOR_PARALLEL_SIZE" \
    --dtype bfloat16 \
    --max-model-len "$MAX_MODEL_LEN" \
    --trust-remote-code \
    --api-key "$STUDENT_27B_API_KEY" \
    --disable-log-requests \
    "${ADAPTER_ARGS[@]}" \
    > "$VLLM_LOG" 2>&1 &
  echo "$!" > "$VLLM_PID_FILE"
  log "vLLM launched pid=$(cat "$VLLM_PID_FILE") log=$VLLM_LOG"
fi

# Wait for vLLM to come up
log "waiting for vLLM to be ready..."
for i in $(seq 1 120); do
  if curl -s "http://127.0.0.1:$VLLM_PORT/v1/models" -H "Authorization: Bearer $STUDENT_27B_API_KEY" 2>/dev/null | grep -q "$VLLM_SERVED_NAME"; then
    log "vLLM ready after ${i}0s"
    break
  fi
  sleep 10
done

# ---- 2. Start the orchestrator (pipeline + periodic trainer) ----
# The orchestrator is a bash loop that alternates between:
#   (a) running the RL+distill pipeline for ~55 minutes (generates samples
#       into the buffer)
#   (b) pausing the vLLM server, running the soft-KL trainer for ~5 minutes
#       (or until max-steps), saving a checkpoint, then resuming vLLM
cat > "$OUT/orchestrator.sh" <<ORCH
#!/usr/bin/env bash
set -uo pipefail
cd "$NAS_ROOT"
export ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES"
export GLM52_API_BASE="$GLM52_API_BASE"
export GLM52_API_KEY="$GLM52_API_KEY"
export STUDENT_27B_API_KEY="$STUDENT_27B_API_KEY"

ROUND=0
while true; do
  ROUND=\$((ROUND + 1))
  echo "[\$(date -Is)] === orchestrator round \$ROUND ===" >> "$ORCHESTRATOR_LOG"

  # ---- (a) Run the pipeline to accumulate samples ----
  echo "[\$(date -Is)] starting pipeline round \$ROUND (target=$BUFFER_TARGET_PER_ROUND samples, max ${PIPELINE_MAX_WALLCLOCK_SECONDS}s, concurrency=$PIPELINE_CONCURRENCY)" >> "$ORCHESTRATOR_LOG"
  python3 scripts/rl_distill_pipeline.py \\
    --config "$CONFIG" \\
    --buffer-dir "$BUFFER_DIR" \\
    --target-buffer-size $BUFFER_TARGET_PER_ROUND \\
    --max-wallclock-seconds $PIPELINE_MAX_WALLCLOCK_SECONDS \\
    --manifest-every 8 \\
    --concurrency $PIPELINE_CONCURRENCY \\
    --pass-rate-stop ${PASS_RATE_STOP:-0.99} \\
    --pass-rate-window ${PASS_RATE_WINDOW:-100} \\
    ${WEAKNESS_REPORT:+--weakness-report "$WEAKNESS_REPORT"} \\
    >> "$PIPELINE_LOG" 2>&1 &
  PIPELINE_PID=\$!
  echo "\$PIPELINE_PID" > "$PIPELINE_PID_FILE"
  wait \$PIPELINE_PID || true
  rm -f "$PIPELINE_PID_FILE"

  # ---- (a.5) Generate a weakness report from this batch for the next round ----
  echo "[\$(date -Is)] generating weakness report from round \$ROUND batch" >> "$ORCHESTRATOR_LOG"
  python3 scripts/analyze_batch_weakness.py \\
    --buffer-dir "$BUFFER_DIR" \\
    --output "$BUFFER_DIR/weakness_report.json" \\
    --batch-id "round-\$ROUND" \\
    --min-cell-n 1 \\
    >> "$ORCHESTRATOR_LOG" 2>&1 || true
  export WEAKNESS_REPORT="$BUFFER_DIR/weakness_report.json"

  # ---- (b) Pause vLLM, run the trainer, resume vLLM ----
  # VLLM_PAUSED_MODE tracks how we paused so the resume step knows whether
  # to wake the process (sleep mode) or relaunch it (kill mode / fallback).
  VLLM_PAUSED_MODE="none"
  VLLM_PID="\$(cat "$VLLM_PID_FILE" 2>/dev/null || echo '')"
  if [[ -n "\$VLLM_PID" ]] && kill -0 "\$VLLM_PID" 2>/dev/null; then
    if [[ "$VLLM_PAUSE_MODE" == "sleep" ]]; then
      echo "[\$(date -Is)] sleeping vLLM (pid=\$VLLM_PID) for training burst" >> "$ORCHESTRATOR_LOG"
      python3 scripts/vllm_lifecycle.py \\
        --base-url "http://127.0.0.1:$VLLM_PORT" \\
        --api-key "$STUDENT_27B_API_KEY" \\
        sleep --level 1 --settle-seconds 5 --timeout 60 \\
        >> "$VLLM_LOG" 2>&1
      SLEEP_RC=\$?
      if [[ \$SLEEP_RC -eq 0 ]]; then
        VLLM_PAUSED_MODE="sleep"
        echo "[\$(date -Is)] vLLM sleep ok (process kept alive)" >> "$ORCHESTRATOR_LOG"
      else
        echo "[\$(date -Is)] vLLM sleep failed rc=\$SLEEP_RC; falling back to kill" >> "$ORCHESTRATOR_LOG"
      fi
    fi
    if [[ "\$VLLM_PAUSED_MODE" != "sleep" ]]; then
      echo "[\$(date -Is)] killing vLLM (pid=\$VLLM_PID) for training burst" >> "$ORCHESTRATOR_LOG"
      kill -TERM "\$VLLM_PID" 2>/dev/null || true
      for i in \$(seq 1 60); do
        kill -0 "\$VLLM_PID" 2>/dev/null || break
        sleep 5
      done
      kill -KILL "\$VLLM_PID" 2>/dev/null || true
      rm -f "$VLLM_PID_FILE"
      sleep 10  # let NPU memory free up
      VLLM_PAUSED_MODE="kill"
    fi
  fi

  # Build the train file from the buffer (all accumulated samples so far)
  TRAIN_FILE="$BUFFER_DIR/rl_distill_samples.jsonl"
  if [[ ! -s "$TRAIN_FILE" ]]; then
    echo "[\$(date -Is)] buffer empty; skipping trainer burst" >> "$ORCHESTRATOR_LOG"
  else
    TRAIN_ROWS=\$(wc -l < "$TRAIN_FILE")
    echo "[\$(date -Is)] starting trainer round \$ROUND on \$TRAIN_ROWS rows" >> "$ORCHESTRATOR_LOG"
    TRAINER_OUT="$OUT/checkpoints/round-\$ROUND"
    mkdir -p "\$TRAINER_OUT"
    ADAPTER_ARGS=()
    [[ -n "$ADAPTER_INIT" ]] && ADAPTER_ARGS=(--adapter-init "$ADAPTER_INIT")
    # For round > 1, warm-start from the previous round's adapter
    if [[ \$ROUND -gt 1 ]]; then
      PREV_ADAPTER="$OUT/checkpoints/round-\$((ROUND-1))/adapter"
      if [[ -d "\$PREV_ADAPTER" ]]; then
        ADAPTER_ARGS=(--adapter-init "\$PREV_ADAPTER")
      fi
    fi
    # Ablation flags (per-artifact reward-weighted distillation). The three
    # ABLATION_* vars are expanded at heredoc-write time from the launcher's
    # ABLATION_PRESET mapping above.
    ABLATION_ARGS=()
    [[ -n "$ABLATION_RW_NLL" ]] && ABLATION_ARGS+=("$ABLATION_RW_NLL")
    [[ -n "$ABLATION_KL_GATE" ]] && ABLATION_ARGS+=("$ABLATION_KL_GATE")
    ABLATION_ARGS+=(--partial-credit-upweight "$ABLATION_PARTIAL_UP")
    python3 training/qwen_sft_peft_kl.py \\
      --model-name "$MODEL" \\
      --train-file "$TRAIN_FILE" \\
      --eval-file "" \\
      --output-dir "\$TRAINER_OUT" \\
      --overwrite-output-dir \\
      --device npu \\
      --npu-device-map balanced-layers \\
      --npu-max-memory-gib 58 \\
      --epochs 1 \\
      --max-steps $TRAINER_MAX_STEPS_PER_ROUND \\
      --per-device-batch-size 1 \\
      --gradient-accumulation-steps 4 \\
      --learning-rate "$LEARNING_RATE" \\
      --warmup-steps 4 \\
      --max-length $MAX_LENGTH \\
      --lora-rank $LORA_RANK \\
      --lora-alpha $LORA_ALPHA \\
      --lora-dropout 0.05 \\
      --lora-backend peft \\
      --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \\
      --train-on-completions-only \\
      --gradient-checkpointing \\
      --checkpoint-interval-seconds $TRAINER_CHECKPOINT_SECONDS \\
      --kl-coeff $KL_COEFF \\
      --nll-coeff $NLL_COEFF \\
      --temperature $TEMPERATURE \\
      --reward-floor $REWARD_FLOOR \\
      "\${ADAPTER_ARGS[@]}" \\
      "\${ABLATION_ARGS[@]}" \\
      >> "$TRAINER_LOG" 2>&1 &
    TRAINER_PID=\$!
    echo "\$TRAINER_PID" > "$TRAINER_PID_FILE"
    wait \$TRAINER_PID || true
    rm -f "$TRAINER_PID_FILE"
    echo "[\$(date -Is)] trainer round \$ROUND done" >> "$ORCHESTRATOR_LOG"
  fi

  # ---- (c) Periodic eval on the latest adapter (closed-loop Stage 9) ----
  # LATEST_ADAPTER is computed once here and reused for vLLM resume below.
  LATEST_ADAPTER=""
  for d in "$OUT/checkpoints/round-"*/adapter; do
    [[ -d "\$d" ]] && LATEST_ADAPTER="\$d"
  done
  if [[ -n "\$LATEST_ADAPTER" && "$EVAL_EVERY_ROUNDS" -gt 0 && \$((ROUND % EVAL_EVERY_ROUNDS)) -eq 0 ]]; then
    EVAL_OUT="$OUT/evals/round-\$ROUND"
    mkdir -p "\$EVAL_OUT"
    EVAL_LOG="\$EVAL_OUT/eval.log"
    echo "[\$(date -Is)] starting eval round \$ROUND adapter=\$LATEST_ADAPTER" >> "$ORCHESTRATOR_LOG"
    # vLLM is still down at this point (we resume it below); run eval against
    # the adapter on the same NPUs via the eval-subsystem harness.
    python3 evals/subsystem/harness.py \\
      --base-model "$MODEL" \\
      --adapter "\$LATEST_ADAPTER" \\
      --output "\$EVAL_OUT/eval-\$ROUND.json" \\
      --device npu \\
      --npu-max-memory-gib $EVAL_NPU_MAX_MEMORY_GIB \\
      --max-new-tokens $EVAL_MAX_NEW_TOKENS \\
      --k $EVAL_K \\
      --tasks "$EVAL_TASKS" \\
      > "\$EVAL_LOG" 2>&1
    EVAL_RC=\$?
    echo "[\$(date -Is)] eval round \$ROUND rc=\$EVAL_RC out=\$EVAL_OUT" >> "$ORCHESTRATOR_LOG"
    # Auto-generate the markdown summary if the analyzer is available.
    if [[ \$EVAL_RC -eq 0 && -f "\$EVAL_OUT/eval-\$ROUND.json" ]]; then
      python3 evals/subsystem/analyzer.py compare \\
        --eval "\$EVAL_OUT/eval-\$ROUND.json" \\
        >> "\$EVAL_LOG" 2>&1 || true
      python3 evals/subsystem/reporter.py update-summary \\
        --eval "\$EVAL_OUT/eval-\$ROUND.json" \\
        --summary-file "$OUT/eval_summary.md" \\
        >> "\$EVAL_LOG" 2>&1 || true
    fi
  fi

  # Resume vLLM with the latest adapter (reuses LATEST_ADAPTER from eval step).
  # If we paused via /v1/sleep, wake the process and hot-swap the adapter via
  # /v1/load_lora_adapter (fast; no base-weight reload). Otherwise relaunch
  # vllm serve with --lora-modules (slow; full cold start).
  if [[ "\$VLLM_PAUSED_MODE" == "sleep" ]]; then
    echo "[\$(date -Is)] waking vLLM (process kept alive)" >> "$ORCHESTRATOR_LOG"
    python3 scripts/vllm_lifecycle.py \\
      --base-url "http://127.0.0.1:$VLLM_PORT" \\
      --api-key "$STUDENT_27B_API_KEY" \\
      wake --timeout $VLLM_WAKE_TIMEOUT_SECONDS \\
      >> "$VLLM_LOG" 2>&1
    WAKE_RC=\$?
    if [[ \$WAKE_RC -ne 0 ]]; then
      echo "[\$(date -Is)] vLLM wake failed rc=\$WAKE_RC; killing and relaunching" >> "$ORCHESTRATOR_LOG"
      VLLM_PID="\$(cat "$VLLM_PID_FILE" 2>/dev/null || echo '')"
      [[ -n "\$VLLM_PID" ]] && kill -KILL "\$VLLM_PID" 2>/dev/null || true
      rm -f "$VLLM_PID_FILE"
      VLLM_PAUSED_MODE="kill"
    elif [[ -n "\$LATEST_ADAPTER" ]]; then
      echo "[\$(date -Is)] hot-swapping LoRA adapter=\$LATEST_ADAPTER" >> "$ORCHESTRATOR_LOG"
      python3 scripts/vllm_lifecycle.py \\
        --base-url "http://127.0.0.1:$VLLM_PORT" \\
        --api-key "$STUDENT_27B_API_KEY" \\
        load-lora --lora-name "$VLLM_LORA_ADAPTER_NAME" \\
        --lora-path "\$LATEST_ADAPTER" --timeout 60 \\
        >> "$VLLM_LOG" 2>&1
      LOAD_RC=\$?
      if [[ \$LOAD_RC -ne 0 ]]; then
        echo "[\$(date -Is)] load_lora failed rc=\$LOAD_RC; falling back to kill/relaunch" >> "$ORCHESTRATOR_LOG"
        VLLM_PID="\$(cat "$VLLM_PID_FILE" 2>/dev/null || echo '')"
        [[ -n "\$VLLM_PID" ]] && kill -KILL "\$VLLM_PID" 2>/dev/null || true
        rm -f "$VLLM_PID_FILE"
        VLLM_PAUSED_MODE="kill"
      else
        echo "[\$(date -Is)] vLLM ready (sleep+wake+hot-swap path)" >> "$ORCHESTRATOR_LOG"
      fi
    else
      echo "[\$(date -Is)] vLLM ready (sleep+wake, no adapter)" >> "$ORCHESTRATOR_LOG"
    fi
  fi
  if [[ "\$VLLM_PAUSED_MODE" != "sleep" ]]; then
    echo "[\$(date -Is)] relaunching vLLM with adapter=\${LATEST_ADAPTER:-none}" >> "$ORCHESTRATOR_LOG"
    ADAPTER_ARGS=()
    if [[ -n "\$LATEST_ADAPTER" ]]; then
      ADAPTER_ARGS=(--enable-lora --lora-modules "$VLLM_LORA_ADAPTER_NAME=\$LATEST_ADAPTER" --max-loras 1 --max-lora-rank $LORA_RANK)
    fi
    nohup vllm serve "$MODEL" \\
      --host 127.0.0.1 --port "$VLLM_PORT" \\
      --served-model-name "$VLLM_SERVED_NAME" \\
      --tensor-parallel-size "$TENSOR_PARALLEL_SIZE" \\
      --dtype bfloat16 \\
      --max-model-len "$MAX_MODEL_LEN" \\
      --trust-remote-code \\
      --api-key "$STUDENT_27B_API_KEY" \\
      --disable-log-requests \\
      "\${ADAPTER_ARGS[@]}" \\
      >> "$VLLM_LOG" 2>&1 &
    echo "\$!" > "$VLLM_PID_FILE"
    # Wait for vLLM to come up
    for i in \$(seq 1 120); do
      if curl -s "http://127.0.0.1:$VLLM_PORT/v1/models" -H "Authorization: Bearer $STUDENT_27B_API_KEY" 2>/dev/null | grep -q "$VLLM_SERVED_NAME"; then
        echo "[\$(date -Is)] vLLM ready after \${i}0s" >> "$ORCHESTRATOR_LOG"
        break
      fi
      sleep 10
    done
  fi
  # Round cap (ablation budget). 0 = unbounded.
  if [[ "$PIPELINE_MAX_ROUNDS" -gt 0 && \$ROUND -ge "$PIPELINE_MAX_ROUNDS" ]]; then
    echo "[\$(date -Is)] reached PIPELINE_MAX_ROUNDS=$PIPELINE_MAX_ROUNDS; exiting orchestrator" >> "$ORCHESTRATOR_LOG"
    break
  fi
done
ORCH
chmod +x "$OUT/orchestrator.sh"

# Launch mode: submit as a job (default) or run directly on local NPUs.
# The user's policy (2026-07-09): training must ALWAYS be submitted as a
# job, not run on the environment's own NPUs. Set LAUNCH_MODE=local to
# override (e.g. for debugging on a dedicated training host).
LAUNCH_MODE="${LAUNCH_MODE:-job}"
JOB_NAME="${JOB_NAME:-rl-distill-27b-${RUN_ID}}"

if [[ "$LAUNCH_MODE" == "job" ]]; then
  log "submitting orchestrator as a job (name=$JOB_NAME) via scripts/ai_job.sh"
  JOB_REMOTE_CMD="cd \"$NAS_ROOT\" && bash \"$OUT/orchestrator.sh\""
  if scripts/ai_job.sh start "$JOB_NAME" "$ORCHESTRATOR_LOG" "$JOB_REMOTE_CMD" > "$OUT/job_submit.json" 2>&1; then
    JOB_ID="$(python3 -c "import json,sys; print(json.load(open('$OUT/job_submit.json')).get('job_id',''))" 2>/dev/null || echo "")"
    echo "$JOB_ID" > "$OUT/job.id"
    log "job submitted job_id=$JOB_ID name=$JOB_NAME log=$ORCHESTRATOR_LOG"
    log "monitor with: scripts/ai_job.sh status $JOB_ID"
    log "stop with:    scripts/ai_job.sh stop $JOB_ID"
  else
    log "WARNING: job submission failed; falling back to local nohup launch"
    nohup bash "$OUT/orchestrator.sh" >> "$ORCHESTRATOR_LOG" 2>&1 &
    echo "$!" > "$ORCHESTRATOR_PID_FILE"
    log "orchestrator launched (fallback) pid=$(cat "$ORCHESTRATOR_PID_FILE") log=$ORCHESTRATOR_LOG"
  fi
else
  log "LAUNCH_MODE=local; running orchestrator directly on local NPUs"
  nohup bash "$OUT/orchestrator.sh" >> "$ORCHESTRATOR_LOG" 2>&1 &
  echo "$!" > "$ORCHESTRATOR_PID_FILE"
  log "orchestrator launched pid=$(cat "$ORCHESTRATOR_PID_FILE") log=$ORCHESTRATOR_LOG"
fi

sleep 5
log "__ASI1_RL_DISTILL_LAUNCHED__ out=$OUT buffer=$BUFFER_DIR vllm_port=$VLLM_PORT mode=$LAUNCH_MODE"
log "monitor with: bash scripts/asi1_launch_rl_distill_27b_2npu.sh status"
log "stop with:    bash scripts/asi1_launch_rl_distill_27b_2npu.sh stop"
