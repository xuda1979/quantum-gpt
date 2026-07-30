#!/usr/bin/env bash
# =============================================================================
# Submit GRPO self-eval training task for Qwen3.6-27B to ASI2 via browser-automation.
#
# Usage:
#   bash scripts/submit_asi2_grpo_27b_selfeval_task.sh [--dry-run|--submit]
#   bash scripts/submit_asi2_grpo_27b_selfeval_task.sh          # dry-run: prints launch spec
#   bash scripts/submit_asi2_grpo_27b_selfeval_task.sh --submit # actually submits
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ENV_NAME="${ASI2_GRPO_ENV:-ASI2}"
REMOTE_ROOT="${ASI2_GRPO_REMOTE_ROOT:-/root/work/software/quantum-gpt}"
TASK_NAME="${ASI2_GRPO_TASK_NAME:-asi2-grpo-27b-selfeval}"
IMAGE_NAME="${ASI2_GRPO_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI2_GRPO_RESOURCE_GROUP:-huanxin-all-resource}"
NPU_COUNT="${ASI2_GRPO_NPU_COUNT:-2}"
CPU_CORES="${ASI2_GRPO_CPU_CORES:-8}"
MEMORY_GB="${ASI2_GRPO_MEMORY_GB:-128}"
ARTIFACT_STEM="${ASI2_GRPO_ARTIFACT_STEM:-huanxin-submit-task-run-asi2-grpo-27b-selfeval}"
TRAIN_DEV_URL="${ASI2_GRPO_TRAIN_DEV_URL:-}"

# Model and training config
MODEL_PATH="/root/work/filestorage/Qwen3.6-27B"
NAS_CHECKPOINT_ROOT="/root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval"

DRY_RUN="1"
SUBMIT="0"

for arg in "${@}"; do
  case "$arg" in
    --submit) SUBMIT="1" ;;
    --dry-run) DRY_RUN="1" ;;
    *) echo "Unknown arg: $arg" >&2; exit 2 ;;
  esac
done

# ---- Build remote script ----
cat > /tmp/asi2_grpo_27b_selfeval_remote.sh << 'REMOTEEOF'
#!/usr/bin/env bash
set -euo pipefail
echo "__ASI2_GRPO_27B_SELFEVAL_START__"
export TZ=Asia/Shanghai
date

# Verify model exists
if [[ ! -d "/root/work/filestorage/Qwen3.6-27B" ]]; then
  echo "ERROR: model not found at /root/work/filestorage/Qwen3.6-27B" >&2
  exit 1
fi

# Ensure NAS checkpoint root exists
mkdir -p /root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval

# Navigate to repo
cd /root/work/software/quantum-gpt
pwd
python3 --version

# Ensure we have the latest code
echo "Pulling latest code..."
git fetch origin && git checkout codex/asi2-qwen36-distillation-lora 2>/dev/null || true

# Launch GRPO training
bash scripts/asi2_launch_grpo_27b_selfeval.sh launch

# Wait for training to complete (poll log)
LOG_FILE="/root/work/software/quantum-gpt/logs/grpo_27b_selfeval/grpo_train_*.log"
echo "Training launched. Monitoring..."
sleep 30

# Show initial status
bash scripts/asi2_launch_grpo_27b_selfeval.sh status
REMOTEEOF

# ---- Build launch spec via Python ----
python3 << PYEOF
import json, shlex, sys

remote_script = open("/tmp/asi2_grpo_27b_selfeval_remote.sh").read()

launch_spec = {
    "env_name": "$ENV_NAME",
    "task_name": "$TASK_NAME",
    "image_name": "$IMAGE_NAME",
    "resource_group": "$RESOURCE_GROUP",
    "npu_count": int("$NPU_COUNT"),
    "cpu_cores": int("$CPU_CORES"),
    "memory_gb": int("$MEMORY_GB"),
    "remote_root": "$REMOTE_ROOT",
    "model_path": "$MODEL_PATH",
    "nas_checkpoint_root": "$NAS_CHECKPOINT_ROOT",
    "checkpoint_interval_hours": 2,
    "remote_script_body": remote_script,
    "description": "GRPO training for Qwen3.6-27B quantum coding with self-evaluation. Adapters saved to NAS every 2h.",
    "embed_patches": False,
}

print(json.dumps(launch_spec, indent=2))
PYEOF

if [[ "$SUBMIT" == "1" ]]; then
  # Use browser-automation to submit
  if [[ -z "$TRAIN_DEV_URL" ]]; then
    TRAIN_DEV_URL="https://huanxin.alibaba.com/train-dev"
  fi

  CMD=(
    node
    "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
    --url "$TRAIN_DEV_URL"
    --env "$ENV_NAME"
    --task-name "$TASK_NAME"
    --image-name "$IMAGE_NAME"
    --resource-group "$RESOURCE_GROUP"
    --npu-count "$NPU_COUNT"
    --cpu-cores "$CPU_CORES"
    --memory-gb "$MEMORY_GB"
    --remote-root "$REMOTE_ROOT"
    --launcher-script "$ROOT_DIR/scripts/submit_asi2_grpo_27b_selfeval_task.sh"
    --launcher-arg "__launch-spec"
    --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
    --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
    --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
    --submit
  )
  echo "Submitting to ASI2..."
  "${CMD[@]}"
else
  echo ""
  echo "=== DRY RUN === To actually submit, run:"
  echo "  bash scripts/submit_asi2_grpo_27b_selfeval_task.sh --submit"
fi
