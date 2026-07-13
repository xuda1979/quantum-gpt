#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_ROOT="${AI3_REMOTE_ROOT:-/root/work/quantum-gpt}"
MODEL_NAME="${AI3_AGENTIC_MODEL_NAME:-models/Qwen3.6-35B-A3B}"
BENCHMARK_FILE="${AI3_AGENTIC_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3}"
NPROC_PER_NODE="${NPROC_PER_NODE:-4}"
MASTER_PORT="${MASTER_PORT:-29533}"
GROUP_SIZE="${GROUP_SIZE:-4}"
GRPO_STEPS="${GRPO_STEPS:-64}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-384}"
MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-4096}"
MAX_TURNS="${MAX_TURNS:-8}"
MAX_TEST_RUNS="${MAX_TEST_RUNS:-3}"
TEMPERATURE="${TEMPERATURE:-0.8}"
LR="${LR:-5e-6}"
KL_COEFF="${KL_COEFF:-0.05}"
LOG_STEPS="${LOG_STEPS:-1}"
CHECKPOINT_INTERVAL_SECONDS="${CHECKPOINT_INTERVAL_SECONDS:-3600}"
ONLINE_EVAL_BENCHMARK_FILE="${ONLINE_EVAL_BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v1.txt}"
ONLINE_EVAL_EVERY_STEPS="${ONLINE_EVAL_EVERY_STEPS:-8}"
ONLINE_EVAL_MAX_TASKS="${ONLINE_EVAL_MAX_TASKS:-4}"
ONLINE_EVAL_TEMPERATURE="${ONLINE_EVAL_TEMPERATURE:-0.2}"
LORA_RANK="${LORA_RANK:-8}"
LORA_ALPHA="${LORA_ALPHA:-16}"
TRAINING_MODE="${TRAINING_MODE:-lora}"
ADAPTER_INIT="${ADAPTER_INIT:-}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_DIR="${AI3_AGENTIC_OUTPUT_DIR:-outputs/qwen36-35b-a3b-agentic-grpo-v1-${TIMESTAMP}}"
LOG_PATH="${AI3_AGENTIC_LOG_PATH:-/tmp/qwen36_35b_a3b_agentic_grpo_ai3_${TIMESTAMP}.log}"
JOB_NAME="${AI3_AGENTIC_JOB_NAME:-qwen36-35b-a3b-agentic-grpo-ai3}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/launch_qwen36_35b_a3b_agentic_grpo_ai3.sh [options]

Options:
  --dry-run
  --model-name <remote model dir or HF id>
  --benchmark-file <remote benchmark file>
  --adapter-init <remote adapter dir>
  --output-dir <remote output dir>
  --log-path <remote log path>
  --group-size <n>
  --grpo-steps <n>
  --max-turns <n>
  --max-test-runs <n>
  --max-new-tokens <n>
  --max-seq-length <n>
  --checkpoint-interval-seconds <n>
  --online-eval-benchmark-file <path>
  --online-eval-every-steps <n>
  --online-eval-max-tasks <n>
  --online-eval-temperature <f>
  --visible-devices <ids>
  --nproc-per-node <n>
  --master-port <n>
  --training-mode <lora|native>
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
    --visible-devices)
      VISIBLE_DEVICES="$2"
      shift 2
      ;;
    --nproc-per-node)
      NPROC_PER_NODE="$2"
      shift 2
      ;;
    --master-port)
      MASTER_PORT="$2"
      shift 2
      ;;
    --training-mode)
      TRAINING_MODE="$2"
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
  "$NPROC_PER_NODE" "$MASTER_PORT" "$GROUP_SIZE" "$GRPO_STEPS" \
  "$MAX_NEW_TOKENS" "$MAX_SEQ_LENGTH" "$MAX_TURNS" "$MAX_TEST_RUNS" \
  "$TEMPERATURE" "$LR" "$KL_COEFF" "$LOG_STEPS" \
  "$CHECKPOINT_INTERVAL_SECONDS" "$ONLINE_EVAL_BENCHMARK_FILE" "$ONLINE_EVAL_EVERY_STEPS" \
  "$ONLINE_EVAL_MAX_TASKS" "$ONLINE_EVAL_TEMPERATURE" "$LORA_RANK" "$LORA_ALPHA" "$TRAINING_MODE" "$ADAPTER_INIT"
