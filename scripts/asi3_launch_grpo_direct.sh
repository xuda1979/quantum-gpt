#!/usr/bin/env bash
# =============================================================================
# asi3_launch_grpo_direct.sh — historical compatibility name for the canonical
# Huanxin AI FV-GSPO/SAPO launcher. New runs enter via ai_launch_sapo_direct.sh;
# the lower-level defaults are AI-safe as a second line of defense.
#
# The AI entrypoint pins /root/software/quantum-gpt, its models tree, and all
# eight visible NPUs. The historical ASI3_SAPO_* variable names remain accepted
# only so prior run cards can be replayed without silently changing parameters.
#
# Usage (from the Huanxin AI shell):
#   bash scripts/asi3_launch_grpo_direct.sh {launch|status|stop}
#
# Persistent Huanxin webshells retain exported variables from earlier runs.
# Never inherit generic LR/LORA/MAX_NEW_TOKENS/etc. here: doing so launched the
# 2026-08-22 SAPO run with stale LR=1e-4, alpha=64, max_new_tokens=2048, and a
# different benchmark. Explicit ASI3_SAPO_* names are the only override path.
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCHER="${ASI3_SAPO_LAUNCHER:-$ROOT_DIR/scripts/asi2_launch_grpo_27b_selfeval.sh}"

case "${1:-}" in
  launch|status|stop) ;;
  *) echo "Usage: $0 {launch|status|stop}" >&2; exit 1 ;;
esac

# ---- fixed ASI3 SAPO settings (ambient-shell-proof) ----
# Every variable consumed by the generic ASI2-compatible launcher is assigned
# here. Huanxin webshells are persistent, so leaving paths/resume flags
# untouched can silently continue an old adapter or write into an old run.
export NAS_ROOT="${ASI3_SAPO_ROOT:-/root/software/quantum-gpt}"
export MODEL_PATH="${ASI3_SAPO_MODEL_PATH:-$NAS_ROOT/models/Qwen3.6-27B}"
export CONFIG_FILE="${ASI3_SAPO_CONFIG_FILE:-$NAS_ROOT/configs/rl/qwen36_27b_fv_gspo_asi2.json}"
export RUN_ID="${ASI3_SAPO_RUN_ID:-$(date +%Y%m%dT%H%M%S)}"
export OUT="${ASI3_SAPO_OUT:-$NAS_ROOT/outputs/sapo-27b-ai-${RUN_ID}}"
export NAS_CHECKPOINT_ROOT="${ASI3_SAPO_CHECKPOINT_ROOT:-$NAS_ROOT/outputs/checkpoints/qwen36_27b_sapo_ai}"
export LOGDIR="${ASI3_SAPO_LOGDIR:-$NAS_ROOT/logs/sapo_27b_ai}"
export DEVICE="npu"

