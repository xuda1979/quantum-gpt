#!/usr/bin/env bash
# =============================================================================
# ASI2 launcher: Frontier-Verifier GSPO (FV-GSPO) training for Qwen3.8-27B.
#
# Architecture
# ------------
#   NPU 0..N -> GRPO trainer (Qwen3.8-27B + LoRA, generates samples + trains)
#   CPU      -> Periodic checkpoint sync to NAS (/root/work/filestorage/grpo_checkpoints)
#
# FV-GSPO (docs/frontier-verifier-gspo-design-2026-08-04.md):
#   - frontier router: probe each group, train only learnable frontier groups
#   - all-fail groups -> execution-verified repair queue (repair SFT/DPO stage)
#   - leave-one-out advantages (Dr.GRPO), no per-task std normalization
#   - GSPO sequence-level clipping (0.1/0.2 — recalibrated 2026-08-20: 3e-4/4e-4
#     pinned the policy (clip_high_fraction 0.5-0.75, inert adapter); the design
#     doc's 1e-3 top-of-sweep was still below observed drift at LR 2e-5)
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
MODEL_PATH="${MODEL_PATH:-/root/work/filestorage/Qwen3.8-27B}"
CONFIG_FILE="${CONFIG_FILE:-$NAS_ROOT/configs/rl/qwen36_27b_fv_gspo_asi2.json}"
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)}"
OUT="${OUT:-$NAS_ROOT/outputs/grpo-27b-selfeval-${RUN_ID}}"
NAS_CHECKPOINT_ROOT="${NAS_CHECKPOINT_ROOT:-/root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval}"
LOGDIR="${LOGDIR:-$NAS_ROOT/logs/grpo_27b_selfeval}"
TRAIN_LOG="$LOGDIR/grpo_train_${RUN_ID}.log"
PID_FILE="$LOGDIR/grpo_27b_selfeval.pid"
CHECKPOINT_PID_FILE="$LOGDIR/grpo_27b_checkpoint_sync.pid"
REPAIR_PID_FILE="$LOGDIR/grpo_27b_repair_sidecar.pid"
JUDGE_BRIDGE_PID_FILE="$LOGDIR/grpo_27b_judge_bridge.pid"
# Repair conversion feed consumed by the all_fail_without_repair circuit breaker.
# The FV-GSPO repair stage (scripts/fv_gspo_repair_stage.py) writes this file; if it
# is never wired, count_repair_conversions() always returns 0 and any all-fail run
# (common on hard tasks) trips the breaker and halts. Must point at the repair stage
# output so conversions actually unblock the breaker.
REPAIR_CONVERTED_JSONL="${REPAIR_CONVERTED_JSONL:-$OUT/repair_stage/repair_converted.jsonl}"
SELF_REPAIR_ROUNDS="${SELF_REPAIR_ROUNDS:-2}"   # teacher-free self-repair rounds per failed
                                                # candidate (plan §8: use 2); 0 disables.
                                                # Wired 2026-08-20: default 0 meant the only
                                                # positive-signal mechanism never ran.
                                                # reports/asi2_next_iteration_design_20260820.md
                                                # §C.3.1: trim to 1 (:-1) if step time exceeds
                                                # ~40 min (reaper window is 1-3h).
REPAIR_POLL_SECONDS="${REPAIR_POLL_SECONDS:-600}"

# ---- training hyperparams ----
# group 4 / cap 4 = the proven-safe operating point (p13/p18/p19 validated;
# group-8 train-logprob historically stalled on the sharded 27B). Smaller
# group also halves per-step time -> more steps per run before the platform
# reaps long sessions (~1-3h) -> faster cumulative policy drift per checkpoint.
GROUP_SIZE="${GROUP_SIZE:-4}"
MAX_ADAPTIVE_GROUP="${MAX_ADAPTIVE_GROUP:-4}"
GRPO_STEPS="${GRPO_STEPS:-500}"
INNER_EPOCHS="${INNER_EPOCHS:-1}"     # One update per independent rollout. The previous
                                       # value of two made 30 optimizer updates represent only
                                       # 15 fresh groups while executable pass yield was 1/60,
                                       # inflating apparent progress and spending compute on
                                       # duplicate data (2026-08-23 decision).
