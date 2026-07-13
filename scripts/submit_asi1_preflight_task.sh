#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

REMOTE_ROOT="${ASI1_PREFLIGHT_REMOTE_ROOT:-/root/work/quantum-gpt}"
MODEL_PATH="${ASI1_PREFLIGHT_MODEL_PATH:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
BENCHMARK_FILE="${ASI1_PREFLIGHT_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
TASK_NAME="${ASI1_PREFLIGHT_TASK_NAME:-asi1-preflight}"
IMAGE_NAME="${ASI1_PREFLIGHT_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_PREFLIGHT_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_PREFLIGHT_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_PREFLIGHT_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_PREFLIGHT_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI1_PREFLIGHT_CPU_CORES:-4}"
MEMORY_GB="${ASI1_PREFLIGHT_MEMORY_GB:-16}"
WAIT_MS="${ASI1_PREFLIGHT_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_PREFLIGHT_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-preflight}"
TRAIN_DEV_URL="${ASI1_PREFLIGHT_URL:-}"
BOOTSTRAP_WHEELHOUSE="${ASI1_PREFLIGHT_BOOTSTRAP_WHEELHOUSE:-0}"
BOOTSTRAP_PIP_INDEX="${ASI1_PREFLIGHT_BOOTSTRAP_PIP_INDEX:-0}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_preflight_task.sh [--submit] [options]

Defaults to filling an ASI1 Huanxin task drawer only. It does not submit unless
--submit is explicitly provided.

Options:
  --submit                 Click the Huanxin submit button after filling the task
  --dry-run                Print the browser-automation command without running it
  --task-name <name>
  --remote-root <path>     Default: /root/work/quantum-gpt
  --model-path <path>      Default: /root/work/filestorage/Qwen3.6-35B-A3B-W8A8
  --benchmark-file <path>
  --artifact-stem <stem>   Files are written under browser-automation/
  --wait-ms <ms>
  --image-name <name>
  --resource-group <name>
  --resource-group-type <label>
  --instance-count <n>
  --accelerator-cards <n>
  --cpu-cores <n>
  --memory-gb <n>
  --bootstrap-wheelhouse  Install peft/accelerate from tools/wheels before probe
  --bootstrap-pip-index   Install pinned peft/accelerate from configured pip index before probe
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  python3 - <<'PY' "$REMOTE_ROOT" "$MODEL_PATH" "$BENCHMARK_FILE" "$BOOTSTRAP_WHEELHOUSE" "$BOOTSTRAP_PIP_INDEX"
import json
import shlex
import sys

remote_root, model_path, benchmark_file, bootstrap_wheelhouse, bootstrap_pip_index = sys.argv[1:6]
module_probe = (
    "import importlib.util; "
    "print('asi1_preflight_dependencies'); "
    "print('torch=' + str(bool(importlib.util.find_spec('torch')))); "
    "print('torch_npu=' + str(bool(importlib.util.find_spec('torch_npu')))); "
    "print('transformers=' + str(bool(importlib.util.find_spec('transformers')))); "
    "print('peft=' + str(bool(importlib.util.find_spec('peft')))); "
    "print('accelerate=' + str(bool(importlib.util.find_spec('accelerate'))))"
)
commands = [
    "set -euo pipefail",
    "echo __ASI1_PREFLIGHT_START__",
    "pwd",
    "whoami",
    "python3 --version",
    f"test -d {shlex.quote(model_path)}",
    "test -f training/agentic_grpo_trainer.py",
    f"test -f {shlex.quote(benchmark_file)}",
]
if bootstrap_wheelhouse == "1":
    commands.extend(
        [
            "test -d tools/wheels",
            "python3 -m pip install --no-input --no-index --find-links tools/wheels accelerate peft",
        ]
    )
if bootstrap_pip_index == "1":
    commands.append("python3 -m pip install --no-input accelerate==1.4.0 peft==0.14.0")
commands.extend(
    [
        "python3 -c " + shlex.quote(module_probe),
        "echo __ASI1_PREFLIGHT_DONE__",
    ]
)
remote_command = " && ".join(commands)
execution_command = "\n".join([commands[0], f"cd {shlex.quote(remote_root)}", *commands[1:]])
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": "asi1-preflight",
            "remote_command": remote_command,
            "execution_command": execution_command,
        },
        indent=2,
    )
)
PY
}

if [[ "${1:-}" == "--dry-run" && "${2:-}" == "__launch-spec" ]]; then
  render_launch_spec
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --submit)
      SUBMIT=1
      shift
      ;;
    --dry-run)
      PRINT_ONLY=1
      shift
      ;;
    --task-name)
      TASK_NAME="${2:-}"
      shift 2
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
      shift 2
      ;;
    --model-path)
      MODEL_PATH="${2:-}"
      shift 2
      ;;
    --benchmark-file)
      BENCHMARK_FILE="${2:-}"
      shift 2
      ;;
    --artifact-stem)
      ARTIFACT_STEM="${2:-}"
      shift 2
      ;;
    --wait-ms)
      WAIT_MS="${2:-}"
      shift 2
      ;;
    --image-name)
      IMAGE_NAME="${2:-}"
      shift 2
      ;;
    --resource-group)
      RESOURCE_GROUP="${2:-}"
      shift 2
      ;;
    --resource-group-type)
      RESOURCE_GROUP_TYPE="${2:-}"
      shift 2
      ;;
    --instance-count)
      INSTANCE_COUNT="${2:-}"
      shift 2
      ;;
    --accelerator-cards)
      ACCELERATOR_CARDS="${2:-}"
      shift 2
      ;;
    --cpu-cores)
      CPU_CORES="${2:-}"
      shift 2
      ;;
    --memory-gb)
      MEMORY_GB="${2:-}"
      shift 2
      ;;
    --bootstrap-wheelhouse)
      BOOTSTRAP_WHEELHOUSE=1
      shift
      ;;
    --bootstrap-pip-index)
      BOOTSTRAP_PIP_INDEX=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

export ASI1_PREFLIGHT_REMOTE_ROOT="$REMOTE_ROOT"
export ASI1_PREFLIGHT_MODEL_PATH="$MODEL_PATH"
export ASI1_PREFLIGHT_BENCHMARK_FILE="$BENCHMARK_FILE"
export ASI1_PREFLIGHT_BOOTSTRAP_WHEELHOUSE="$BOOTSTRAP_WHEELHOUSE"
export ASI1_PREFLIGHT_BOOTSTRAP_PIP_INDEX="$BOOTSTRAP_PIP_INDEX"

CMD=(
  node
  "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
  --url "$TRAIN_DEV_URL"
  --wait-ms "$WAIT_MS"
  --task-name "$TASK_NAME"
  --image-name "$IMAGE_NAME"
  --resource-group "$RESOURCE_GROUP"
  --resource-group-type "$RESOURCE_GROUP_TYPE"
  --instance-count "$INSTANCE_COUNT"
  --accelerator-cards "$ACCELERATOR_CARDS"
  --cpu-cores "$CPU_CORES"
  --memory-gb "$MEMORY_GB"
  --remote-root "$REMOTE_ROOT"
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_preflight_task.sh"
  --launcher-arg "__launch-spec"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
  --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
)

if [[ "$SUBMIT" == "1" ]]; then
  CMD+=(--submit)
fi

if [[ "$PRINT_ONLY" == "1" ]]; then
  shell_quote "${CMD[@]}"
  exit 0
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
