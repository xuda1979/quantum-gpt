#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

TASK_NAME="${ASI1_SHELL_TASK_NAME:-asi1-shell-task}"
IMAGE_NAME="${ASI1_SHELL_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_SHELL_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_SHELL_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_SHELL_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_SHELL_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI1_SHELL_CPU_CORES:-4}"
MEMORY_GB="${ASI1_SHELL_MEMORY_GB:-16}"
WAIT_MS="${ASI1_SHELL_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_SHELL_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-shell-task}"
TRAIN_DEV_URL="${ASI1_SHELL_URL:-}"
REMOTE_ROOT="${ASI1_SHELL_REMOTE_ROOT:-/tmp}"
REMOTE_COMMAND_FILE="${ASI1_SHELL_REMOTE_COMMAND_FILE:-}"
REMOTE_COMMAND="${ASI1_SHELL_REMOTE_COMMAND:-}"
AUTO_CODECONTENTS_OVERRIDE="${ASI1_SHELL_AUTO_CODECONTENTS_OVERRIDE:-1}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_shell_task.sh [--submit] [--dry-run]

Runs a small ASI1 training-task shell payload. Provide either
ASI1_SHELL_REMOTE_COMMAND_FILE or ASI1_SHELL_REMOTE_COMMAND.
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  python3 - <<'PY' "$REMOTE_ROOT" "$REMOTE_COMMAND_FILE" "$REMOTE_COMMAND"
import json
import pathlib
import sys

remote_root, command_file, command = sys.argv[1:4]
if command_file:
    command = pathlib.Path(command_file).read_text(encoding="utf-8").replace("\r\n", "\n")
if not command.strip():
    raise SystemExit("ASI1_SHELL_REMOTE_COMMAND_FILE or ASI1_SHELL_REMOTE_COMMAND is required")
print(json.dumps({
    "remote_root": remote_root,
    "output_dir": "",
    "log_path": "",
    "job_name": "asi1-shell-task",
    "remote_command": command,
    "execution_command": command,
}, indent=2))
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
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

CMD=(
  node "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
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
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_shell_task.sh"
  --launcher-arg "__launch-spec"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
  --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
)

if [[ "$AUTO_CODECONTENTS_OVERRIDE" != "1" ]]; then
  CMD+=(--no-auto-codecontents-override)
fi

if [[ "$SUBMIT" == "1" ]]; then
  CMD+=(--submit)
fi
if [[ "$PRINT_ONLY" == "1" ]]; then
  shell_quote "${CMD[@]}"
  exit 0
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