# Qwen3.6-27B does not fit as one DDP replica per card. balanced-layers is a
# single process whose model layers are sharded across the explicitly visible
# eight cards. Fixing visibility prevents a stale 1/2-card shell export from
# silently leaving ASI3 capacity idle.
export NUM_NPU="8"
export NPU_DEVICE_MAP="balanced-layers"
export ASCEND_RT_VISIBLE_DEVICES="0,1,2,3,4,5,6,7"
export ASCEND_VISIBLE_DEVICES="0,1,2,3,4,5,6,7"
export NPU_MAX_MEMORY_GIB="${ASI3_SAPO_NPU_MAX_MEMORY_GIB:-54}"
export GROUP_SIZE="${ASI3_SAPO_GROUP_SIZE:-4}"
export MAX_ADAPTIVE_GROUP="${ASI3_SAPO_MAX_ADAPTIVE_GROUP:-4}"
# 2026-08-27 (r19, user binding): every round rolls out 8 candidates. The router's
# adaptive-4 recommendation is overridden by a HARD floor. Default 1 = inert.
export MIN_GROUP_SIZE="${ASI3_SAPO_MIN_GROUP_SIZE:-1}"
export GRPO_STEPS="${ASI3_SAPO_STEPS:-500}"
# A group currently takes about 14 minutes, so a 600-second timer writes an
# immutable ~313 MB checkpoint plus the flat adapter after every group. Thirty
# minutes preserves at most two groups of restart exposure while cutting the
# checkpoint write/sync rate by roughly 2-3x.
export CHECKPOINT_INTERVAL_SECONDS="${ASI3_SAPO_CHECKPOINT_SECONDS:-1800}"
export LOSS_MODE="sapo"
export SAPO_TAU_POS="${ASI3_SAPO_TAU_POS:-1.0}"
export SAPO_TAU_NEG="${ASI3_SAPO_TAU_NEG:-1.05}"
# 2026-08-24 escalation analysis (reports/sapo-escalation-analysis-2026-08-24.md):
# run-2 (base-init, shared_mad, LR 5e-5) earned only 2.5e-5 B/update (1e-4 ->
# 2e-4 over steps 4-8); run-1's 'active' 3.8e-3 B was inherited warm-SFT LoRA.
# 2026-08-25 relaunch escalation (reports/sapo-relaunch-package-lr2e4-2026-08-25.md):
# run-3 (LR 1e-4) plateaued at merged max_abs_diff 4.88e-4 (INERT_AT_PRECISION
# at s11/s13, ACTIVE bar ~1e-3) — the LR-1e-4 stack's effective movement
# saturates near the noise boundary. Relaunch stack: LR 2e-4 (2x; kl_after
# ~2.6e-3/update projected, still ~100x below the 0.25 trust-region ceiling).
# 2026-09-01 (manager, entropy-blowup fix): RUN-12 at LR 2e-4 caused CAPABILITY
# EROSION — entropy exploded 0.055 -> 1.59 (28x), 16 trust-region violation
# windows, uniform rubric losses vs base (STANDUP #227b deep-cause). RUN-13
# relaunched at LR 5e-5 (4x lower) with the working judge + entropy floor +
# recalibrated clips (STANDUP #233). The DEFAULT is now the calibrated 5e-5 so
# ANY relaunch (resurrector/manual) without an explicit override gets the safe
# stack. Escalate only deliberately via ASI3_SAPO_LR.
export LR="${ASI3_SAPO_LR:-5e-5}"
export KL_COEFF="${ASI3_SAPO_KL_COEFF:-0.01}"
# One update per independent rollout. The previous value of two made 30
# optimizer updates represent only 15 fresh groups while executable pass yield
# was 1/60, inflating apparent progress and spending compute on duplicate data.
export INNER_EPOCHS="${ASI3_SAPO_INNER_EPOCHS:-1}"
export LORA_RANK="${ASI3_SAPO_LORA_RANK:-16}"
# alpha 64 = 2x merged delta (alpha/rank = 4 vs 2) at identical optimizer
# state — same escalation rationale as LR; B target for meaningful movement
# halves. Rollback: ASI3_SAPO_LORA_ALPHA=32.
export LORA_ALPHA="${ASI3_SAPO_LORA_ALPHA:-64}"
# 2048-token completions are the proven budget on the 8-card layout: run 9
# and the 08-23 fence-stop run both completed train-logprob at this cap with
# 0% truncation, while the OOM-era 512/1024 stopgap cut solutions mid-code
# (avg 1019.75 tokens -> checker fail -> reward 0). MAX_SEQ_LENGTH keeps
# prompt+completion headroom: the trainer's policy-math path truncates
# prompt+completion at max-seq-length, so a 2048 cap with 2048 seq length
# would silently drop the tail tokens out of the SAPO token gate.
export MAX_NEW_TOKENS="${ASI3_SAPO_MAX_NEW_TOKENS:-2048}"
export MAX_ADAPTIVE_NEW_TOKENS="${ASI3_SAPO_MAX_ADAPTIVE_NEW_TOKENS:-2048}"
export MAX_SEQ_LENGTH="${ASI3_SAPO_MAX_SEQ_LENGTH:-3072}"
# 2026-08-25 OOM fix (run-4, sapo-27b-ai-20260825T052636): the train pass
# (current-policy log-probs + SAPO token loss) is computed on at most the
# first N tokens of each candidate; rollout log-probs/eval/reward stay on the
# full sequence. Run-4 died when a long v8 prompt + 4x2048-token completions
# (truncation_rate 1.0) blew the grad-enabled forward's activation peak on
# the lm_head card (59.90 GiB live of 60.96; 38 MiB attempt failed).
# Rollback: ASI3_SAPO_TRAIN_PASS_MAX_SEQ_LENGTH=0 disables the cap.
export TRAIN_PASS_MAX_SEQ_LENGTH="${ASI3_SAPO_TRAIN_PASS_MAX_SEQ_LENGTH:-2048}"
export LOGIT_CLIP="${ASI3_SAPO_LOGIT_CLIP:-50.0}"
# Semantic-stdout distill tasks remain an explicit opt-in until their checker
# binds every scored value to runtime quantum-execution provenance.  The safe
# default is the 20-task holdout-adjacent set (v8 = v7 targeted10 + 10 new
# tasks mapped 1:1 to the frozen-holdout failure classes; v7 intact, header
# hashes valid; builder scripts/build_grpo_v8_manifest.py --check green) —
# 2026-08-25 relaunch decision, evidence in
# reports/sapo-relaunch-package-lr2e4-2026-08-25.md. The v7-targeted10 file
# remains the manifest source and stays deploy-required.
export BENCHMARK_FILE="${ASI3_SAPO_BENCHMARK_FILE:-evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt}"
# In-loop repair samples come from a different prompt and therefore cannot be
# credited with the original rollout's log-probability. Keep them out of the
# on-policy SAPO update; the repair sidecar may consume them later via SFT/DPO.
export SELF_REPAIR_ROUNDS="0"
export REPAIR_POLL_SECONDS="${ASI3_SAPO_REPAIR_POLL_SECONDS:-60}"
export RESUME_FROM="${ASI3_SAPO_RESUME_FROM:-}"
export ADAPTER_INIT="${ASI3_SAPO_ADAPTER_INIT:-}"
# SOFT-RESUME (2026-08-25, lane #20): point ASI3_SAPO_RESUME_STATE at a paused
# run's outputs/<run>/resume_state.json to continue the exact curriculum/
# router/temperature/trust-region/repair state (step counter, curriculum EMA,
# task-seen counts, repair-converted ledger) instead of re-walking early tasks.
# Requires ASI3_SAPO_ADAPTER_INIT (the paused checkpoint's weights) — the
# trainer refuses a state file over fresh weights (silent policy rewind).
export RESUME_STATE="${ASI3_SAPO_RESUME_STATE:-}"
# R10 PREVENTIVE WAVE (2026-08-26 debug-lane F-A): the greedy/entropy-floor
# knobs default in the trainer (0.4 / 1.5 / 0.03 — entropy-floor-weight was
# strengthened 0.01 -> 0.03 by research audit T1c 2026-08-27) but MUST be
# passed explicitly so the boot echo + launch_config are truthful. The pinned
# 0.01 below remains the RUN-13 config; raise to 0.03 deliberately via
# ASI3_SAPO_ENTROPY_FLOOR_WEIGHT when the T1c strengthening is wanted.
# Env overrides allow a future launch to tune them without editing the launcher.
export GREEDY_ROLLOUT_FRACTION="${ASI3_SAPO_GREEDY_ROLLOUT_FRACTION:-0.4}"
export ENTROPY_FLOOR="${ASI3_SAPO_ENTROPY_FLOOR:-1.5}"
export ENTROPY_FLOOR_WEIGHT="${ASI3_SAPO_ENTROPY_FLOOR_WEIGHT:-0.01}"
# RUN-8 OOM FIX (2026-08-26): the differentiable entropy branch retains per-chunk
# fp32 tensors over the FULL completion sequence (run-8 peak 59.8 GiB at
# train-logprob); --entropy-token-cap bounds the entropy mean to the first N
# completion tokens (rollout entropy for degenerate alarms is never capped).
export ENTROPY_TOKEN_CAP="${ASI3_SAPO_ENTROPY_TOKEN_CAP:-256}"
# The generic launcher reads REPAIR_CONVERTED_JSONL with a default; pin it
# here or a persistent-webshell export silently redirects the repair
# conversion ledger -> count_repair_conversions() sees 0 -> the
# all_fail_without_repair breaker false-trips (2026-08-24 bug-hunt).
export REPAIR_CONVERTED_JSONL="${ASI3_SAPO_REPAIR_CONVERTED_JSONL:-$OUT/repair_stage/repair_converted.jsonl}"