LR="${LR:-2e-4}"                       # 2026-08-25 relaunch escalation: run-3 (base-init, LR 1e-4,
                                       # alpha 64, SAPO) plateaued at merged max_abs_diff 4.88e-4
                                       # (INERT_AT_PRECISION at s11/s13, ACTIVE bar ~1e-3) — the
                                       # LR-1e-4 stack's effective movement saturates near the noise
                                       # boundary. LR 2e-4 (2x) is the pre-authorized relaunch stack
                                       # (reports/sapo-relaunch-package-lr2e4-2026-08-25.md).
KL_COEFF="${KL_COEFF:-0.01}"           # FV-GSPO initial KL beta (raised 2026-08-20: more policy
                                       # movement per step needs a slightly stronger anchor)
TEMPERATURE="${TEMPERATURE:-1.0}"      # 1.0 for sampling-policy consistency (review 2026-08-05)
TOP_P="${TOP_P:-1.0}"                  # 1.0 likewise; diversity comes from sampling
LORA_RANK="${LORA_RANK:-16}"
LORA_ALPHA="${LORA_ALPHA:-64}"   # corrected stack 2026-08-24 (escalation analysis): alpha 64 =
                                 # 2x merged delta (alpha/rank = 4 vs 2) at identical optimizer
                                 # state; same escalation rationale as LR.
# Save at the first completed step after thirty minutes. The timer is
# step-boundary based; 1800s preserves at most two groups of restart exposure
# while cutting the ~313 MB adapter write/sync rate by 2-3x vs 600s (2026-08-23).
CHECKPOINT_INTERVAL_SECONDS="${CHECKPOINT_INTERVAL_SECONDS:-1800}"
# R10 PREVENTIVE WAVE (2026-08-26 debug-lane F-A): greedy rollout fraction +
# entropy floor are trainer defaults (0.4 / 1.5 / 0.01) but passed EXPLICITLY
# here so boot echo + launch_config stay truthful. Env overrides tune without
# editing the launcher (the ASI3 wrapper pins ASI3_SAPO_* names over these).
GREEDY_ROLLOUT_FRACTION="${GREEDY_ROLLOUT_FRACTION:-0.4}"
ENTROPY_FLOOR="${ENTROPY_FLOOR:-1.5}"
ENTROPY_FLOOR_WEIGHT="${ENTROPY_FLOOR_WEIGHT:-0.01}"
# RUN-8 OOM FIX (2026-08-26): cap the differentiable entropy branch to the
# first N completion tokens (256 default) — the full-sequence fp32 autograd
# retention peaked at 59.8 GiB on NPU-0 at train-logprob (run-8 death).
ENTROPY_TOKEN_CAP="${ENTROPY_TOKEN_CAP:-256}"
# 2048-token completions are the proven budget on the 8-card layout (run 9 +
# the 08-23 fence-stop run: 0% truncation; the 1024 cap cut solutions
# mid-code -> checker fail -> reward 0). MAX_SEQ_LENGTH keeps prompt+completion
# headroom: the trainer's policy-math path truncates prompt+completion at
# max-seq-length, which would silently drop the tail tokens out of the SAPO
# token gate at a 2048 cap with 2048 seq length.
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-2048}"
MAX_ADAPTIVE_NEW_TOKENS="${MAX_ADAPTIVE_NEW_TOKENS:-$MAX_NEW_TOKENS}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-3072}"
LOGIT_CLIP="${LOGIT_CLIP:-50.0}"
DEVICE="${DEVICE:-npu}"
NUM_NPU="${NUM_NPU:-8}"
BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt}"

