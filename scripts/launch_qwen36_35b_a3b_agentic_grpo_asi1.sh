#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_ROOT="${ASI1_REMOTE_ROOT:-${HUANXIN_TRAINING_REMOTE_ROOT:-/workspace/quantum-gpt}}"
MODEL_NAME="${ASI1_AGENTIC_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B}"
BENCHMARK_FILE="${ASI1_AGENTIC_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
DOMAIN_FILTER="${ASI1_AGENTIC_DOMAIN_FILTER:-${ASI1_AGENTIC_TASK_DOMAIN_FILTER:-}}"
VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
NPROC_PER_NODE="${NPROC_PER_NODE:-8}"
MASTER_PORT="${MASTER_PORT:-29533}"
GROUP_SIZE="${GROUP_SIZE:-8}"
GRPO_STEPS="${GRPO_STEPS:-64}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-2048}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-16384}"
MAX_TURNS="${MAX_TURNS:-24}"
MAX_TEST_RUNS="${MAX_TEST_RUNS:-2}"
TRAINING_MODE="${TRAINING_MODE:-lora}"
TEMPERATURE="${TEMPERATURE:-0.7}"
LR="${LR:-1e-5}"
KL_COEFF="${KL_COEFF:-0.03}"
LOG_STEPS="${LOG_STEPS:-1}"
CHECKPOINT_INTERVAL_SECONDS="${CHECKPOINT_INTERVAL_SECONDS:-3600}"
CHECKPOINT_EVERY_STEPS="${CHECKPOINT_EVERY_STEPS:-0}"
ONLINE_EVAL_BENCHMARK_FILE="${ONLINE_EVAL_BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v2_hard.txt}"
ONLINE_EVAL_EVERY_STEPS="${ONLINE_EVAL_EVERY_STEPS:-8}"
ONLINE_EVAL_MAX_TASKS="${ONLINE_EVAL_MAX_TASKS:-4}"
ONLINE_EVAL_TEMPERATURE="${ONLINE_EVAL_TEMPERATURE:-0.2}"
LORA_RANK="${LORA_RANK:-64}"
LORA_ALPHA="${LORA_ALPHA:-128}"
LORA_DROPOUT="${LORA_DROPOUT:-${ASI1_AGENTIC_TASK_LORA_DROPOUT:-0.0}}"
TARGET_MODULES="${TARGET_MODULES:-${ASI1_AGENTIC_TASK_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}}"
TRAIN_LAYER_NORM="${TRAIN_LAYER_NORM:-${ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM:-1}}"
MIN_TRAINABLE_PARAMETERS="${MIN_TRAINABLE_PARAMETERS:-${ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS:-200000000}}"
MAX_TRAINABLE_PARAMETERS="${MAX_TRAINABLE_PARAMETERS:-${ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS:-1000000000}}"
ADAPTER_INIT="${ASI1_AGENTIC_ADAPTER_INIT:-}"
TRAINING_MODE="${ASI1_AGENTIC_TASK_TRAINING_MODE:-lora}"
TRAINING_ENV="${HUANXIN_TRAINING_ENV:-ASI1}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_DIR="${ASI1_AGENTIC_OUTPUT_DIR:-outputs/qwen36-35b-a3b-agentic-grpo-asi1-fast-${TIMESTAMP}}"
LOG_PATH="${ASI1_AGENTIC_LOG_PATH:-/tmp/qwen36_35b_a3b_agentic_grpo_asi1_fast_${TIMESTAMP}.log}"
JOB_NAME="${ASI1_AGENTIC_JOB_NAME:-qwen36-35b-a3b-agentic-grpo-asi1-fast}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/launch_qwen36_35b_a3b_agentic_grpo_asi1.sh [options]

Fast ASI1 defaults:
  - 8 visible devices
  - 8 rollout group size
  - 64 GRPO steps
  - 2k max new tokens
  - 16k sequence length
  - 5m checkpoint cadence
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --model-name)
      MODEL_NAME="$2"
      shift 2
      ;;
    --benchmark-file)
      BENCHMARK_FILE="$2"
      shift 2
      ;;
    --domain-filter)
      DOMAIN_FILTER="$2"
      shift 2
      ;;
    --adapter-init)
      ADAPTER_INIT="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --log-path)
      LOG_PATH="$2"
      shift 2
      ;;
    --group-size)
      GROUP_SIZE="$2"
      shift 2
      ;;
    --grpo-steps)
      GRPO_STEPS="$2"
      shift 2
      ;;
    --max-turns)
      MAX_TURNS="$2"
      shift 2
      ;;
    --max-test-runs)
      MAX_TEST_RUNS="$2"
      shift 2
      ;;
    --max-new-tokens)
      MAX_NEW_TOKENS="$2"
      shift 2
      ;;
    --max-seq-length)
      MAX_SEQ_LENGTH="$2"
      shift 2
      ;;
    --checkpoint-interval-seconds)
      CHECKPOINT_INTERVAL_SECONDS="$2"
      shift 2
      ;;
    --checkpoint-every-steps)
      CHECKPOINT_EVERY_STEPS="$2"
      shift 2
      ;;
    --online-eval-benchmark-file)
      ONLINE_EVAL_BENCHMARK_FILE="$2"
      shift 2
      ;;
    --online-eval-every-steps)
      ONLINE_EVAL_EVERY_STEPS="$2"
      shift 2
      ;;
    --online-eval-max-tasks)
      ONLINE_EVAL_MAX_TASKS="$2"
      shift 2
      ;;
    --online-eval-temperature)
      ONLINE_EVAL_TEMPERATURE="$2"
      shift 2
      ;;
    --training-mode)
      TRAINING_MODE="$2"
      shift 2
      ;;
    --visible-devices)
      VISIBLE_DEVICES="$2"
      shift 2
      ;;
    --nproc-per-node)
      NPROC_PER_NODE="$2"
      shift 2
      ;;
    --hours)
      # Long-run helper: keep the job alive and checkpoint-driven rather than
      # encoding a fixed stop time into the launcher. The user can still tune
      # steps/turns explicitly.
      shift 2
      ;;
    --master-port)
      MASTER_PORT="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