# Pin the less frequently changed knobs too; stale generic values must never
# mutate a supposedly canonical ASI3 SAPO launch.
export TEMPERATURE="${ASI3_SAPO_TEMPERATURE:-1.0}"
export TOP_P="${ASI3_SAPO_TOP_P:-1.0}"
export GSPO_CLIP_LOW="${ASI3_SAPO_GSPO_CLIP_LOW:-0.1}"
export GSPO_CLIP_HIGH="${ASI3_SAPO_GSPO_CLIP_HIGH:-0.2}"
export ADVANTAGE_MODE="loo"
# 2026-08-24 (algorithm analyst): raw LOO advantages (scale 'none') produced
# the measured small-drift signature (ratio_mean ~1.0003, seq_kl ~2e-4).
# Dr.GRPO endorses a shared running MAD as the only batch-level scaling; the
# trainer implements it but no launcher passed the flag, so it was dead code.
# Default shared_mad for the SAPO canonical path; rollback:
# ASI3_SAPO_LOO_ADVANTAGE_SCALE=none.
export LOO_ADVANTAGE_SCALE="${ASI3_SAPO_LOO_ADVANTAGE_SCALE:-shared_mad}"
export FRONTIER_THRESHOLD="${ASI3_SAPO_FRONTIER_THRESHOLD:-0.10}"
export MASTERED_THRESHOLD="${ASI3_SAPO_MASTERED_THRESHOLD:-0.95}"
export MIX_TARGETED="${ASI3_SAPO_MIX_TARGETED:-0.5}"
export MIX_NEIGHBOR="${ASI3_SAPO_MIX_NEIGHBOR:-0.25}"
export MIX_REPLAY="${ASI3_SAPO_MIX_REPLAY:-0.25}"
export NEIGHBOR_WINDOW="${ASI3_SAPO_NEIGHBOR_WINDOW:-10}"
export CIRCUIT_BREAKER_WINDOW="${ASI3_SAPO_BREAKER_WINDOW:-10}"
export TRUST_REGION_ON_VIOLATION="scale_lr"
export TRUST_REGION_MAX_SEQ_KL="${ASI3_SAPO_MAX_SEQ_KL:-0.25}"
export TRUST_REGION_MAX_CLIP_FRACTION="${ASI3_SAPO_MAX_CLIP_FRACTION:-0.90}"
export CIRCUIT_BREAKER_CLIP_FRACTION_LIMIT="${ASI3_SAPO_BREAKER_CLIP_LIMIT:-0.90}"
export REWARD_MODE="${ASI3_SAPO_REWARD_MODE:-p_dominant}"
export REWARD_PASS_MASS="${ASI3_SAPO_REWARD_PASS_MASS:-0.50}"
export REWARD_SHAPED_MASS="${ASI3_SAPO_REWARD_SHAPED_MASS:-0.40}"
export REWARD_JUDGE_MASS="${ASI3_SAPO_REWARD_JUDGE_MASS:-0.10}"
# 2026-08-27 (r19, user binding): the reward judge is EXCLUSIVELY the Huanxin
# dp4 (deepseek-v4-flash) model — scores ALL candidates AT ONCE in a batch
# COMPARATIVE pass (same URL + API key as `claude -p huanxin -m dp4`) — and the
# raw reward scores are normalized across the group before the GRPO/SAPO
# advantage. Default OFF / 'none' / empty = inert (batch judge disabled).
export BATCH_COMPARATIVE_JUDGE="${ASI3_SAPO_BATCH_COMPARATIVE_JUDGE:-0}"
export REWARD_NORMALIZATION="${ASI3_SAPO_REWARD_NORMALIZATION:-none}"
export JUDGE_DP4_ENDPOINT="${ASI3_SAPO_JUDGE_DP4_ENDPOINT:-}"
export JUDGE_DP4_MODEL="${ASI3_SAPO_JUDGE_DP4_MODEL:-dp4}"
export JUDGE_DP4_MAX_TOKENS="${ASI3_SAPO_JUDGE_DP4_MAX_TOKENS:-4096}"
export JUDGE_BRIDGE_PORT="${ASI3_SAPO_JUDGE_BRIDGE_PORT:-56237}"
export REWARD_BREVITY_WEIGHT="${ASI3_SAPO_REWARD_BREVITY_WEIGHT:-0.05}"
# 2026-08-26 (r16 judge wave): model-judge path with the base 27B as judge
# on the SAME sharded model instance; verifier-watched (see asi2 launcher).
export MODEL_JUDGE_ENABLED="${ASI3_SAPO_MODEL_JUDGE_ENABLED:-0}"
export MODEL_JUDGE_PATH="${ASI3_SAPO_MODEL_JUDGE_PATH:-$MODEL_PATH}"
export CURRICULUM_EMA_DECAY="${ASI3_SAPO_CURRICULUM_EMA_DECAY:-0.9}"
export CURRICULUM_MIN_WEIGHT="${ASI3_SAPO_CURRICULUM_MIN_WEIGHT:-0.05}"
export MIN_REWARD_STD="${ASI3_SAPO_MIN_REWARD_STD:-0.05}"
export ADAPTIVE_TEMP_STEP="${ASI3_SAPO_ADAPTIVE_TEMP_STEP:-0.15}"
# 2026-08-25 (router-watch reconciliation): default must equal the trainer's
# TEMP_ESCALATION_CEILING (1.3) — the clamp enforces 1.3 at construction and
# use sites, so 2.0 was a display lie in launch_config.json; no behavior change.
export ADAPTIVE_TEMP_MAX="${ASI3_SAPO_ADAPTIVE_TEMP_MAX:-1.3}"

