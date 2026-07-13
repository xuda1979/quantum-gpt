#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_JOB_REMOTE_ROOT="${AI_JOB_REMOTE_ROOT:-/root/software/quantum-gpt}" \
AI2_JOB_REMOTE_ROOT="${AI2_JOB_REMOTE_ROOT:-/root/software/quantum-gpt}" \
AI2_JOB_SHELL_WRAPPER="${AI2_JOB_SHELL_WRAPPER:-$ROOT_DIR/scripts/ai_shell.sh}" \
AI2_JOB_META_DIR="${AI2_JOB_META_DIR:-$ROOT_DIR/.huanxin_ai_jobs}" \
  bash "$ROOT_DIR/scripts/ai2_job.sh" "$@"