# ---- FV-GSPO: frontier router + mixture + GSPO clipping + breakers ----
# 2026-08-21: LOSS_MODE defaults to sapo — Soft Adaptive Policy Optimization
# (arXiv:2511.20347, Qwen team): smooth sigmoid gate g(r)=(4/tau)*sigmoid(tau*(r-1))
# over ALL tokens of each sample (token-level ratios, sequence LOO advantage);
# validated > GSPO/GRPO-R2 on code-gen (LiveCodeBench v6). Set LOSS_MODE=gspo
# to revert to the hard-clip sequence objective (clips 0.1/0.2 below).
LOSS_MODE="${LOSS_MODE:-sapo}"
SAPO_TAU_POS="${SAPO_TAU_POS:-1.0}"
SAPO_TAU_NEG="${SAPO_TAU_NEG:-1.05}"
GSPO_CLIP_LOW="${GSPO_CLIP_LOW:-0.1}"
GSPO_CLIP_HIGH="${GSPO_CLIP_HIGH:-0.2}"
ADVANTAGE_MODE="${ADVANTAGE_MODE:-loo}"
# 2026-08-24 (algorithm analyst): leave-one-out advantage scaling — 'none'
# keeps raw LOO (the measured small-drift cause); 'shared_mad' divides by one
# running MAD shared across tasks (Dr.GRPO-endorsed batch-level scaling; the
# ASI3 SAPO wrapper defaults this to shared_mad).
LOO_ADVANTAGE_SCALE="${LOO_ADVANTAGE_SCALE:-none}"
FRONTIER_THRESHOLD="${FRONTIER_THRESHOLD:-0.10}"
MASTERED_THRESHOLD="${MASTERED_THRESHOLD:-0.95}"
MIX_TARGETED="${MIX_TARGETED:-0.5}"
MIX_NEIGHBOR="${MIX_NEIGHBOR:-0.25}"
MIX_REPLAY="${MIX_REPLAY:-0.25}"
NEIGHBOR_WINDOW="${NEIGHBOR_WINDOW:-10}"
CIRCUIT_BREAKER_WINDOW="${CIRCUIT_BREAKER_WINDOW:-10}"
# 2026-08-20 recalibration (risk analysis reports/asi2_relaunch_risk_analysis_20260820.md):
# the default trust region (reject at seq_kl>0.05 OR clip_fraction>0.50) silently
# REVERTS every update once per-sequence ratios reach the clip edge at LR 2e-5 —
# a fresh adapter==base no-op vector. scale_lr keeps updates (halving LR on
# violation); ceilings 0.25/0.90 only guard real collapse. The clip-fraction
# circuit breaker gets the same 0.90 ceiling (0.50 trips the normal saturated-PPO
# regime after ~20 steps).
TRUST_REGION_ON_VIOLATION="${TRUST_REGION_ON_VIOLATION:-scale_lr}"
TRUST_REGION_MAX_SEQ_KL="${TRUST_REGION_MAX_SEQ_KL:-0.25}"
TRUST_REGION_MAX_CLIP_FRACTION="${TRUST_REGION_MAX_CLIP_FRACTION:-0.90}"
CIRCUIT_BREAKER_CLIP_FRACTION_LIMIT="${CIRCUIT_BREAKER_CLIP_FRACTION_LIMIT:-0.90}"
REWARD_MODE="${REWARD_MODE:-p_dominant}"   # comprehensive: R = w_P*P + w_S*S + w_J*J
REWARD_PASS_MASS="${REWARD_PASS_MASS:-0.50}"   # research memo 2026-08-26 r17
REWARD_SHAPED_MASS="${REWARD_SHAPED_MASS:-0.40}"
REWARD_JUDGE_MASS="${REWARD_JUDGE_MASS:-0.10}"  # calibration-gated: judge mass is 0 until a calibration file exists
# 2026-08-27 (r19, user binding): the reward judge is EXCLUSIVELY the Huanxin
# dp4 (deepseek-v4-flash) model, which scores ALL group candidates AT ONCE in a
# batch COMPARATIVE pass (same URL + API key as `claude -p huanxin -m dp4`) +
# group normalization of raw reward scores before the GRPO/SAPO advantage.
# Default OFF / 'none' / empty = inert (batch judge disabled entirely).
BATCH_COMPARATIVE_JUDGE="${BATCH_COMPARATIVE_JUDGE:-0}"
REWARD_NORMALIZATION="${REWARD_NORMALIZATION:-none}"
JUDGE_DP4_ENDPOINT="${JUDGE_DP4_ENDPOINT:-}"
JUDGE_DP4_MODEL="${JUDGE_DP4_MODEL:-dp4}"
JUDGE_DP4_MAX_TOKENS="${JUDGE_DP4_MAX_TOKENS:-4096}"
BATCH_COMPARATIVE_FLAG=()
if [[ "$BATCH_COMPARATIVE_JUDGE" == "1" ]]; then
  BATCH_COMPARATIVE_FLAG=(
    --batch-comparative-judge
    --judge-dp4-endpoint "$JUDGE_DP4_ENDPOINT"
    --judge-dp4-model "$JUDGE_DP4_MODEL"
    --judge-dp4-max-tokens "$JUDGE_DP4_MAX_TOKENS"
  )