if [[ "$1" == "launch" ]]; then
  required_files=(
    "$MODEL_PATH/config.json"
    "$NAS_ROOT/training/grpo_trainer.py"
    "$NAS_ROOT/training/grpo_utils.py"
    "$NAS_ROOT/evals/runner/candidate_security.py"
    "$NAS_ROOT/evals/runner/single_candidate_eval.py"
    "$NAS_ROOT/$BENCHMARK_FILE"
    "$NAS_ROOT/scripts/fv_gspo_repair_sidecar.sh"
    "$NAS_ROOT/scripts/sapo_ensure_repair_sidecar.sh"
    "$NAS_ROOT/training/sidecar_liveness.py"
    "$CONFIG_FILE"
    "$NAS_ROOT/evals/benchmarks/quantum_generalization_holdout_v1.txt"
    "$NAS_ROOT/evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
    "$NAS_ROOT/evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt"
    "$NAS_ROOT/evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt"
    "$NAS_ROOT/evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
  )
  for required_file in "${required_files[@]}"; do
    if [[ ! -f "$required_file" ]]; then
      echo "[asi3] ERROR: required launch file missing: $required_file" >&2
      exit 1
    fi
  done

  # The generated manifest records the exact third-party imports used by its
  # verified reference programs. Refuse to spend a rollout on tasks whose
  # runtime is absent from ASI3 (the v5 run discarded its first group because
  # cirq/qiskit/stim were not installed).
  python3 - "$NAS_ROOT/$BENCHMARK_FILE" <<'PY'
