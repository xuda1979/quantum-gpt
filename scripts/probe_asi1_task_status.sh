#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

TASK_NAME="${ASI1_TASK_STATUS_NAME:-asi1-preflight-0523}"
TASK_ID="${ASI1_TASK_STATUS_ID:-}"
ARTIFACT_STEM="${ASI1_TASK_STATUS_ARTIFACT_STEM:-huanxin-task-status-asi1-preflight}"
WAIT_MS="${ASI1_TASK_STATUS_WAIT_MS:-12000}"
TRAIN_DEV_URL="${ASI1_TASK_STATUS_URL:-}"
OPEN_DETAIL=0
OPEN_POD_LOG=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/probe_asi1_task_status.sh [--task-name <name>] [--task-id <id>] [--url <train-dev-url>] [--open-detail] [--open-pod-log] [--dry-run]
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task-name)
      TASK_NAME="${2:-}"
      shift 2
      ;;
    --task-id)
      TASK_ID="${2:-}"
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
    --url)
      TRAIN_DEV_URL="${2:-}"
      shift 2
      ;;
    --open-detail)
      OPEN_DETAIL=1
      shift
      ;;
    --open-pod-log)
      OPEN_POD_LOG=1
      shift
      ;;
    --dry-run)
      PRINT_ONLY=1
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

CMD=(
  node
  "$ROOT_DIR/browser-automation/huanxin_task_status_probe.js"
  --url "$TRAIN_DEV_URL"
  --wait-ms "$WAIT_MS"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
)

if [[ -n "$TASK_ID" ]]; then
  CMD+=(--task-id "$TASK_ID")
fi
if [[ -n "$TASK_NAME" && -z "$TASK_ID" ]]; then
  CMD+=(--task-name "$TASK_NAME")
fi
if [[ "$OPEN_DETAIL" == "1" ]]; then
  CMD+=(--open-detail)
fi
if [[ "$OPEN_POD_LOG" == "1" ]]; then
  CMD+=(--open-pod-log)
fi

if [[ "$PRINT_ONLY" == "1" ]]; then
  shell_quote "${CMD[@]}"
  exit 0
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
