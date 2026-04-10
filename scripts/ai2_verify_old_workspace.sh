#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export HUANXIN_PROFILE_COPY_NAME="${HUANXIN_PROFILE_COPY_NAME:-quantum-rnd}"
export HUANXIN_HEADLESS="${HUANXIN_HEADLESS:-1}"

REMOTE_CMD=$'cd /root/root/work/quantum-gpt\npwd\nif [ -f models/OmniCoder-9B/config.json ]; then echo BASE_CONFIG_OK; else echo BASE_CONFIG_MISSING; fi\nif [ -f models/OmniCoder-9B/model.safetensors ] || ls models/OmniCoder-9B/model-*.safetensors >/dev/null 2>&1; then echo BASE_WEIGHTS_OK; else echo BASE_WEIGHTS_MISSING; fi\nif [ -f outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST/adapter/adapter_model.safetensors ]; then echo ADAPTER_OK; else echo ADAPTER_MISSING; fi\nif [ -f /tmp/old_root_artifact_copy.log ]; then echo COPY_LOG_PRESENT; tail -n 20 /tmp/old_root_artifact_copy.log; else echo COPY_LOG_MISSING; fi\ncommand -v codex || true\n/root/.local/bin/codex --version || true'

node browser-automation/huanxin_shell_exec.js ai2 --wait-ms 180000 --command "$REMOTE_CMD"