import hashlib
import importlib.util
import json
import pathlib
import sys

manifest = pathlib.Path(sys.argv[1])
root = manifest.parents[2]
lines = manifest.read_text(encoding="utf-8").splitlines()
prefix = "# required_import_roots="
line = next((item for item in lines if item.startswith(prefix)), None)
if line is None:
    raise SystemExit(f"manifest lacks runtime import declaration: {manifest}")
required = [root for root in line[len(prefix):].split(",") if root]
missing = [root for root in required if importlib.util.find_spec(root) is None]
if missing:
    raise SystemExit(f"missing SAPO task runtimes: {','.join(missing)}")
verification = next(
    (item for item in lines if item.startswith("# reference_execution_verified=")), None
)
if verification is None or not verification.startswith("# reference_execution_verified=true "):
    raise SystemExit(f"manifest references were not execution-verified: {manifest}")
composition = next((item for item in lines if item.startswith("# targeted=")), None)
if composition is None:
    raise SystemExit(f"manifest lacks reward-integrity composition: {manifest}")
composition_fields = dict(
    field.split("=", 1) for field in composition.removeprefix("# ").split()
)
if int(composition_fields.get("semantic", "-1")) != 0:
    raise SystemExit(
        "semantic-stdout training is circuit-broken until scored values have "
        f"runtime execution provenance: {manifest}"
    )
