#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${AI2_REMOTE_ROOT:-/root/root/work/quantum-gpt}"
RUN_DIR="$ROOT_DIR/outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST"
LOG_PATH="/tmp/omnicoder_merge_full.log"
OUTPUT_DIR="$RUN_DIR/merged_full"

cd "$ROOT_DIR"
rm -f "$LOG_PATH"
rm -rf "$OUTPUT_DIR"

export PYTHONPATH="$ROOT_DIR/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/overlay-site-packages"
export QUANTUM_TRANSFORMERS_RUNTIME_SRC="$ROOT_DIR/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src"
export QUANTUM_HF_HUB_COMPAT_VERSION="1.8.0"
export QUANTUM_RUNTIME_HTTPX_STUB="0"
export PYTHONPYCACHEPREFIX="/tmp/pycache"

nohup python3 scripts/export_merged_peft_model.py \
  --base-model models/OmniCoder-9B \
  --adapter outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST/adapter \
  --output-dir "$OUTPUT_DIR" \
  --device cpu \
  >"$LOG_PATH" 2>&1 </dev/null &

echo "MERGE_CPU_PID:$!"
