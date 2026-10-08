#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"

export AI3_REMOTE_ROOT="${AI3_REMOTE_ROOT:-${AI_REMOTE_ROOT:-/root/software/quantum-gpt}}"
export AI3_JOB_REMOTE_ROOT="${AI3_JOB_REMOTE_ROOT:-${AI_JOB_REMOTE_ROOT:-$AI3_REMOTE_ROOT}}"
export AI3_JOB_SHELL_WRAPPER="${AI3_JOB_SHELL_WRAPPER:-${AI_JOB_SHELL_WRAPPER:-$ROOT_DIR/scripts/ai_shell.sh}}"
export AI3_JOB_META_DIR="${AI3_JOB_META_DIR:-${AI_JOB_META_DIR:-$ROOT_DIR/.huanxin_ai_jobs}}"

if [[ -n "${AI_AGENTIC_MODEL_NAME:-}" && -z "${AI3_AGENTIC_MODEL_NAME:-}" ]]; then
  export AI3_AGENTIC_MODEL_NAME="$AI_AGENTIC_MODEL_NAME"
fi
if [[ -n "${AI_AGENTIC_BENCHMARK_FILE:-}" && -z "${AI3_AGENTIC_BENCHMARK_FILE:-}" ]]; then
  export AI3_AGENTIC_BENCHMARK_FILE="$AI_AGENTIC_BENCHMARK_FILE"
fi
if [[ -n "${AI_AGENTIC_OUTPUT_DIR:-}" && -z "${AI3_AGENTIC_OUTPUT_DIR:-}" ]]; then
  export AI3_AGENTIC_OUTPUT_DIR="$AI_AGENTIC_OUTPUT_DIR"
fi
if [[ -n "${AI_AGENTIC_LOG_PATH:-}" && -z "${AI3_AGENTIC_LOG_PATH:-}" ]]; then
  export AI3_AGENTIC_LOG_PATH="$AI_AGENTIC_LOG_PATH"
fi
if [[ -n "${AI_AGENTIC_JOB_NAME:-}" && -z "${AI3_AGENTIC_JOB_NAME:-}" ]]; then
  export AI3_AGENTIC_JOB_NAME="$AI_AGENTIC_JOB_NAME"
fi

export AI3_AGENTIC_JOB_NAME="${AI3_AGENTIC_JOB_NAME:-qwen36-35b-a3b-agentic-grpo-ai}"
export AI3_AGENTIC_LOG_PATH="${AI3_AGENTIC_LOG_PATH:-/tmp/qwen36_35b_a3b_agentic_grpo_ai_${TIMESTAMP}.log}"

exec bash "$ROOT_DIR/scripts/launch_qwen36_35b_a3b_agentic_grpo_ai3.sh" "$@"
