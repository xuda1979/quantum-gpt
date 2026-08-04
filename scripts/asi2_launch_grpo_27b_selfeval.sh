#!/usr/bin/env bash
# =============================================================================
# ASI2 launcher: Frontier-Verifier GSPO (FV-GSPO) training for Qwen3.6-27B.
#
# Architecture
# ------------
#   NPU 0..N -> GRPO trainer (Qwen3.6-27B + LoRA, generates samples + trains)
#   CPU      -> Periodic checkpoint sync to NAS (/root/work/filestorage/grpo_checkpoints)
#
# FV-GSPO (docs/frontier-verifier-gspo-design-2026-08-04.md):
#   - frontier router: probe each group, train only learnable frontier groups
#   - all-fail groups -> execution-verified repair queue (repair SFT/DPO stage)
#   - leave-one-out advantages (Dr.GRPO), no per-task std normalization
#   - GSPO sequence-level clipping (calibrated 3e-4/4e-4, NOT DAPO's 0.2/0.28)
#   - 50% targeted / 25% neighboring variants / 25% replay sampling
#   - executable tests authoritative; self-judge reward weight = 0
#   - circuit breakers: non-finite, clip fraction, entropy collapse,
#     all-fail-without-repair (trips after two windows -> halt)
#
# Usage:
#   bash scripts/asi2_launch_grpo_27b_selfeval.sh launch
#   bash scripts/asi2_launch_grpo_27b_selfeval.sh status
#   bash scripts/asi2_launch_grpo_27b_selfeval.sh stop
# =============================================================================

set -euo pipefail

SCRIPT_NAME="asi2_launch_grpo_27b_selfeval"
export TZ="${TZ:-Asia/Shanghai}"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*"; }

# ---- paths ----
NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
MODEL_PATH="${MODEL_PATH:-/root/work/filestorage/Qwen3.6-27B}"
CONFIG_FILE="${CONFIG_FILE:-$NAS_ROOT/configs/rl/qwen36_27b_fv_gspo_asi2.json}"
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)}"
OUT="${OUT:-$NAS_ROOT/outputs/grpo-27b-selfeval-${RUN_ID}}"
NAS_CHECKPOINT_ROOT="${NAS_CHECKPOINT_ROOT:-/root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval}"
LOGDIR="${LOGDIR:-$NAS_ROOT/logs/grpo_27b_selfeval}"
TRAIN_LOG="$LOGDIR/grpo_train_${RUN_ID}.log"
PID_FILE="$LOGDIR/grpo_27b_selfeval.pid"
CHECKPOINT_PID_FILE="$LOGDIR/grpo_27b_checkpoint_sync.pid"

# ---- training hyperparams ----
GROUP_SIZE="${GROUP_SIZE:-8}"
GRPO_STEPS="${GRPO_STEPS:-500}"
LR="${LR:-2e-6}"                       # FV-GSPO: 1e-6..3e-6 LoRA; legacy 1e-5 is aggressive
KL_COEFF="${KL_COEFF:-0.005}"          # FV-GSPO initial KL beta (design table)
TEMPERATURE="${TEMPERATURE:-0.8}"
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-32}"
CHECKPOINT_INTERVAL_SECONDS="${CHECKPOINT_INTERVAL_SECONDS:-7200}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-1024}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-2048}"
DEVICE="${DEVICE:-npu}"
NUM_NPU="${NUM_NPU:-4}"
BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_grpo_training_v1.txt}"

# ---- FV-GSPO: frontier router + mixture + GSPO clipping + breakers ----
LOSS_MODE="${LOSS_MODE:-gspo}"
GSPO_CLIP_LOW="${GSPO_CLIP_LOW:-0.0003}"
GSPO_CLIP_HIGH="${GSPO_CLIP_HIGH:-0.0004}"
ADVANTAGE_MODE="${ADVANTAGE_MODE:-loo}"
FRONTIER_THRESHOLD="${FRONTIER_THRESHOLD:-0.10}"
MASTERED_THRESHOLD="${MASTERED_THRESHOLD:-0.95}"
MIX_TARGETED="${MIX_TARGETED:-0.5}"
MIX_NEIGHBOR="${MIX_NEIGHBOR:-0.25}"
MIX_REPLAY="${MIX_REPLAY:-0.25}"
NEIGHBOR_WINDOW="${NEIGHBOR_WINDOW:-10}"
CIRCUIT_BREAKER_WINDOW="${CIRCUIT_BREAKER_WINDOW:-10}"