source_line = next((item for item in lines if item.startswith("# source=")), None)
if source_line is None or " sha256=" not in source_line:
    raise SystemExit(f"manifest lacks source lineage: {manifest}")
source_rel, source_sha = source_line[len("# source="):].rsplit(" sha256=", 1)
source_path = root / source_rel
if not source_path.is_file():
    raise SystemExit(f"manifest source missing: {source_path}")
actual_source_sha = hashlib.sha256(source_path.read_bytes()).hexdigest()
if actual_source_sha != source_sha:
    raise SystemExit(f"manifest source hash mismatch: {source_path}")

contract_line = next((item for item in lines if item.startswith("# task_contract_sha256=")), None)
if contract_line is None:
    raise SystemExit(f"manifest lacks task contract hash: {manifest}")
expected_contract = contract_line.split("=", 1)[1]
wanted = [item.strip() for item in lines if item.strip() and not item.startswith("#")]
task_dirs = {}
for task_json in (root / "evals/tasks").glob("*/*/task.json"):
    meta = json.loads(task_json.read_text(encoding="utf-8"))
    task_dirs[str(meta.get("id", task_json.parent.name))] = task_json.parent
digest = hashlib.sha256()
for task_id in sorted(wanted):
    task_dir = task_dirs.get(task_id)
    if task_dir is None:
        raise SystemExit(f"manifest task missing: {task_id}")
    for name in ("task.json", "tests.py"):
        path = task_dir / name
        if not path.is_file():
            raise SystemExit(f"manifest task artifact missing: {path}")
        digest.update(task_id.encode())
        digest.update(b"\0")
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
if digest.hexdigest() != expected_contract:
    raise SystemExit(f"manifest task contract hash mismatch: {manifest}")
