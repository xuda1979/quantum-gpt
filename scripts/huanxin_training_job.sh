#!/usr/bin/env bash
set -euo pipefail

# Generic long-running Huanxin job manager. The environment name is always an
# input, and shell control is routed through huanxin_env_shell.sh.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${HUANXIN_TRAINING_ENV:-}"
REMOTE_ROOT="${HUANXIN_TRAINING_REMOTE_ROOT:-}"
META_DIR="${HUANXIN_TRAINING_JOB_META_DIR:-$ROOT_DIR/.huanxin_training_jobs}"

if [[ "${1:-}" == "--env" ]]; then
  ENV_NAME="${2:-}"
  shift 2
fi

if [[ -z "$ENV_NAME" ]]; then
  echo "Usage: scripts/huanxin_training_job.sh --env <env-name> <ai2_job subcommand...>" >&2
  exit 2
fi

if [[ -z "$REMOTE_ROOT" ]]; then
  case "$ENV_NAME" in
    ASI1) REMOTE_ROOT="/workspace/quantum-gpt" ;;
    *) REMOTE_ROOT="/root/work/quantum-gpt" ;;
  esac
fi

HUANXIN_TRAINING_ENV="$ENV_NAME" \
AI2_JOB_REMOTE_ROOT="$REMOTE_ROOT" \
AI2_JOB_SHELL_WRAPPER="$ROOT_DIR/scripts/huanxin_env_shell.sh" \
AI2_JOB_META_DIR="$META_DIR" \
  bash "$ROOT_DIR/scripts/ai2_job.sh" "$@"
