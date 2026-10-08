#!/usr/bin/env bash
# Orchestrate the Qwen3.6-35B-A3B (W8A8 -> bf16 decompressed) verified-10k SFT on
# the ASI1 train-dev environment.
#
# The W8A8 frozen int8 checkpoint cannot train on the Ascend HF path because the
# int8 matmul reaches aclnnMm (DT_INT8 rejected). The trainer now forces
# compressed-tensors decompression to bf16 at load (run_compressed=False), so we
# shard the bf16 model across the 4 visible NPUs with a single process
# (balanced-layers) and train LoRA on the frozen bf16 base.
#
# Usage:
#   scripts/asi1_launch_verified10k_decompress.sh setup    # rclone config + S3 sync + deps
#   scripts/asi1_launch_verified10k_decompress.sh launch   # start training (nohup)
#   scripts/asi1_launch_verified10k_decompress.sh status   # tail log + ps
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"
cd "$ROOT_DIR"

ENV_NAME="${ASI1_ENV_NAME:-ASI1}"
REMOTE_ROOT="${ASI1_REMOTE_ROOT:-/workspace}"
CONF="${ASI1_RCLONE_CONFIG:-/tmp/iner-rclone-asi1.conf}"
RBIN="${ASI1_REMOTE_RCLONE_BIN:-/root/work/filestorage/rclone-bin}"
S3="${INER_S3_ROOT}"
MODEL="${ASI1_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
VIS="${ASI1_VISIBLE_DEVICES:-0,1,2,3}"
SPLIT_DIR="data/generated/quantum_finetune_verified_chat_sft"
RUN_ID="${ASI1_RUN_ID:-20260616}"
OUT="${ASI1_OUTPUT_DIR:-outputs/qwen36-35b-a3b-bf16dq-verified10k-sft-${RUN_ID}}"
LOG="${ASI1_LOG_PATH:-logs/asi1_verified10k_bf16dq_${RUN_ID}.log}"
PIDFILE="/tmp/asi1_verified10k_bf16dq.pid"

remote() {
  HUANXIN_USE_DAEMON=0 HUANXIN_ALLOW_STANDALONE_FALLBACK=1 \
    bash scripts/huanxin_env_shell.sh --env "$ENV_NAME" "$1"
}

cmd="${1:-status}"

case "$cmd" in
  setup)
    SETUP_SNIPPET="$(iner_remote_rclone_setup_script "$CONF")"
    SETUP_LOG="/tmp/asi1_dq_setup.log"
    SETUP_PID="/tmp/asi1_dq_setup.pid"
    INNER="set -euo pipefail
${SETUP_SNIPPET}
cd '${REMOTE_ROOT}'
mkdir -p logs reports outputs
echo __ASI1_DQ_SYNC_START__ \$(date -u +%FT%TZ)
for sub in training scripts/preflight_qwen36_ascend_hf_training.py ${SPLIT_DIR} artifacts/runtime-overlays/qwen35-moe-slim; do
  mkdir -p \"\$(dirname \"\$sub\")\"
  env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
    '${RBIN}' copy \"${S3}/\$sub\" \"\$sub\" --config '${CONF}' --s3-no-check-bucket --no-traverse \
    --transfers 8 --checkers 16 --low-level-retries 3 --retries 3 --contimeout 20s --timeout 180s
done
echo __ASI1_DQ_SYNC_DONE__ \$(date -u +%FT%TZ)
test -d '${MODEL}'
test -s training/qwen_sft_peft.py
test -s ${SPLIT_DIR}/train_chatml.jsonl
test -s ${SPLIT_DIR}/eval_chatml.jsonl
wc -l ${SPLIT_DIR}/train_chatml.jsonl ${SPLIT_DIR}/eval_chatml.jsonl
echo __ASI1_DQ_PIP_START__ \$(date -u +%FT%TZ)
python3 -m pip install --no-input --disable-pip-version-check peft accelerate 2>&1 | tail -12
python3 -c 'import peft, accelerate; print(\"__ASI1_DQ_DEPS_OK__ peft\", peft.__version__, \"accelerate\", accelerate.__version__)'
echo __ASI1_DQ_SETUP_DONE__ \$(date -u +%FT%TZ)"
    INNER_B64="$(printf '%s' "$INNER" | base64 | tr -d '\n')"
    REMOTE_SCRIPT="printf '%s' '${INNER_B64}' | base64 -d > /tmp/asi1_dq_setup.sh
nohup bash /tmp/asi1_dq_setup.sh > '${SETUP_LOG}' 2>&1 &
echo \$! > '${SETUP_PID}'
sleep 3
echo __ASI1_DQ_SETUP_LAUNCHED__ pid=\$(cat '${SETUP_PID}')
tail -n 5 '${SETUP_LOG}' 2>/dev/null || true"
    remote "$REMOTE_SCRIPT"
    ;;

  setup-status)
    SETUP_LOG="/tmp/asi1_dq_setup.log"
    SETUP_PID="/tmp/asi1_dq_setup.pid"
    REMOTE_SCRIPT="pid=\$(cat '${SETUP_PID}' 2>/dev/null || echo)
echo PID=\$pid
[ -n \"\$pid\" ] && (ps -p \$pid -o pid,stat,etime,cmd || echo SETUP_FINISHED) || echo NO_PID
echo '--- setup log tail ---'
tail -n 40 '${SETUP_LOG}' 2>/dev/null || echo NO_LOG"
    remote "$REMOTE_SCRIPT"
    ;;

  launch)
    REMOTE_SCRIPT="set -euo pipefail
cd '${REMOTE_ROOT}'
mkdir -p logs reports outputs '${OUT}'
export QUANTUM_TRANSFORMERS_RUNTIME_SRC=artifacts/runtime-overlays/qwen35-moe-slim
export QUANTUM_HF_HUB_COMPAT_VERSION=0.35.3
export ASCEND_RT_VISIBLE_DEVICES='${VIS}'
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export ALLOW_KNOWN_QWEN36_W8A8_ASCEND_HF_BLOCKER=1
export QWEN_SFT_DECOMPRESS_COMPRESSED_TENSORS=1
nohup python3 training/qwen_sft_peft.py \
  --model-name '${MODEL}' \
  --train-file ${SPLIT_DIR}/train_chatml.jsonl \
  --eval-file ${SPLIT_DIR}/eval_chatml.jsonl \
  --output-dir '${OUT}' \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib 54 \
  --max-length 512 \
  --max-steps 400 \
  --num-epochs 3 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 2e-5 \
  --eval-steps 50 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.0 \
  --target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --train-layernorm \
  --min-trainable-parameters 5000000 \
  --max-trainable-parameters 2000000000 \
  > '${LOG}' 2>&1 &
echo \$! > '${PIDFILE}'
sleep 6
echo __ASI1_DQ_LAUNCHED__ pid=\$(cat '${PIDFILE}')
ps -p \$(cat '${PIDFILE}') -o pid,stat,etime,cmd || true
tail -n 30 '${LOG}' || true"
    remote "$REMOTE_SCRIPT"
    ;;

  status)
    REMOTE_SCRIPT="cd '${REMOTE_ROOT}'
pid=\$(cat '${PIDFILE}' 2>/dev/null || echo)
echo PID=\$pid
[ -n \"\$pid\" ] && ps -p \$pid -o pid,stat,etime,cmd || echo NO_PROCESS
echo '--- log tail ---'
tail -n 60 '${LOG}' 2>/dev/null || echo NO_LOG"
    remote "$REMOTE_SCRIPT"
    ;;

  *)
    echo "Usage: $0 {setup|launch|status}" >&2
    exit 2
    ;;
esac