print("[asi3] runtime imports verified: " + ",".join(required))
PY

  promotion_benchmarks=(
    "$NAS_ROOT/evals/benchmarks/quantum_generalization_holdout_v1.txt"
    "$NAS_ROOT/evals/benchmarks/quantum_generalization_holdout_v2_hard.txt"
    "$NAS_ROOT/evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt"
    "$NAS_ROOT/evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt"
    "$NAS_ROOT/evals/benchmarks/sapo_promotion_holdout_v1_18.txt"
  )
  train_ids="$(mktemp)"
  trap 'rm -f "$train_ids" "${eval_ids:-}"' EXIT
  sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$NAS_ROOT/$BENCHMARK_FILE" | sort -u > "$train_ids"
  for promotion_benchmark in "${promotion_benchmarks[@]}"; do
    eval_ids="$(mktemp)"
    sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' "$promotion_benchmark" | sort -u > "$eval_ids"
    overlap="$(comm -12 "$train_ids" "$eval_ids")"
    rm -f "$eval_ids"
    eval_ids=""
    if [[ -n "$overlap" ]]; then
      echo "[asi3] ERROR: training/eval task contamination with $promotion_benchmark: $overlap" >&2
      exit 1
    fi
  done
  rm -f "$train_ids"
  trap - EXIT

  if [[ -n "$RESUME_FROM" ]]; then
    if [[ -z "$ADAPTER_INIT" ]]; then
      echo "[asi3] ERROR: ASI3_SAPO_RESUME_FROM requires ASI3_SAPO_ADAPTER_INIT" >&2
      exit 1
    fi
    if [[ ! -f "$RESUME_FROM" ]]; then
      echo "[asi3] ERROR: resume metrics missing: $RESUME_FROM" >&2
      exit 1
    fi
  fi
  # SOFT-RESUME (lane #20): the state file describes a paused policy, so the
  # paused checkpoint's weights are mandatory (trainer enforces this too).
  if [[ -n "$RESUME_STATE" ]]; then
    if [[ -z "$ADAPTER_INIT" ]]; then
      echo "[asi3] ERROR: ASI3_SAPO_RESUME_STATE requires ASI3_SAPO_ADAPTER_INIT" >&2
      exit 1
    fi
    if [[ ! -f "$RESUME_STATE" ]]; then
      echo "[asi3] ERROR: resume state missing: $RESUME_STATE" >&2
      exit 1
    fi
  fi
  if [[ -n "$ADAPTER_INIT" && ! -f "$ADAPTER_INIT/adapter_config.json" ]]; then
    echo "[asi3] ERROR: adapter init is incomplete: $ADAPTER_INIT" >&2
    exit 1
  fi
  # Adapter-init completeness gate (artifact-integrity lane 2026-09-01): the
  # trainer's own rule (peft_checkpoint_complete) requires adapter_config.json
  # PLUS weights (safetensors or bin). A config-only dir would otherwise pass
  # the launcher, boot the full trainer (15-30 min model load), and only then
  # crash inside PeftModel.from_pretrained — fail closed here instead.
  if [[ -n "$ADAPTER_INIT" && ! -f "$ADAPTER_INIT/adapter_model.safetensors" && ! -f "$ADAPTER_INIT/adapter_model.bin" ]]; then
    echo "[asi3] ERROR: adapter init is incomplete: $ADAPTER_INIT (missing adapter weights)" >&2
    exit 1
  fi
  if [[ -n "$ADAPTER_INIT" ]]; then
    python3 - "$ADAPTER_INIT/adapter_config.json" "$LORA_RANK" "$LORA_ALPHA" <<'PY'
import json
import sys

path, expected_rank, expected_alpha = sys.argv[1:]
config = json.load(open(path, encoding="utf-8"))
actual_rank = int(config.get("r", -1))
actual_alpha = int(config.get("lora_alpha", -1))
if (actual_rank, actual_alpha) != (int(expected_rank), int(expected_alpha)):
    raise SystemExit(
        f"warm adapter LoRA mismatch: got r/alpha={actual_rank}/{actual_alpha}, "
        f"expected {expected_rank}/{expected_alpha} ({path})"
    )
