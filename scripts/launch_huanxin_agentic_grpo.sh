#!/usr/bin/env bash
set -euo pipefail

# Generic launcher for Huanxin agentic GRPO training. The environment name is
# intentionally an argument, not encoded in the filename or inferred from notes.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_NAME="${HUANXIN_TRAINING_ENV:-}"
REMOTE_ROOT="${HUANXIN_TRAINING_REMOTE_ROOT:-/root/work/quantum-gpt}"

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
    --help|-h)
      cat <<'EOF'
Usage:
  scripts/launch_huanxin_agentic_grpo.sh --env <env-name> [launcher options]

Required:
  --env <env-name>  Huanxin training environment explicitly provided by user

All remaining options are passed to the agentic GRPO command renderer.
EOF
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ -z "$ENV_NAME" ]]; then
  echo "Missing --env. Ask the user for the Huanxin training environment before launching." >&2
  exit 2
fi

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SAFE_ENV="$(printf '%s' "$ENV_NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9._-' '-')"

export HUANXIN_TRAINING_ENV="$ENV_NAME"
export HUANXIN_TRAINING_REMOTE_ROOT="$REMOTE_ROOT"
export AI3_REMOTE_ROOT="$REMOTE_ROOT"
export AI3_JOB_REMOTE_ROOT="$REMOTE_ROOT"
export AI3_JOB_SCRIPT="$ROOT_DIR/scripts/huanxin_training_job.sh"
export AI3_JOB_META_DIR="${HUANXIN_TRAINING_JOB_META_DIR:-$ROOT_DIR/.huanxin_training_jobs}"
export AI3_AGENTIC_JOB_NAME="${HUANXIN_AGENTIC_JOB_NAME:-qwen36-35b-a3b-agentic-grpo-${SAFE_ENV}}"
export AI3_AGENTIC_LOG_PATH="${HUANXIN_AGENTIC_LOG_PATH:-/tmp/qwen36_35b_a3b_agentic_grpo_${SAFE_ENV}_${TIMESTAMP}.log}"
export AI3_AGENTIC_OUTPUT_DIR="${HUANXIN_AGENTIC_OUTPUT_DIR:-outputs/qwen36-35b-a3b-agentic-grpo-${SAFE_ENV}-${TIMESTAMP}}"

if [[ -n "${HUANXIN_AGENTIC_MODEL_NAME:-}" ]]; then
  export AI3_AGENTIC_MODEL_NAME="$HUANXIN_AGENTIC_MODEL_NAME"
fi
if [[ -n "${HUANXIN_AGENTIC_BENCHMARK_FILE:-}" ]]; then
  export AI3_AGENTIC_BENCHMARK_FILE="$HUANXIN_AGENTIC_BENCHMARK_FILE"
fi

exec bash "$ROOT_DIR/scripts/launch_qwen36_35b_a3b_agentic_grpo_asi1.sh" "$@"
