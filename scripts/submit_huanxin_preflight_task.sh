#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${HUANXIN_PREFLIGHT_ENV:-ASI1}"
REMOTE_ROOT="${HUANXIN_PREFLIGHT_REMOTE_ROOT:-/root/work/quantum-gpt}"
MODEL_PATH="${HUANXIN_PREFLIGHT_MODEL_PATH:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
BENCHMARK_FILE="${HUANXIN_PREFLIGHT_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
TASK_NAME="${HUANXIN_PREFLIGHT_TASK_NAME:-huanxin-preflight}"
IMAGE_NAME="${HUANXIN_PREFLIGHT_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${HUANXIN_PREFLIGHT_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${HUANXIN_PREFLIGHT_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${HUANXIN_PREFLIGHT_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${HUANXIN_PREFLIGHT_ACCELERATOR_CARDS:-1}"
CPU_CORES="${HUANXIN_PREFLIGHT_CPU_CORES:-4}"
MEMORY_GB="${HUANXIN_PREFLIGHT_MEMORY_GB:-16}"
WAIT_MS="${HUANXIN_PREFLIGHT_WAIT_MS:-12000}"
ARTIFACT_STEM="${HUANXIN_PREFLIGHT_ARTIFACT_STEM:-huanxin-submit-task-run-preflight}"
TRAIN_DEV_URL="${HUANXIN_PREFLIGHT_URL:-}"
BOOTSTRAP_WHEELHOUSE="${HUANXIN_PREFLIGHT_BOOTSTRAP_WHEELHOUSE:-0}"
BOOTSTRAP_PIP_INDEX="${HUANXIN_PREFLIGHT_BOOTSTRAP_PIP_INDEX:-0}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_huanxin_preflight_task.sh --env <name> [--submit] [options]

Defaults to filling a Huanxin task drawer only. It does not submit unless
--submit is explicitly provided.

Options:
  --env <name>             Target Huanxin environment name, for example yx-QITE
  --url <url>              Exact train-dev environment URL. If omitted, a common
                           train-dev route is built from --env.
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

default_train_dev_url() {
  "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$1" --field train_dev_url 2>/dev/null \
    || python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$1" --field train_dev_url
}

render_launch_spec() {
  python3 - <<'PY' "$ENV_NAME" "$REMOTE_ROOT" "$MODEL_PATH" "$BENCHMARK_FILE" "$BOOTSTRAP_WHEELHOUSE" "$BOOTSTRAP_PIP_INDEX"
import json
import re
import shlex
import sys

env_name, remote_root, model_path, benchmark_file, bootstrap_wheelhouse, bootstrap_pip_index = sys.argv[1:7]
marker_prefix = re.sub(r"[^A-Za-z0-9]+", "_", env_name).strip("_").upper() or "HUANXIN"
module_probe = (
    "import importlib.util; "
    f"print('{env_name}_preflight_dependencies'); "
    "print('torch=' + str(bool(importlib.util.find_spec('torch')))); "
    "print('torch_npu=' + str(bool(importlib.util.find_spec('torch_npu')))); "
    "print('transformers=' + str(bool(importlib.util.find_spec('transformers')))); "
    "print('peft=' + str(bool(importlib.util.find_spec('peft')))); "
    "print('accelerate=' + str(bool(importlib.util.find_spec('accelerate'))))"
)
commands = [
    "set -euo pipefail",
    f"echo __{marker_prefix}_PREFLIGHT_START__",
    f"mkdir -p {shlex.quote(remote_root)}",
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
        f"echo __{marker_prefix}_PREFLIGHT_DONE__",
    ]
)
execution_command = "\n".join([commands[0], *commands[1:2], f"cd {shlex.quote(remote_root)}", *commands[2:]])
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": f"{env_name}-preflight",
            "remote_command": " && ".join(commands),
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
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --url)
      TRAIN_DEV_URL="${2:-}"
      shift 2
      ;;
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

if [[ -z "$ENV_NAME" ]]; then
  echo "--env is required" >&2
  exit 2
fi

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url "$ENV_NAME")"
fi

export HUANXIN_PREFLIGHT_ENV="$ENV_NAME"
export HUANXIN_PREFLIGHT_REMOTE_ROOT="$REMOTE_ROOT"
export HUANXIN_PREFLIGHT_MODEL_PATH="$MODEL_PATH"
export HUANXIN_PREFLIGHT_BENCHMARK_FILE="$BENCHMARK_FILE"
export HUANXIN_PREFLIGHT_BOOTSTRAP_WHEELHOUSE="$BOOTSTRAP_WHEELHOUSE"
export HUANXIN_PREFLIGHT_BOOTSTRAP_PIP_INDEX="$BOOTSTRAP_PIP_INDEX"

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
  --launcher-script "$ROOT_DIR/scripts/submit_huanxin_preflight_task.sh"
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