PY
  fi

  # Refuse to overwrite shared PID files or launch a second orphaned trainer.
  if [[ -f "$LOGDIR/grpo_27b_selfeval.pid" ]]; then
    existing_pid="$(cat "$LOGDIR/grpo_27b_selfeval.pid" 2>/dev/null || true)"
    existing_cmd=""
    if [[ -n "$existing_pid" ]]; then
      existing_cmd="$(ps -p "$existing_pid" -o args= 2>/dev/null || true)"
    fi
    if [[ "$existing_cmd" == *"training/grpo_trainer.py"* ]]; then
      echo "[asi3] ERROR: SAPO trainer already running pid=$existing_pid" >&2
      exit 1
    fi
  fi
  if existing_pids="$(pgrep -f 'training/[g]rpo_trainer.py' 2>/dev/null)" && [[ -n "$existing_pids" ]]; then
    echo "[asi3] ERROR: existing GRPO trainer process(es): $existing_pids" >&2
    exit 1
  fi
fi

echo "[asi3] launching via ${LAUNCHER} $1"
echo "[asi3] NUM_NPU=$NUM_NPU NPU_DEVICE_MAP=$NPU_DEVICE_MAP GROUP=$GROUP_SIZE CAP=$MAX_ADAPTIVE_GROUP CKPT=${CHECKPOINT_INTERVAL_SECONDS}s STEPS=$GRPO_STEPS"
echo "[asi3] VISIBLE_NPUS=$ASCEND_RT_VISIBLE_DEVICES MODEL=$MODEL_PATH OUT=$OUT"
echo "[asi3] LOSS=$LOSS_MODE LR=$LR KL=$KL_COEFF INNER_EPOCHS=$INNER_EPOCHS LORA=$LORA_RANK/$LORA_ALPHA TOKENS=$MAX_NEW_TOKENS/$MAX_ADAPTIVE_NEW_TOKENS LOGIT_CLIP=$LOGIT_CLIP BENCHMARK=$BENCHMARK_FILE REPAIR_ROUNDS=$SELF_REPAIR_ROUNDS"
echo "[asi3] GREEDY_ROLLOUT_FRACTION=${GREEDY_ROLLOUT_FRACTION} ENTROPY_FLOOR=${ENTROPY_FLOOR} ENTROPY_FLOOR_WEIGHT=${ENTROPY_FLOOR_WEIGHT} ENTROPY_TOKEN_CAP=${ENTROPY_TOKEN_CAP}"
echo "[asi3] R19_REWARD MIN_GROUP_SIZE=${MIN_GROUP_SIZE} BATCH_COMPARATIVE_JUDGE=${BATCH_COMPARATIVE_JUDGE} REWARD_NORMALIZATION=${REWARD_NORMALIZATION} REWARD_MODE=${REWARD_MODE}"
echo "[asi3] RESUME_FROM=${RESUME_FROM:-none} ADAPTER_INIT=${ADAPTER_INIT:-none} RESUME_STATE=${RESUME_STATE:-none}"
# ── Guardian alarm 8 (2026-08-26): boot guard for the repair sidecar ──
# The sidecar died SILENTLY at launch on runs 11/12 (SIGKILL from box-prep
# cleanup loops; untrappable, no error), starved the repair queue, and the
# all_fail_without_repair breaker stopped the runs hours later. Ensure it is
# alive BEFORE the trainer starts; relaunch idempotently if dead. The trainer
# additionally alarms per-step (step-record flag sidecar_alive + log line).
echo "[asi3] ensuring repair sidecar alive before trainer launch (boot guard)..."
bash "$NAS_ROOT/scripts/sapo_ensure_repair_sidecar.sh" "$OUT" "$LOGDIR" 2>&1 | sed 's/^/[asi3] /' || true
bash "$LAUNCHER" "$1"
