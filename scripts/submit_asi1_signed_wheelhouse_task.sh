#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

REMOTE_ROOT="${ASI1_SIGNED_WHEELHOUSE_REMOTE_ROOT:-/workspace/quantum-gpt}"
WHEEL_ROOT="${ASI1_SIGNED_WHEELHOUSE_WHEEL_ROOT:-/tmp/asi1-wheelhouse}"
TASK_NAME="${ASI1_SIGNED_WHEELHOUSE_TASK_NAME:-asi1-wheel-signed}"
IMAGE_NAME="${ASI1_SIGNED_WHEELHOUSE_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_SIGNED_WHEELHOUSE_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_SIGNED_WHEELHOUSE_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_SIGNED_WHEELHOUSE_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_SIGNED_WHEELHOUSE_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI1_SIGNED_WHEELHOUSE_CPU_CORES:-4}"
MEMORY_GB="${ASI1_SIGNED_WHEELHOUSE_MEMORY_GB:-16}"
WAIT_MS="${ASI1_SIGNED_WHEELHOUSE_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_SIGNED_WHEELHOUSE_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-signed-wheelhouse}"
TRAIN_DEV_URL="${ASI1_SIGNED_WHEELHOUSE_URL:-}"
ACCELERATE_URL="${ASI1_ACCELERATE_WHEEL_URL:-}"
PEFT_URL="${ASI1_PEFT_WHEEL_URL:-}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  ASI1_ACCELERATE_WHEEL_URL=<signed-url> ASI1_PEFT_WHEEL_URL=<signed-url> \
    scripts/submit_asi1_signed_wheelhouse_task.sh [--submit] [options]

Fills or submits an ASI1 Huanxin task that downloads signed wheel URLs into
a temp wheelhouse, validates them as zip files, and installs peft/accelerate offline.
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  python3 - <<'PY' "$REMOTE_ROOT" "$WHEEL_ROOT" "$ACCELERATE_URL" "$PEFT_URL"
import json
import shlex
import sys

remote_root, wheel_root, accelerate_url, peft_url = sys.argv[1:5]
if not accelerate_url or not peft_url:
    raise SystemExit("ASI1_ACCELERATE_WHEEL_URL and ASI1_PEFT_WHEEL_URL are required")
wheel_dir = f"{wheel_root}/tools/wheels"
commands = [
    "set -euo pipefail",
    "echo __ASI1_SIGNED_WHEELHOUSE_START__",
    "pwd",
    "whoami",
    "python3 --version",
    f"mkdir -p {shlex.quote(wheel_dir)}",
    f"curl -fL --retry 3 {shlex.quote(accelerate_url)} -o {shlex.quote(wheel_dir + '/accelerate-1.4.0-py3-none-any.whl')}",
    f"curl -fL --retry 3 {shlex.quote(peft_url)} -o {shlex.quote(wheel_dir + '/peft-0.14.0-py3-none-any.whl')}",
    f"python3 -m zipfile -t {shlex.quote(wheel_dir + '/accelerate-1.4.0-py3-none-any.whl')} >/dev/null",
    f"python3 -m zipfile -t {shlex.quote(wheel_dir + '/peft-0.14.0-py3-none-any.whl')} >/dev/null",
    f"ls -l {shlex.quote(wheel_dir)}",
    f"python3 -m pip install --no-cache-dir --no-input --no-index --find-links {shlex.quote(wheel_dir)} accelerate==1.4.0 peft==0.14.0",
    "python3 -c \"import accelerate; import peft; print('accelerate=' + accelerate.__version__); print('peft=' + peft.__version__)\"",
    "echo __ASI1_SIGNED_WHEELHOUSE_DONE__",
]
execution_command = "; ".join([commands[0], f"cd {shlex.quote(remote_root)}", *commands[1:]])
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": "asi1-signed-wheelhouse",
            "remote_command": execution_command,
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
    --submit) SUBMIT=1; shift ;;
    --dry-run) PRINT_ONLY=1; shift ;;
    --task-name) TASK_NAME="${2:-}"; shift 2 ;;
    --remote-root) REMOTE_ROOT="${2:-}"; shift 2 ;;
    --artifact-stem) ARTIFACT_STEM="${2:-}"; shift 2 ;;
    --wait-ms) WAIT_MS="${2:-}"; shift 2 ;;
    --image-name) IMAGE_NAME="${2:-}"; shift 2 ;;
    --resource-group) RESOURCE_GROUP="${2:-}"; shift 2 ;;
    --resource-group-type) RESOURCE_GROUP_TYPE="${2:-}"; shift 2 ;;
    --instance-count) INSTANCE_COUNT="${2:-}"; shift 2 ;;
    --accelerator-cards) ACCELERATOR_CARDS="${2:-}"; shift 2 ;;
    --cpu-cores) CPU_CORES="${2:-}"; shift 2 ;;
    --memory-gb) MEMORY_GB="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

export ASI1_SIGNED_WHEELHOUSE_REMOTE_ROOT="$REMOTE_ROOT"
export ASI1_SIGNED_WHEELHOUSE_WHEEL_ROOT="$WHEEL_ROOT"
export ASI1_ACCELERATE_WHEEL_URL="$ACCELERATE_URL"
export ASI1_PEFT_WHEEL_URL="$PEFT_URL"

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
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_signed_wheelhouse_task.sh"
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
