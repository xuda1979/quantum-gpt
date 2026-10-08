#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${HUANXIN_TRAINING_ENV:-}"
REMOTE_ROOT="${HUANXIN_TRAINING_REMOTE_ROOT:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

if [[ -z "$ENV_NAME" || $# -lt 1 ]]; then
  echo 'Usage: scripts/show_huanxin_agentic_grpo_status.sh --env <env-name> <remote-output-dir>' >&2
  exit 2
fi

if [[ -z "$REMOTE_ROOT" ]]; then
  case "$ENV_NAME" in
    ASI1) REMOTE_ROOT="/workspace/quantum-gpt" ;;
    *) REMOTE_ROOT="/root/work/quantum-gpt" ;;
  esac
fi

REMOTE_OUTPUT_DIR="$1"
if [[ "$REMOTE_OUTPUT_DIR" == /* ]]; then
  REMOTE_OUTPUT_REL="${REMOTE_OUTPUT_DIR#${REMOTE_ROOT}/}"
else
  REMOTE_OUTPUT_REL="$REMOTE_OUTPUT_DIR"
fi

exec bash "$ROOT_DIR/scripts/huanxin_env_shell.sh" --env "$ENV_NAME" \
  "cd '$REMOTE_ROOT' && python3 scripts/show_agentic_grpo_status.py '$REMOTE_OUTPUT_REL'"