# ---- adaptive difficulty (boundary of capability) ----
CURRICULUM_EMA_DECAY="${CURRICULUM_EMA_DECAY:-0.9}"
CURRICULUM_MIN_WEIGHT="${CURRICULUM_MIN_WEIGHT:-0.05}"
MIN_REWARD_STD="${MIN_REWARD_STD:-0.05}"
ADAPTIVE_TEMP_STEP="${ADAPTIVE_TEMP_STEP:-0.15}"
ADAPTIVE_TEMP_MAX="${ADAPTIVE_TEMP_MAX:-2.0}"

# ---- dry-run mode (for browser-automation deriveLaunchSpec) ----
if [[ "${1:-}" == "--dry-run" ]]; then
  # Output JSON launch spec for the browser-automation submit script
  python3 -c "
import json
spec = {
    'remote_root': '$NAS_ROOT',
    'execution_command': 'cd $NAS_ROOT && bash scripts/asi2_launch_grpo_27b_selfeval.sh launch',
    'remote_command': 'bash scripts/asi2_launch_grpo_27b_selfeval.sh launch',
    'output_dir': '$OUT',
    'log_path': '$TRAIN_LOG',
    'job_name': 'asi2-grpo-27b-selfeval',
    'group_size': '$GROUP_SIZE',
    'grpo_steps': '$GRPO_STEPS',
    'checkpoint_interval_seconds': '$CHECKPOINT_INTERVAL_SECONDS',
    'model_path': '$MODEL_PATH',
    'nas_checkpoint_root': '$NAS_CHECKPOINT_ROOT',
    'self_eval_enabled': 'false',
    'loss_mode': 'gspo',
    'gspo_clip_low': '$GSPO_CLIP_LOW',
    'gspo_clip_high': '$GSPO_CLIP_HIGH',
    'advantage_mode': 'loo',
    'benchmark_file': '$BENCHMARK_FILE',
}
print(json.dumps(spec, indent=2))
"
  exit 0
fi

mkdir -p "$LOGDIR" "$OUT" "$NAS_CHECKPOINT_ROOT"

# ---- resume support ----
RESUME_FLAGS=()
if [[ "${RESUME_FROM:-}" != "" ]]; then
  RESUME_FLAGS=(--resume-from "$RESUME_FROM")
  log "RESUME_FROM=$RESUME_FROM"
fi
if [[ "${ADAPTER_INIT:-}" != "" ]]; then
  RESUME_FLAGS+=(--adapter-init "$ADAPTER_INIT")
  log "ADAPTER_INIT=$ADAPTER_INIT"
fi

# ---- stop subcommand ----
if [[ "${1:-}" == "stop" ]]; then
  log "stopping GRPO training and checkpoint sync..."
  for pf in "$PID_FILE" "$CHECKPOINT_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        log "killing $pf pid=$pid"
        kill -TERM "$pid" 2>/dev/null || true
      fi
      rm -f "$pf"
    fi
  done
  sleep 3
  for pf in "$PID_FILE" "$CHECKPOINT_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        kill -KILL "$pid" 2>/dev/null || true
      fi
      rm -f "$pf"
    fi
  done
  log "stopped."
  exit 0
fi

# ---- status subcommand ----
if [[ "${1:-}" == "status" ]]; then
  log "=== GRPO 27B Self-Eval Status ==="
  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      log "GRPO trainer: RUNNING pid=$pid"
    else
      log "GRPO trainer: STOPPED (pid file stale)"
    fi
  else
    log "GRPO trainer: NOT RUNNING"
  fi
  if [[ -f "$CHECKPOINT_PID_FILE" ]]; then
    pid="$(cat "$CHECKPOINT_PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      log "Checkpoint sync: RUNNING pid=$pid"
    else
      log "Checkpoint sync: STOPPED (pid file stale)"
    fi
  else
    log "Checkpoint sync: NOT RUNNING"
  fi
  log "NAS checkpoint root: $NAS_CHECKPOINT_ROOT"
  if [[ -d "$NAS_CHECKPOINT_ROOT" ]]; then
    log "Checkpoints on NAS:"
    ls -la "$NAS_CHECKPOINT_ROOT/" 2>/dev/null | tail -20 || log "(empty)"
  fi
  log "Train log: $TRAIN_LOG"
  if [[ -f "$TRAIN_LOG" ]]; then
    log "Last 10 lines:"
    tail -10 "$TRAIN_LOG"
  fi
  exit 0