fi
# 2026-08-27 (research audit P5): small positive brevity counterweight —
# length-degenerate outputs (run-5 prompt-echo class) get no free credit.
REWARD_BREVITY_WEIGHT="${REWARD_BREVITY_WEIGHT:-0.05}"
# 2026-08-26 (r16 judge wave, user directive): model-judge path ENABLED with
# the base 27B as judge. The judge runs on the SAME sharded model instance
# (the trainer shares it when --judge-model-path equals the training model
# path — the memory wall stays dead); the reward verifier recomputes every
# judge-scored total, so a miscalibrated judge is caught in numbers, not
# trusted blindly. 0 = disabled (legacy), 1 = enabled.
MODEL_JUDGE_ENABLED="${MODEL_JUDGE_ENABLED:-0}"
MODEL_JUDGE_PATH="${MODEL_JUDGE_PATH:-$MODEL_PATH}"
JUDGE_ARGS=()
if [[ "$MODEL_JUDGE_ENABLED" == "1" ]]; then
  JUDGE_ARGS=(--model-judge-enabled --judge-model-path "$MODEL_JUDGE_PATH")
fi

# ---- adaptive difficulty (boundary of capability) ----
CURRICULUM_EMA_DECAY="${CURRICULUM_EMA_DECAY:-0.9}"
CURRICULUM_MIN_WEIGHT="${CURRICULUM_MIN_WEIGHT:-0.05}"
MIN_REWARD_STD="${MIN_REWARD_STD:-0.05}"
ADAPTIVE_TEMP_STEP="${ADAPTIVE_TEMP_STEP:-0.15}"
# 2026-08-25 (router-watch reconciliation): ADAPTIVE_TEMP_MAX must equal the
# trainer's TEMP_ESCALATION_CEILING (1.3, grpo_trainer.py) — the clamp applies
# at construction (min(args.adaptive_temp_max, 1.3)) and use sites, so the old
# default of 2.0 was a display lie in launch_config.json (echoed 2.0, effective
# 1.3). Behavior unchanged; config == code == echo now.
ADAPTIVE_TEMP_MAX="${ADAPTIVE_TEMP_MAX:-1.3}"

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
    'loss_mode': '$LOSS_MODE',
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
# SOFT-RESUME (2026-08-25, lane #20): --resume-state continues the exact
# curriculum/router/temp/trust-region/repair state from a paused run's
# resume_state.json (trainer requires --adapter-init alongside).
if [[ "${RESUME_STATE:-}" != "" ]]; then
  RESUME_FLAGS+=(--resume-state "$RESUME_STATE")
  log "RESUME_STATE=$RESUME_STATE"
fi