import base64
import pathlib
import shlex
import sys

(
    model_name,
    benchmark_file,
    output_dir,
    visible_devices,
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
    online_eval_benchmark_file,
    online_eval_every_steps,
    online_eval_max_tasks,
    online_eval_temperature,
    lora_rank,
    lora_alpha,
    training_mode,
    adapter_init,
) = sys.argv[1:]

parts = [
    "set -euo pipefail",
    "echo __ASI1_GRPO_START__",
    f"export ASCEND_RT_VISIBLE_DEVICES={shlex.quote(visible_devices)}",
    f"export TRAINING_MODE={shlex.quote(training_mode)}",
    "export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
    "export TOKENIZERS_PARALLELISM=false",
]
if training_mode != "native":
    parts.append("python3 -c 'import peft;print(\"peft_ok\")'")

script_env = {
    "ASI1_AGENTIC_TASK_MODEL_NAME": model_name,
    "ASI1_AGENTIC_TASK_BENCHMARK_FILE": benchmark_file,
    "ASI1_AGENTIC_TASK_OUTPUT_DIR": output_dir,
    "ASI1_AGENTIC_TASK_LOG_PATH": "/tmp/asi1_agentic_grpo_task.log",
    "ASI1_AGENTIC_TASK_VISIBLE_DEVICES": visible_devices,
    "ASI1_AGENTIC_TASK_NPROC_PER_NODE": nproc,
    "ASI1_AGENTIC_TASK_GROUP_SIZE": group_size,
    "ASI1_AGENTIC_TASK_GRPO_STEPS": grpo_steps,
    "ASI1_AGENTIC_TASK_MAX_NEW_TOKENS": max_new_tokens,
    "ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH": max_seq_length,
    "ASI1_AGENTIC_TASK_MAX_TURNS": max_turns,
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS": online_eval_every_steps,
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS": online_eval_max_tasks,
    "ASI1_AGENTIC_TASK_TRAINING_MODE": training_mode,
}
parts.extend(f"export {key}={shlex.quote(value)}" for key, value in script_env.items())

runner_path = pathlib.Path("scripts/run_asi1_agentic_grpo_from_env.sh")
if runner_path.exists():
    encoded_runner = base64.b64encode(runner_path.read_bytes()).decode("ascii")
    parts.append("python3 -c " + shlex.quote(
        "import base64;import pathlib;"
        f"pathlib.Path('/tmp/asi1_grpo_runner.sh').write_bytes(base64.b64decode({encoded_runner!r}));"
        "pathlib.Path('/tmp/asi1_grpo_runner.sh').chmod(0o700)"
    ))

command = [
    "torchrun",
    f"--nproc_per_node={shlex.quote(nproc)}",
    f"--master_port={shlex.quote(master_port)}",
    "training/agentic_grpo_trainer.py",
    "--model-name",
    shlex.quote(model_name),
    "--benchmark-file",
    shlex.quote(benchmark_file),
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
    "--target-module-regex",
    shlex.quote(r".*self_attn\.(q_proj|k_proj|v_proj|o_proj)$"),
    "--research-methods",
    "clause_aware_verifier_reward",
    "ast_anchor_interface_grounding",
    "self_consistency_verifier_routing",
    "uncertainty_triggered_repair_replay",
    "behavior_anchor_coverage_reward",
]
if adapter_init:
    command.extend(["--adapter-init", shlex.quote(adapter_init)])

parts.append("echo __ASI1_GRPO_RUNNER__")
parts.append("bash /tmp/asi1_grpo_runner.sh")
print("\n".join(parts))
PY
)"

cd "$ROOT_DIR"

if [[ "$DRY_RUN" == "1" ]]; then
  python3 - <<'PY' "$REMOTE_ROOT" "$OUTPUT_DIR" "$LOG_PATH" "$JOB_NAME" "$REMOTE_CMD"
import json
import sys

remote_root, output_dir, log_path, job_name, remote_cmd = sys.argv[1:6]
print(
    json.dumps(
        {
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

JOB_SCRIPT="${AI3_JOB_SCRIPT:-scripts/ai3_job.sh}"
exec bash "$JOB_SCRIPT" start "$JOB_NAME" "$LOG_PATH" "cd '$REMOTE_ROOT' && $REMOTE_CMD"
