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
NPU_COUNT="${ASI2_GRPO_NPU_COUNT:-8}"
CPU_CORES="${ASI2_GRPO_CPU_CORES:-160}"
MEMORY_GB="${ASI2_GRPO_MEMORY_GB:-1920}"
ARTIFACT_STEM="${ASI2_GRPO_ARTIFACT_STEM:-huanxin-submit-task-run-asi2-grpo-27b-selfeval}"
TRAIN_DEV_URL="${ASI2_GRPO_TRAIN_DEV_URL:-}"

# Model and training config
MODEL_PATH="/root/work/filestorage/Qwen3.6-27B"
NAS_CHECKPOINT_ROOT="/root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval"

# FV-GSPO run parameters (overridable for short frontier-yield probes)
# Short probe: ASI2_GRPO_STEPS=24 ASI2_GRPO_CHECKPOINT_SECONDS=3600
RUN_STEPS="${ASI2_GRPO_STEPS:-500}"
RUN_LR="${ASI2_GRPO_LR:-2e-6}"
RUN_KL_COEFF="${ASI2_GRPO_KL_COEFF:-0.005}"
RUN_CHECKPOINT_SECONDS="${ASI2_GRPO_CHECKPOINT_SECONDS:-7200}"
RUN_NPU_COUNT="${ASI2_GRPO_NPU_COUNT:-8}"
RUN_LOSS_MODE="${ASI2_GRPO_LOSS_MODE:-gspo}"
RUN_GSPO_CLIP_LOW="${ASI2_GRPO_GSPO_CLIP_LOW:-0.0003}"
RUN_GSPO_CLIP_HIGH="${ASI2_GRPO_GSPO_CLIP_HIGH:-0.0004}"
RUN_REWARD_MODE="${ASI2_GRPO_REWARD_MODE:-p_dominant}"
RUN_MAX_NEW_TOKENS="${ASI2_GRPO_MAX_NEW_TOKENS:-1024}"
RUN_MAX_SEQ_LENGTH="${ASI2_GRPO_MAX_SEQ_LENGTH:-2048}"
RUN_GROUP_SIZE="${ASI2_GRPO_GROUP_SIZE:-8}"
RUN_NPU_MAX_MEMORY_GIB="${ASI2_GRPO_NPU_MAX_MEMORY_GIB:-54}"

DRY_RUN="1"
SUBMIT="0"

for arg in "$@"; do
  case "$arg" in
    --submit) SUBMIT="1" ;;
    --dry-run) DRY_RUN="1" ;;
    __launch-spec) ;;  # no-op: used by browser-automation deriveLaunchSpec
    *) echo "Unknown arg: $arg" >&2; exit 2 ;;
  esac
done

# ---- Build remote script ----
# NOTE: unquoted heredoc so RUN_* values are baked into the remote script;
# keep any literal '$' (none currently) escaped as \$.
cat > /tmp/asi2_grpo_27b_selfeval_remote.sh << REMOTEEOF
#!/usr/bin/env bash
set -euo pipefail
export TZ=Asia/Shanghai

# ---- bootstrap logging to shared NAS (readable via the dev-env daemon) ----
mkdir -p /root/work/software/quantum-gpt/logs/grpo_27b_selfeval
BOOTSTRAP_LOG="/root/work/software/quantum-gpt/logs/grpo_27b_selfeval/bootstrap_\$(date +%Y%m%dT%H%M%S).log"
exec >> "\$BOOTSTRAP_LOG" 2>&1
echo "__ASI2_GRPO_27B_SELFEVAL_START__ \$(date)"

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

# FV-GSPO run parameters (probe: short GRPO_STEPS; long run: full steps)
export GRPO_STEPS="$RUN_STEPS"
export LR="$RUN_LR"
export KL_COEFF="$RUN_KL_COEFF"
export CHECKPOINT_INTERVAL_SECONDS="$RUN_CHECKPOINT_SECONDS"
export NUM_NPU="$RUN_NPU_COUNT"
export LOSS_MODE="$RUN_LOSS_MODE"
export GSPO_CLIP_LOW="$RUN_GSPO_CLIP_LOW"
export GSPO_CLIP_HIGH="$RUN_GSPO_CLIP_HIGH"
export REWARD_MODE="$RUN_REWARD_MODE"
export MAX_NEW_TOKENS="$RUN_MAX_NEW_TOKENS"
export MAX_SEQ_LENGTH="$RUN_MAX_SEQ_LENGTH"

# Ascend memory fragmentation guard (HEARTBEAT lesson: NPU OOM without it)
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export NPU_DEVICE_MAP="balanced-layers"
export NPU_MAX_MEMORY_GIB="$RUN_NPU_MAX_MEMORY_GIB"
export GROUP_SIZE="$RUN_GROUP_SIZE"