# ---- stop subcommand ----
if [[ "${1:-}" == "stop" ]]; then
  log "stopping GRPO training, checkpoint sync, and repair sidecar..."
  # 2026-08-24 stop-script bug (manager): a stop left the live trainer running
  # ~30 min until manual kill because (a) the pidfile did not resolve the real
  # process (stale/wrong pid -> silent no-op) and (b) the KILL-escalation loop
  # re-read pidfiles that the first loop had already removed, so a TERM-
  # ignoring trainer survived forever. Resolve pids ONCE, fall back to
  # process-pattern discovery, TERM, then KILL the survivors, then clean up.
  target_pids=""
  for pf in "$PID_FILE" "$CHECKPOINT_PID_FILE" "$REPAIR_PID_FILE" "$JUDGE_BRIDGE_PID_FILE"; do
    if [[ -f "$pf" ]]; then
      pid="$(cat "$pf" 2>/dev/null || true)"
      if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        target_pids="${target_pids} ${pid}"
        log "resolved $pf pid=$pid"
      fi
    fi
  done
  # Pattern fallback: catch the trainer/sync/sidecar even when the pidfile is
  # stale or points at the wrong process. Bracket trick avoids self-match.
  for pattern in 'training/[g]rpo_trainer.py' 'checkpoint_sync_[d]aemon.sh' 'fv_gspo_repair_[s]idecar.sh' 'sapo_judge_[b]ridge.py'; do
    while read -r pid; do
      [[ -n "${pid:-}" ]] || continue
      case " ${target_pids} " in
        *" ${pid} "*) continue ;;
      esac
      target_pids="${target_pids} ${pid}"
      log "resolved by pattern ${pattern} pid=${pid}"
    done < <(pgrep -f "$pattern" 2>/dev/null || true)
  done
  if [[ -z "${target_pids// /}" ]]; then
    log "no trainer/sync/sidecar processes found to stop"
  else
    for pid in ${target_pids}; do
      log "TERM ${pid}"
      kill -TERM "${pid}" 2>/dev/null || true
    done
    sleep 3
    for pid in ${target_pids}; do
      if kill -0 "${pid}" 2>/dev/null; then
        log "KILL ${pid}"
        kill -KILL "${pid}" 2>/dev/null || true
      fi
    done
  fi
  rm -f "$PID_FILE" "$CHECKPOINT_PID_FILE" "$REPAIR_PID_FILE" "$JUDGE_BRIDGE_PID_FILE"
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
  if [[ -f "$REPAIR_PID_FILE" ]]; then
    pid="$(cat "$REPAIR_PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      log "Repair sidecar: RUNNING pid=$pid"
    else
      log "Repair sidecar: STOPPED (pid file stale)"
    fi
  else
    log "Repair sidecar: NOT RUNNING"
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
if [[ "$MODEL_JUDGE_ENABLED" == "1" ]]; then
  log "Model judge:    ENABLED (base $MODEL_JUDGE_PATH, shares the training model; reward verifier-watched)"
  log "Reward blend:   $REWARD_MODE ($REWARD_PASS_MASS pass / $REWARD_SHAPED_MASS shaped / $REWARD_JUDGE_MASS judge, judge calibration-gated)"
log "Brevity weight: $REWARD_BREVITY_WEIGHT (length counterweight)"
else
  log "Model judge:    disabled"
fi
log "Benchmark:      $BENCHMARK_FILE (training-only; held-out tasks excluded)"
log "Checkpoint interval: ${CHECKPOINT_INTERVAL_SECONDS}s (= every $((CHECKPOINT_INTERVAL_SECONDS / 60)) min)"
log "Curriculum EMA decay: $CURRICULUM_EMA_DECAY"
log "============================================================"

# ---- checkpoint sync daemon (saves adapters to NAS on CHECKPOINT_INTERVAL_SECONDS) ----
CHECKPOINT_SYNC_SCRIPT="$OUT/checkpoint_sync_daemon.sh"
cat > "$CHECKPOINT_SYNC_SCRIPT" << 'DAEMONEOF'
#!/usr/bin/env bash
# Runs as a background daemon: every CHECKPOINT_INTERVAL_SECONDS, copies the
# latest adapter from the GRPO output dir to the NAS checkpoint root.
set -euo pipefail
OUT="${1:?need output dir}"
NAS_ROOT="${2:?need NAS root}"
INTERVAL="${3:-1800}"
LOGFILE="${4:-/dev/null}"