PREFLIGHT_ARGS=(
  "$ROOT_DIR/scripts/preflight_qwen36_ascend_hf_training.py"
  --model-name "$MODEL_NAME"
  --device npu
  --json
)
python3 "${PREFLIGHT_ARGS[@]}" >&2

REMOTE_CMD="$(python3 - <<'PY' \
  "$MODEL_NAME" "$BENCHMARK_FILE" "$OUTPUT_DIR" "$VISIBLE_DEVICES" \
  "$DOMAIN_FILTER" \
  "$NPROC_PER_NODE" "$MASTER_PORT" "$GROUP_SIZE" "$GRPO_STEPS" \
  "$MAX_NEW_TOKENS" "$MAX_SEQ_LENGTH" "$MAX_TURNS" "$MAX_TEST_RUNS" \
  "$TEMPERATURE" "$LR" "$KL_COEFF" "$LOG_STEPS" \
  "$CHECKPOINT_INTERVAL_SECONDS" "$CHECKPOINT_EVERY_STEPS" "$ONLINE_EVAL_BENCHMARK_FILE" "$ONLINE_EVAL_EVERY_STEPS" \
  "$ONLINE_EVAL_MAX_TASKS" "$ONLINE_EVAL_TEMPERATURE" "$LORA_RANK" "$LORA_ALPHA" "$ADAPTER_INIT" "$REMOTE_ROOT" "$TRAINING_MODE" "$TRAIN_LAYER_NORM" "$MIN_TRAINABLE_PARAMETERS" "$MAX_TRAINABLE_PARAMETERS"
import shlex
import sys
import os

(
    model_name,
    benchmark_file,
    output_dir,
    visible_devices,
    domain_filter,
    nproc,
    master_port,
    group_size,
    grpo_steps,
    max_new_tokens,
    max_seq_length,
    max_turns,
    max_test_runs,
    temperature,
    lr,
    kl_coeff,
    log_steps,
    checkpoint_interval_seconds,
    checkpoint_every_steps,
    online_eval_benchmark_file,
    online_eval_every_steps,
    online_eval_max_tasks,
    online_eval_temperature,
    lora_rank,
    lora_alpha,
    adapter_init,
    remote_root,
    training_mode,
    train_layer_norm,
    min_trainable_parameters,
    max_trainable_parameters,
) = sys.argv[1:]

lora_dropout = os.environ.get("LORA_DROPOUT") or os.environ.get("ASI1_AGENTIC_TASK_LORA_DROPOUT") or "0.0"
target_modules = (os.environ.get("TARGET_MODULES") or os.environ.get("ASI1_AGENTIC_TASK_TARGET_MODULES") or "q_proj k_proj v_proj o_proj gate_proj up_proj down_proj").split()

probe_modules = ["torch", "torch_npu", "transformers"]
if training_mode == "lora":
    probe_modules.extend(["peft", "accelerate"])
probe_modules_python = " ".join(
    f"print('{module}=' + str(importlib.util.find_spec({module!r}) is not None));"
    for module in probe_modules
)

parts = [
    "set -euo pipefail",
    f"export ASCEND_RT_VISIBLE_DEVICES={shlex.quote(visible_devices)}",
    "export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
    "export TOKENIZERS_PARALLELISM=false",
    f"mkdir -p {shlex.quote(output_dir)}",
    f"test -d {shlex.quote(remote_root)}",
    "test -f training/agentic_grpo_trainer.py",
    f"test -d {shlex.quote(model_name)}",
    f"test -f {shlex.quote(benchmark_file)}",
    (
        "python3 -c "
        f"\"import importlib.util; print('__ASI1_DEPENDENCY_PROBE__'); {probe_modules_python} "
        "print('__ASI1_DEPENDENCY_PROBE_DONE__', flush=True)\""
    ),
    "echo __ASI1_GRPO_BEFORE_TORCHRUN__",
]

