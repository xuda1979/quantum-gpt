#!/usr/bin/env bash
set -euo pipefail

# Long-running job manager for Huanxin ai3, reusing the ai2_job.sh state machine
# but pointing at the ai3 shell wrapper and a dedicated metadata directory.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI3_JOB_REMOTE_ROOT="${AI3_JOB_REMOTE_ROOT:-/root/work/quantum-gpt}" \
AI2_JOB_REMOTE_ROOT="${AI3_JOB_REMOTE_ROOT:-/root/work/quantum-gpt}" \
AI2_JOB_SHELL_WRAPPER="${AI3_JOB_SHELL_WRAPPER:-$ROOT_DIR/scripts/ai3_shell.sh}" \
AI2_JOB_META_DIR="${AI3_JOB_META_DIR:-$ROOT_DIR/.huanxin_ai3_jobs}" \
  bash "$ROOT_DIR/scripts/ai2_job.sh" "$@"