# ---- install training deps ----
# Task-run containers boot from the bare image: peft/accelerate are NOT
# preinstalled (dev env has them, task containers do not).
echo "Installing training deps..."
# fast path: network install if the task container has internet
pip install --no-cache-dir -q peft accelerate 2>&1 | tail -3 || true
if ! python3 -c "import peft, accelerate" 2>/dev/null; then
  echo "network install failed; using offline wheelhouse..."
  python3 -m pip install --no-cache-dir --no-input --no-index --find-links /root/work/software/quantum-gpt/tools/wheels peft==0.19.1 accelerate==1.13.0 2>&1 | tail -6 || true
fi
python3 -c "import peft, accelerate, torch, transformers; print('PYDEPS_OK peft', peft.__version__, 'accelerate', accelerate.__version__, 'transformers', transformers.__version__)" || { echo "PYDEPS_FAIL"; pip list 2>/dev/null | grep -iE 'peft|accelerate|transformers|torch|sentencepiece' || true; exit 1; }

# Launch FV-GSPO training (launcher backgrounds torchrun via nohup)
bash scripts/asi2_launch_grpo_27b_selfeval.sh launch

# ---- keep-alive ----
# The platform tears the task environment down when the main command exits,
# which would kill the backgrounded trainer (p7 ran 63s then died with the env).
# Stay alive until the trainer process is gone.
echo "Training launched. Keeping container alive while the trainer runs..."
PID_FILE="/root/work/software/quantum-gpt/logs/grpo_27b_selfeval/grpo_27b_selfeval.pid"
while [[ -f "\$PID_FILE" ]]; do
  TID="\$(cat "\$PID_FILE" 2>/dev/null || true)"
  if [[ -z "\$TID" ]] || ! kill -0 "\$TID" 2>/dev/null; then
    echo "trainer pid \$TID not alive; re-checking in 30s..."
    sleep 30
    TID="\$(cat "\$PID_FILE" 2>/dev/null || true)"
    if [[ -z "\$TID" ]] || ! kill -0 "\$TID" 2>/dev/null; then
      echo "TRAINER_EXITED"
      break
    fi
  fi
  sleep 60
done
echo "CONTAINER_KEEPALIVE_END"

# Show final status
bash scripts/asi2_launch_grpo_27b_selfeval.sh status
REMOTEEOF

# ---- Build launch spec via Python ----
python3 << PYEOF
import base64, json, shlex, sys

remote_script = open("/tmp/asi2_grpo_27b_selfeval_remote.sh").read()

# Single-line python bootstrap (proven format, Jun 2026 qwen36-ai-sft1): the
# platform executes codeContents as ONE entry; multi-line codeContents (one
# entry per script line) fails at boot with 00:00:00.
payload_b64 = base64.b64encode(remote_script.encode("utf-8")).decode("ascii")
execution_command = (
    "python3 -c "
    + shlex.quote(
        "b=__import__('base64');"
        "p=__import__('pathlib').Path('/tmp/asi2_grpo_27b_selfeval_full.sh');"
        f"p.write_bytes(b.b64decode('{payload_b64}'));"
        "p.chmod(0o700);"
        "s=__import__('subprocess');"
        "raise SystemExit(s.run(['bash',str(p)]).returncode)"
    )
)

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
    "remote_command": execution_command,
    "execution_command": execution_command,
    "description": "FV-GSPO training for Qwen3.6-27B quantum coding: frontier-router GRPO on learnable mixed-outcome groups, leave-one-out advantages, GSPO sequence clipping (3e-4/4e-4), all-fail tasks routed to repair queue, 50/25/25 targeted/neighbor/replay mix, circuit breakers. Executable tests authoritative (self-judge weight 0).",
    "embed_patches": False,
}

print(json.dumps(launch_spec, indent=2))
PYEOF

if [[ "$SUBMIT" == "1" ]]; then
  # Use browser-automation to submit
  if [[ -z "$TRAIN_DEV_URL" ]]; then
    TRAIN_DEV_URL="https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-868c196fb82d3e0b8cfbbe826d8afd0a?name=ASI2"
  fi

  CMD=(
    node
    "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
    --url "$TRAIN_DEV_URL"
    --task-name "$TASK_NAME"
    --image-name "$IMAGE_NAME"
    --resource-group "$RESOURCE_GROUP"
    --instance-count 1
    --accelerator-cards "$NPU_COUNT"
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
  if [[ "${ASI2_GRPO_IGNORE_QUOTA:-1}" == "1" ]]; then
    CMD+=(--ignore-project-quota-text)
  fi
  if [[ "${ASI2_GRPO_DIRECT_SUBMIT:-0}" == "1" ]]; then
    CMD+=(--direct-submit-only)
  fi
  echo "Submitting to ASI2..."
  "${CMD[@]}"
else
  echo ""
  echo "=== DRY RUN === To actually submit, run:" >&2
  echo "  bash scripts/submit_asi2_grpo_27b_selfeval_task.sh --submit" >&2
fi
