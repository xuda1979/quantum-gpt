#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

REMOTE_ROOT="${ASI1_WHEELHOUSE_REMOTE_ROOT:-/workspace/quantum-gpt}"
WHEEL_ROOT="${ASI1_WHEELHOUSE_WHEEL_ROOT:-/tmp/asi1-wheelhouse}"
TASK_NAME="${ASI1_WHEELHOUSE_TASK_NAME:-asi1-wheel-sync}"
IMAGE_NAME="${ASI1_WHEELHOUSE_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_WHEELHOUSE_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_WHEELHOUSE_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_WHEELHOUSE_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_WHEELHOUSE_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI1_WHEELHOUSE_CPU_CORES:-4}"
MEMORY_GB="${ASI1_WHEELHOUSE_MEMORY_GB:-16}"
WAIT_MS="${ASI1_WHEELHOUSE_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_WHEELHOUSE_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-wheelhouse-sync}"
TRAIN_DEV_URL="${ASI1_WHEELHOUSE_URL:-}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_wheelhouse_sync_task.sh [--submit] [options]

Submits or fills a tiny ASI1 Huanxin task that refreshes tools/wheels from the
INER S3 relay into a temp wheelhouse and validates the wheel zip files.
It does not submit unless --submit is explicitly provided.

Options:
  --submit                 Click the Huanxin submit button after filling the task
  --dry-run                Print the browser-automation command without running it
  --task-name <name>
  --remote-root <path>     Default: /workspace/quantum-gpt
  --wheel-root <path>      Default: /tmp/asi1-wheelhouse
  --artifact-stem <stem>   Files are written under browser-automation/
  --wait-ms <ms>
  --image-name <name>
  --resource-group <name>
  --resource-group-type <label>
  --instance-count <n>
  --accelerator-cards <n>
  --cpu-cores <n>
  --memory-gb <n>
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  python3 - <<'PY' "$REMOTE_ROOT" "$WHEEL_ROOT"
import json
import shlex
import sys

remote_root = sys.argv[1]
wheel_root = sys.argv[2]
commands = [
    "set -euo pipefail",
    "echo __ASI1_WHEELHOUSE_SYNC_START__",
    "pwd",
    "whoami",
    "python3 --version",
    "test -f scripts/iner_s3_env.sh",
    "if command -v rclone; then echo using_system_rclone; else test -f tools/preseed/rclone-linux-arm64; mkdir -p /tmp/asi1-rclone-bin; cp tools/preseed/rclone-linux-arm64 /tmp/asi1-rclone-bin/rclone; chmod +x /tmp/asi1-rclone-bin/rclone; export PATH=/tmp/asi1-rclone-bin:$PATH; fi",
    "command -v rclone",
    "source scripts/iner_s3_env.sh",
    "cfg=/tmp/iner-rclone.conf",
    "iner_write_rclone_config \"$cfg\"",
    f"mkdir -p {shlex.quote(wheel_root)}/tools/wheels",
    f"rclone sync \"$INER_S3_ROOT/tools/wheels\" {shlex.quote(wheel_root + '/tools/wheels')} --config \"$cfg\" --s3-no-check-bucket --checksum --progress",
    f"ls -l {shlex.quote(wheel_root)}/tools/wheels",
    f"python3 scripts/validate_wheelhouse.py --wheel-root {shlex.quote(wheel_root + '/tools/wheels')}",
    f"python3 -m pip install --no-cache-dir --no-input --no-index --find-links {shlex.quote(wheel_root + '/tools/wheels')} accelerate==1.4.0 peft==0.14.0",
    "python3 -c \"import accelerate; import peft; print('accelerate=' + accelerate.__version__); print('peft=' + peft.__version__)\"",
    "echo __ASI1_WHEELHOUSE_SYNC_DONE__",
]
execution_command = "; ".join([commands[0], f"cd {shlex.quote(remote_root)}", *commands[1:]])
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": "asi1-wheelhouse-sync",
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
    --wheel-root)
      WHEEL_ROOT="${2:-}"
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

export ASI1_WHEELHOUSE_REMOTE_ROOT="$REMOTE_ROOT"
export ASI1_WHEELHOUSE_WHEEL_ROOT="$WHEEL_ROOT"

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
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_wheelhouse_sync_task.sh"
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