fi

# ---- launch (default) ----
if [[ "${1:-}" != "launch" ]]; then
  echo "Usage: $0 {launch|status|stop}" >&2
  exit 1
fi

# ---- preflight checks ----
if [[ ! -d "$NAS_ROOT" ]]; then
  log "ERROR: NAS root $NAS_ROOT does not exist" >&2
  exit 1
fi
if [[ ! -d "$MODEL_PATH" ]]; then
  log "ERROR: model path $MODEL_PATH does not exist" >&2
  exit 1
fi
cd "$NAS_ROOT"

log "============================================================"
log "GRPO 27B Self-Eval Training Launch"
log "============================================================"
log "NAS root:       $NAS_ROOT"
log "Model:          $MODEL_PATH"
log "Output dir:     $OUT"
log "Checkpoint NAS: $NAS_CHECKPOINT_ROOT"
log "Log:            $TRAIN_LOG"
log "Group size:     $GROUP_SIZE"
log "GRPO steps:     $GRPO_STEPS"
log "LR:             $LR"
log "Temperature:    $TEMPERATURE"
log "Loss mode:      $LOSS_MODE (GSPO clips $GSPO_CLIP_LOW/$GSPO_CLIP_HIGH)"
log "Advantage:      $ADVANTAGE_MODE leave-one-out (no per-task std norm)"
log "Mix:            $MIX_TARGETED targeted / $MIX_NEIGHBOR neighbor / $MIX_REPLAY replay"
log "Self-judge:     disabled (zero reward weight until executable-label calibration)"
log "Benchmark:      $BENCHMARK_FILE (training-only; held-out tasks excluded)"
log "Checkpoint interval: ${CHECKPOINT_INTERVAL_SECONDS}s (= every 2h)"
log "Curriculum EMA decay: $CURRICULUM_EMA_DECAY"
log "============================================================"

# ---- checkpoint sync daemon (saves adapters to NAS every 2h) ----
CHECKPOINT_SYNC_SCRIPT="$OUT/checkpoint_sync_daemon.sh"
cat > "$CHECKPOINT_SYNC_SCRIPT" << 'DAEMONEOF'
#!/usr/bin/env bash
# Runs as a background daemon: every CHECKPOINT_INTERVAL_SECONDS, copies the
# latest adapter from the GRPO output dir to the NAS checkpoint root.
set -euo pipefail
OUT="${1:?need output dir}"
NAS_ROOT="${2:?need NAS root}"
INTERVAL="${3:-7200}"
LOGFILE="${4:-/dev/null}"