command = [
    "torchrun",
    f"--nproc_per_node={shlex.quote(nproc)}",
    f"--master_port={shlex.quote(master_port)}",
    "training/agentic_grpo_trainer.py",
    "--model-name",
    shlex.quote(model_name),
    "--benchmark-file",
    shlex.quote(benchmark_file),
]
if domain_filter:
    command.extend(["--domain-filter", shlex.quote(domain_filter)])
command.extend([
    "--output-dir",
    shlex.quote(output_dir),
    "--device",
    "npu",
    "--group-size",
    shlex.quote(group_size),
    "--grpo-steps",
    shlex.quote(grpo_steps),
    "--max-new-tokens",
    shlex.quote(max_new_tokens),
    "--max-seq-length",
    shlex.quote(max_seq_length),
    "--max-turns",
    shlex.quote(max_turns),
    "--max-test-runs",
    shlex.quote(max_test_runs),
    "--temperature",
    shlex.quote(temperature),
    "--lr",
    shlex.quote(lr),
    "--kl-coeff",
    shlex.quote(kl_coeff),
    "--log-steps",
    shlex.quote(log_steps),
    "--checkpoint-interval-seconds",
    shlex.quote(checkpoint_interval_seconds),
    "--checkpoint-every-steps",
    shlex.quote(checkpoint_every_steps),
    "--online-eval-benchmark-file",
    shlex.quote(online_eval_benchmark_file),
    "--online-eval-every-steps",
    shlex.quote(online_eval_every_steps),
    "--online-eval-max-tasks",
    shlex.quote(online_eval_max_tasks),
    "--online-eval-temperature",
    shlex.quote(online_eval_temperature),
    "--lora-rank",
    shlex.quote(lora_rank),
    "--lora-alpha",
    shlex.quote(lora_alpha),
    "--lora-dropout",
    shlex.quote(lora_dropout),
    "--training-mode",
    shlex.quote(training_mode),
    "--reward-pass-weight",
    "0.6",
    "--reward-syntax-weight",
    "0.1",
    "--reward-interface-weight",
    "0.15",
    "--reward-verifier-weight",
    "0.15",
    "--reward-import-hygiene-weight",
    "0.05",
    "--ratio-clip-log-delta",
    "8.0",
    "--logit-clip",
    "50.0",
    "--min-reward-std",
    "0.02",
    "--curriculum-ema-decay",
    "0.8",
    "--curriculum-min-weight",
    "0.1",
    "--curriculum-uncertainty-bonus",
    "0.25",
    "--quantum-priority",
    "1.2",
    "--target-modules",
    *[shlex.quote(module) for module in target_modules],
    "--research-methods",
    "clause_aware_verifier_reward",
    "ast_anchor_interface_grounding",
    "self_consistency_verifier_routing",
    "uncertainty_triggered_repair_replay",
    "behavior_anchor_coverage_reward",
])
if train_layer_norm == "1":
    command.append("--train-layernorm")
if min_trainable_parameters:
    command.extend(["--min-trainable-parameters", shlex.quote(min_trainable_parameters)])
if max_trainable_parameters:
    command.extend(["--max-trainable-parameters", shlex.quote(max_trainable_parameters)])
if adapter_init:
    command.extend(["--adapter-init", shlex.quote(adapter_init)])

parts.append(" ".join(command))
parts.extend(
    [
        "echo __ASI1_GRPO_AFTER_TORCHRUN__",
        f"test -s {shlex.quote(output_dir)}/grpo_step_metrics.jsonl",
        f"test -d {shlex.quote(output_dir)}/final_adapter",
        "echo __ASI1_GRPO_METRICS_AND_ARTIFACTS_OK__",
    ]
)
print(" && ".join(parts))
PY
)"

cd "$ROOT_DIR"

if [[ "$DRY_RUN" == "1" ]]; then
  python3 - <<'PY' "$REMOTE_ROOT" "$OUTPUT_DIR" "$LOG_PATH" "$JOB_NAME" "$REMOTE_CMD" "$TRAINING_ENV"
import json
import sys

remote_root, output_dir, log_path, job_name, remote_cmd, env_name = sys.argv[1:7]
print(
    json.dumps(
        {
            "environment": env_name,
            "remote_root": remote_root,
            "output_dir": output_dir,
            "log_path": log_path,
            "job_name": job_name,
            "remote_command": remote_cmd,
        },
        indent=2,
    )
)
PY
  exit 0
fi

if [[ -z "$TRAINING_ENV" ]]; then
  echo "Missing HUANXIN_TRAINING_ENV (expected ASI1 for this lane)." >&2
  exit 2
fi

exec bash "$ROOT_DIR/scripts/huanxin_training_job.sh" --env "$TRAINING_ENV" start "$JOB_NAME" "$LOG_PATH" "cd '$REMOTE_ROOT' && $REMOTE_CMD"