logd() { printf '[%s] checkpoint-daemon: %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" | tee -a "$LOGFILE"; }

logd "daemon started. interval=${INTERVAL}s, out=$OUT, nas=$NAS_ROOT"
while true; do
  sleep "$INTERVAL"

  # Find the current adapter directory: prefer the newest step_*_adapter —
  # it is written FIRST and is complete; the flat "adapter" dir is written
  # second and can be stale/partial if the trainer is killed between the two
  # saves (2026-08-21 review finding #2).
  STEP_DIRS=$(ls -dt "$OUT"/step_*_adapter 2>/dev/null || true)
  STEP_LABEL="flat"
  if [[ -n "$STEP_DIRS" ]]; then
    ADAPTER_DIR=$(echo "$STEP_DIRS" | head -1)
    # Audit #5: name the snapshot after the TRAINING STEP, not just wall-clock,
    # so re-copies of the same adapter share a name instead of masquerading as
    # progress (the staleness detector could not tell re-copies apart before).
    STEP_LABEL=$(basename "$ADAPTER_DIR" | sed -nE 's/^step_([0-9]+)_adapter$/\1/p' || true)
    [[ "$STEP_LABEL" =~ ^[0-9]+$ ]] || STEP_LABEL="flat"
  else
    ADAPTER_DIR="$OUT/adapter"
    if [[ ! -d "$ADAPTER_DIR" ]]; then
      logd "no adapter dir found yet, skipping this sync cycle"
      continue
    fi
  fi

  TS=$(date +%Y%m%dT%H%M%S)
  # If a snapshot for this step already exists, refresh it in place (same
  # name) instead of minting a duplicate checkpoint_<newTS>.
  EXISTING=$(ls -dt "$NAS_ROOT"/checkpoint_*_step"$STEP_LABEL" 2>/dev/null | head -1 || true)
  if [[ -n "$EXISTING" ]]; then
    SNAPSHOT_DIR="$EXISTING"
  else
    SNAPSHOT_DIR="$NAS_ROOT/checkpoint_${TS}_step${STEP_LABEL}"
  fi
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

# ---- C-9122 grader-runtime preflight (fail-closed before trainer exec) ----
TRAINER_PY="${TRAINER_PY:-python3}"
if ! "$TRAINER_PY" harness/grader_runtime_preflight.py --interpreter "$TRAINER_PY"; then
  log "C-9122 FAIL-CLOSED: grader-runtime preflight failed in $TRAINER_PY -- refusing to launch"
  exit 3
fi

# ---- GRPO trainer ----
if [[ "$NPU_DEVICE_MAP" == "balanced-layers" ]]; then
  log "launching GRPO trainer as SINGLE process with balanced-layers NPU sharding..."
  RUN_CMD=(
    env MASTER_ADDR=127.0.0.1 MASTER_PORT=29500 WORLD_SIZE=1 RANK=0 LOCAL_RANK=0
    "$TRAINER_PY" training/grpo_trainer.py
    --npu-device-map balanced-layers
    --npu-max-memory-gib "$NPU_MAX_MEMORY_GIB"
  )
  NUM_NPU=1
else
  log "launching GRPO trainer on $NUM_NPU NPUs (torchrun DDP)..."
  RUN_CMD=("$TRAINER_PY" -m torch.distributed.run --nproc_per_node="$NUM_NPU" training/grpo_trainer.py)
fi

nohup "${RUN_CMD[@]}" \
  --model-name "$MODEL_PATH" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device "$DEVICE" \
  --group-size "$GROUP_SIZE" \
  --max-adaptive-group "$MAX_ADAPTIVE_GROUP" \
  --grpo-steps "$GRPO_STEPS" \
  --lr "$LR" \
  --kl-coeff "$KL_COEFF" \
  --temperature "$TEMPERATURE" \
  --adaptive-temp-step "$ADAPTIVE_TEMP_STEP" \
  --adaptive-temp-max "$ADAPTIVE_TEMP_MAX" \
  --top-p "$TOP_P" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --max-adaptive-new-tokens "$MAX_ADAPTIVE_NEW_TOKENS" \
  --max-seq-length "$MAX_SEQ_LENGTH" \
  --train-pass-max-seq-length "${TRAIN_PASS_MAX_SEQ_LENGTH:-2048}" \
  --greedy-rollout-fraction "$GREEDY_ROLLOUT_FRACTION" \
  --entropy-floor "$ENTROPY_FLOOR" \
  --entropy-floor-weight "$ENTROPY_FLOOR_WEIGHT" \
  --entropy-token-cap "$ENTROPY_TOKEN_CAP" \
  --reward-pass-weight 0.45 \
  --reward-syntax-weight 0.05 \
  --reward-interface-weight 0.10 \
  --reward-verifier-weight 0.10 \
  --reward-brevity-weight "$REWARD_BREVITY_WEIGHT" \
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
  --logit-clip "$LOGIT_CLIP" \
  --loss-mode "$LOSS_MODE" \
  --inner-epochs "$INNER_EPOCHS" \
  --sapo-tau-pos "$SAPO_TAU_POS" \
  --sapo-tau-neg "$SAPO_TAU_NEG" \
  --gspo-clip-low "$GSPO_CLIP_LOW" \
  --gspo-clip-high "$GSPO_CLIP_HIGH" \
  --advantage-mode "$ADVANTAGE_MODE" \
  --loo-advantage-scale "$LOO_ADVANTAGE_SCALE" \
  --frontier-threshold "$FRONTIER_THRESHOLD" \
  --mastered-threshold "$MASTERED_THRESHOLD" \
  --mix-targeted "$MIX_TARGETED" \
  --mix-neighbor "$MIX_NEIGHBOR" \
  --mix-replay "$MIX_REPLAY" \
  --neighbor-window "$NEIGHBOR_WINDOW" \
  --repair-queue-path "$OUT/repair_queue.jsonl" \
  --repair-converted-jsonl "$REPAIR_CONVERTED_JSONL" \
  --self-repair-rounds "$SELF_REPAIR_ROUNDS" \
  --circuit-breaker-window "$CIRCUIT_BREAKER_WINDOW" \
  --circuit-breaker-clip-fraction-limit "$CIRCUIT_BREAKER_CLIP_FRACTION_LIMIT" \
  --trust-region-on-violation "$TRUST_REGION_ON_VIOLATION" \
  --trust-region-max-seq-kl "$TRUST_REGION_MAX_SEQ_KL" \
  --trust-region-max-clip-fraction "$TRUST_REGION_MAX_CLIP_FRACTION" \
  --reward-mode "$REWARD_MODE" \
  --reward-pass-mass "$REWARD_PASS_MASS" \
  --reward-shaped-mass "$REWARD_SHAPED_MASS" \
  --reward-judge-mass "$REWARD_JUDGE_MASS" \
  --min-group-size "${MIN_GROUP_SIZE:-1}" \
  --reward-normalization "$REWARD_NORMALIZATION" \
  "${BATCH_COMPARATIVE_FLAG[@]}" \
  "${JUDGE_ARGS[@]}" \
  --model-judge-max-tokens 256 \
  "${RESUME_FLAGS[@]}" \
  > "$TRAIN_LOG" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"
disown "$PID" 2>/dev/null || true

# ---- repair sidecar (CPU-only) ----
# Converts the trainer's repair_queue.jsonl into verified SFT/DPO positives and
# keeps repair_converted.jsonl flowing so the all_fail_without_repair breaker
# never false-trips (diagnosed 2026-08-19: stage never ran in-loop).
nohup bash "$NAS_ROOT/scripts/fv_gspo_repair_sidecar.sh" "$OUT" \
  >> "$LOGDIR/repair_sidecar_${RUN_ID}.log" 2>&1 &
echo "$!" > "$REPAIR_PID_FILE"
disown "$(cat "$REPAIR_PID_FILE")" 2>/dev/null || true
log "repair sidecar launched pid=$(cat "$REPAIR_PID_FILE") (poll ${REPAIR_POLL_SECONDS}s)"

# ---- judge bridge sidecar (dp4 judge only) ----
# 2026-08-27 (JUDGE BRIDGE lane): the box has no route to the dp4 subscription;
# the bridge stages the trainer's batch judge call and a Mac-side watcher
# (scripts/sapo_judge_mac_watcher.py) resolves it through the Mac dp4 proxy.
# Started ONLY when the batch comparative judge is on (inert otherwise).
if [[ "$BATCH_COMPARATIVE_JUDGE" == "1" ]]; then
  mkdir -p "$OUT/judge_bridge"
  nohup python3 "$NAS_ROOT/scripts/sapo_judge_bridge.py"     --queue-dir "$OUT/judge_bridge"     --port "${JUDGE_BRIDGE_PORT:-56237}"     >> "$LOGDIR/judge_bridge_${RUN_ID}.log" 2>&1 &
  echo "$!" > "$JUDGE_BRIDGE_PID_FILE"
  disown "$(cat "$JUDGE_BRIDGE_PID_FILE")" 2>/dev/null || true
  log "judge bridge launched pid=$(cat "$JUDGE_BRIDGE_PID_FILE") queue=$OUT/judge_bridge"
fi

log "============================================================"
log "__ASI2_GRPO_27B_SELFEVAL_LAUNCHED__"
log "Trainer PID: $PID"
log "Checkpoint daemon PID: $(cat "$CHECKPOINT_PID_FILE")"
log "Repair sidecar PID: $(cat "$REPAIR_PID_FILE")"
log "Train log: $TRAIN_LOG"
log "Output dir: $OUT"
log "NAS checkpoints: $NAS_CHECKPOINT_ROOT"
log "Monitor:  bash scripts/asi2_launch_grpo_27b_selfeval.sh status"
log "Stop:     bash scripts/asi2_launch_grpo_27b_selfeval.sh stop"
log "Tail log: tail -f $TRAIN_LOG"
log "============================================================"