logd() { printf '[%s] checkpoint-daemon: %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" | tee -a "$LOGFILE"; }

logd "daemon started. interval=${INTERVAL}s, out=$OUT, nas=$NAS_ROOT"
while true; do
  sleep "$INTERVAL"

  # Find the current adapter directory
  ADAPTER_DIR="$OUT/adapter"
  if [[ ! -d "$ADAPTER_DIR" ]]; then
    # Try step-based checkpoints
    STEP_DIRS=$(ls -dt "$OUT"/step_*_adapter 2>/dev/null || true)
    if [[ -z "$STEP_DIRS" ]]; then
      logd "no adapter dir found yet, skipping this sync cycle"
      continue
    fi
    ADAPTER_DIR=$(echo "$STEP_DIRS" | head -1)
  fi

  TS=$(date +%Y%m%dT%H%M%S)
  SNAPSHOT_DIR="$NAS_ROOT/checkpoint_${TS}"
  mkdir -p "$SNAPSHOT_DIR"

  logd "syncing adapter from $ADAPTER_DIR -> $SNAPSHOT_DIR"
  if cp -a "$ADAPTER_DIR"/* "$SNAPSHOT_DIR/" 2>/dev/null; then
    # Copy metrics if available
    for mf in "$OUT"/grpo_metrics.json "$OUT"/grpo_step_metrics.jsonl; do
      if [[ -f "$mf" ]]; then
        cp "$mf" "$SNAPSHOT_DIR/" 2>/dev/null || true
      fi
    done
    logd "checkpoint saved: $SNAPSHOT_DIR"

    # Rotate: keep only the latest N checkpoints
    RETAIN="${5:-5}"
    ALL_CHECKPOINTS=$(ls -dt "$NAS_ROOT"/checkpoint_* 2>/dev/null || true)
    COUNT=0
    for CP in $ALL_CHECKPOINTS; do
      COUNT=$((COUNT + 1))
      if [[ $COUNT -gt $RETAIN ]]; then
        logd "rotating old checkpoint: $CP"
        rm -rf "$CP"
      fi
    done
  else
    logd "ERROR: failed to copy adapter to $SNAPSHOT_DIR"
  fi
done
DAEMONEOF
chmod +x "$CHECKPOINT_SYNC_SCRIPT"

nohup bash "$CHECKPOINT_SYNC_SCRIPT" \
  "$OUT" "$NAS_CHECKPOINT_ROOT" "$CHECKPOINT_INTERVAL_SECONDS" "$LOGDIR/checkpoint_sync.log" "5" \
  >> "$LOGDIR/checkpoint_sync.log" 2>&1 &
echo "$!" > "$CHECKPOINT_PID_FILE"
disown "$(cat "$CHECKPOINT_PID_FILE")" 2>/dev/null || true
log "checkpoint sync daemon launched pid=$(cat "$CHECKPOINT_PID_FILE")"

# ---- GRPO trainer ----
log "launching GRPO trainer on $NUM_NPU NPUs..."

nohup torchrun --nproc_per_node="$NUM_NPU" training/grpo_trainer.py \
  --model-name "$MODEL_PATH" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device "$DEVICE" \
  --group-size "$GROUP_SIZE" \
  --grpo-steps "$GRPO_STEPS" \
  --lr "$LR" \
  --kl-coeff "$KL_COEFF" \
  --temperature "$TEMPERATURE" \
  --adaptive-temp-step "$ADAPTIVE_TEMP_STEP" \
  --adaptive-temp-max "$ADAPTIVE_TEMP_MAX" \
  --top-p 0.95 \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --max-seq-length "$MAX_SEQ_LENGTH" \
  --reward-pass-weight 0.45 \
  --reward-syntax-weight 0.05 \
  --reward-interface-weight 0.10 \
  --reward-verifier-weight 0.10 \
  --reward-import-hygiene-weight 0.05 \
  --lora-rank "$LORA_RANK" \
  --lora-alpha "$LORA_ALPHA" \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --freeze-param-regex '.*\.(mlp\.gate|router)\..*' \
  --benchmark-file "$BENCHMARK_FILE" \
  --domain-filter quantum \
  --curriculum-ema-decay "$CURRICULUM_EMA_DECAY" \
  --curriculum-min-weight "$CURRICULUM_MIN_WEIGHT" \
  --min-reward-std "$MIN_REWARD_STD" \
  --checkpoint-interval-seconds "$CHECKPOINT_INTERVAL_SECONDS" \
  --logit-clip 5.0 \
  --loss-mode "$LOSS_MODE" \
  --gspo-clip-low "$GSPO_CLIP_LOW" \
  --gspo-clip-high "$GSPO_CLIP_HIGH" \
  --advantage-mode "$ADVANTAGE_MODE" \
  --frontier-threshold "$FRONTIER_THRESHOLD" \
  --mastered-threshold "$MASTERED_THRESHOLD" \
  --mix-targeted "$MIX_TARGETED" \
  --mix-neighbor "$MIX_NEIGHBOR" \
  --mix-replay "$MIX_REPLAY" \
  --neighbor-window "$NEIGHBOR_WINDOW" \
  --repair-queue-path "$OUT/repair_queue.jsonl" \
  --circuit-breaker-window "$CIRCUIT_BREAKER_WINDOW" \
  "${RESUME_FLAGS[@]}" \
  > "$TRAIN_LOG" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"
disown "$PID" 2>/dev/null || true

log "============================================================"
log "__ASI2_GRPO_27B_SELFEVAL_LAUNCHED__"
log "Trainer PID: $PID"
log "Checkpoint daemon PID: $(cat "$CHECKPOINT_PID_FILE")"
log "Train log: $TRAIN_LOG"
log "Output dir: $OUT"
log "NAS checkpoints: $NAS_CHECKPOINT_ROOT"
log "Monitor:  bash scripts/asi2_launch_grpo_27b_selfeval.sh status"
log "Stop:     bash scripts/asi2_launch_grpo_27b_selfeval.sh stop"
log "Tail log: tail -f $TRAIN_LOG"
log "============================================================"
