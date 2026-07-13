#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_ROOT="${AI_REMOTE_ROOT:-/root/software/quantum-gpt}"
MODEL_NAME="${AI_TRAIN_MODEL_NAME:-models/Qwen3.6-27B}"
TRAIN_FILE="${AI_TRAIN_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl}"
EVAL_FILE="${AI_EVAL_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl}"
RUNTIME_SRC="${AI_TRANSFORMERS_RUNTIME_SRC:-$REMOTE_ROOT/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src}"
RUNTIME_HUB_COMPAT_VERSION="${AI_HF_HUB_COMPAT_VERSION:-1.8.0}"
VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
NPROC_PER_NODE="${NPROC_PER_NODE:-8}"
MAX_STEPS="${MAX_STEPS:-20}"
EVAL_STEPS="${EVAL_STEPS:-10}"
LOG_STEPS="${LOG_STEPS:-1}"
MAX_LENGTH="${MAX_LENGTH:-512}"
GRAD_ACCUM="${GRAD_ACCUM:-2}"
LR="${LR:-2e-4}"
PER_DEVICE_BATCH_SIZE="${PER_DEVICE_BATCH_SIZE:-1}"
MASTER_PORT="${MASTER_PORT:-29531}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_DIR="${AI_OUTPUT_DIR:-outputs/qwen36-27b-quantum-generalization-sft-ai-${TIMESTAMP}}"
LOG_PATH="${AI_LOG_PATH:-/tmp/qwen36_27b_quantum_generalization_sft_ai_${TIMESTAMP}.log}"

REMOTE_CMD=$(python3 - <<'PY' \
  "$MODEL_NAME" "$TRAIN_FILE" "$EVAL_FILE" "$OUTPUT_DIR" "$VISIBLE_DEVICES" \
    "$NPROC_PER_NODE" "$MAX_STEPS" "$EVAL_STEPS" "$LOG_STEPS" "$MAX_LENGTH" \
    "$GRAD_ACCUM" "$LR" "$PER_DEVICE_BATCH_SIZE" "$MASTER_PORT" "$RUNTIME_SRC" "$RUNTIME_HUB_COMPAT_VERSION"
import shlex
import sys

(
    model_name,
    train_file,
    eval_file,
    output_dir,
    visible_devices,
    nproc,
    max_steps,
    eval_steps,
    log_steps,
    max_length,
    grad_accum,
    lr,
    batch_size,
    master_port,
    runtime_src,
    runtime_hub_compat_version,
) = sys.argv[1:]

parts = [
    "set -euo pipefail",
    f"export ASCEND_RT_VISIBLE_DEVICES={shlex.quote(visible_devices)}",
    "export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
    "export TOKENIZERS_PARALLELISM=false",
    f"export QUANTUM_TRANSFORMERS_RUNTIME_SRC={shlex.quote(runtime_src)}",
    f"export QUANTUM_HF_HUB_COMPAT_VERSION={shlex.quote(runtime_hub_compat_version)}",
    "test -f training/qwen_sft_peft.py",
    f"test -d {shlex.quote(model_name)}",
    f"test -f {shlex.quote(train_file)}",
    f"test -f {shlex.quote(eval_file)}",
    "python3 -c \"import importlib.util,json; mods=['torch','transformers','peft']; print(json.dumps({'stage':'dependency_probe','modules':{m:bool(importlib.util.find_spec(m)) for m in mods}}), flush=True)\"",
    " ".join(
        [
            "torchrun",
            f"--nproc_per_node={shlex.quote(nproc)}",
            f"--master_port={shlex.quote(master_port)}",
            "training/qwen_sft_peft.py",
            "--model-name",
            shlex.quote(model_name),
            "--train-file",
            shlex.quote(train_file),
            "--eval-file",
            shlex.quote(eval_file),
            "--output-dir",
            shlex.quote(output_dir),
            "--device npu",
            "--max-length",
            shlex.quote(max_length),
            "--per-device-batch-size",
            shlex.quote(batch_size),
            "--gradient-accumulation-steps",
            shlex.quote(grad_accum),
            "--learning-rate",
            shlex.quote(lr),
            "--num-epochs 1",
            "--max-steps",
            shlex.quote(max_steps),
            "--eval-steps",
            shlex.quote(eval_steps),
            "--log-steps",
            shlex.quote(log_steps),
            "--train-on-completions-only",
        ]
    ),
]
print(" && ".join(parts))
PY
)

cd "$ROOT_DIR"
exec bash scripts/ai_job.sh start "qwen36-27b-quantum-sft-ai" "$LOG_PATH" "$REMOTE_CMD"
