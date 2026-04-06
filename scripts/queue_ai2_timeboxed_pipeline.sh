#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
REMOTE_ROOT="/root/root/work/quantum-gpt"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
TIMEOUT_SEC="${TIMEOUT_SEC:-7200}"
POLL_SEC="${POLL_SEC:-60}"
STAGE_ONLY=0
DRY_RUN=0
GRPO_GROUP_SIZE="${GRPO_GROUP_SIZE:-4}"
GRPO_STEPS="${GRPO_STEPS:-8}"
GRPO_MAX_NEW_TOKENS="${GRPO_MAX_NEW_TOKENS:-128}"
GRPO_MAX_SEQ_LENGTH="${GRPO_MAX_SEQ_LENGTH:-2048}"
GRPO_TEMPERATURE="${GRPO_TEMPERATURE:-0.7}"

SFT_COMMAND="cd ${REMOTE_ROOT} && PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 TOKENIZERS_PARALLELISM=false ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 torchrun --nproc_per_node=8 training/qwen_sft_peft.py --model-name models/OmniCoder-9B --adapter-init outputs/omnicoder9b-quantum-hard-v1-continue-true40-e2-20260330T142009CST/adapter --train-file data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl --eval-file data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl --output-dir outputs/omnicoder9b-quantum-generalization-sft-8npu-true40 --device npu --max-length 512 --per-device-batch-size 1 --gradient-accumulation-steps 2 --learning-rate 2e-4 --num-epochs 1 --max-steps 40 --eval-steps 1000 --log-steps 5 --train-on-completions-only --research-methods verifier_guided_repair_curriculum ast_anchor_interface_grounding"
GRPO_COMMAND="cd ${REMOTE_ROOT} && PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 TOKENIZERS_PARALLELISM=false ASCEND_RT_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 torchrun --nproc_per_node=8 --master_port=29531 training/grpo_trainer.py --model-name models/OmniCoder-9B --adapter-init outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter --benchmark-file evals/benchmarks/quantum_generalization_holdout_v1.txt --domain-filter quantum --output-dir outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8 --device npu --group-size ${GRPO_GROUP_SIZE} --grpo-steps ${GRPO_STEPS} --max-new-tokens ${GRPO_MAX_NEW_TOKENS} --max-seq-length ${GRPO_MAX_SEQ_LENGTH} --temperature ${GRPO_TEMPERATURE} --lr 5e-6 --kl-coeff 0.05 --reward-pass-weight 0.6 --reward-syntax-weight 0.1 --reward-interface-weight 0.15 --reward-verifier-weight 0.15 --ratio-clip-log-delta 4.0 --logit-clip 30.0 --min-reward-std 0.02 --curriculum-ema-decay 0.8 --curriculum-min-weight 0.1 --quantum-priority 1.1 --curriculum-uncertainty-bonus 0.2 --log-steps 1 --research-methods clause_aware_verifier_reward ast_anchor_interface_grounding"

shell_quote() {
  local value="${1//\'/\'\"\'\"\'}"
  printf "'%s'" "$value"
}

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/queue_ai2_timeboxed_pipeline.sh [--stage-only] [--dry-run]

Stages the timeboxed 8-NPU launch payload to S3, syncs it to ai2, and starts
the remote watcher pipeline. Use --stage-only to stop after S3 staging.
Use --dry-run to preview only the S3 staging transfer.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stage-only)
      STAGE_ONLY=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

stage_paths=(
  scripts/timeboxed_8npu_pipeline.sh
  scripts/timeboxed_8npu_watch_and_launch.sh
  training/qwen_sft_peft.py
  training/grpo_trainer.py
  training/research_plugins.py
  research/papers
)

cd "$ROOT_DIR"
push_cmd=(bash "$ROOT_DIR/scripts/push_to_s3.sh")
if [[ "$DRY_RUN" -eq 1 ]]; then
  push_cmd+=(--dry-run)
fi
push_cmd+=("${stage_paths[@]}")
"${push_cmd[@]}"

if [[ "$DRY_RUN" -eq 1 || "$STAGE_ONLY" -eq 1 ]]; then
  exit 0
fi

REMOTE_CMD="cd $(shell_quote "$REMOTE_ROOT"); "
REMOTE_CMD+="rclone copy $(shell_quote "$S3_ROOT/scripts") $(shell_quote "$REMOTE_ROOT/scripts") --include 'timeboxed_8npu_pipeline.sh' --fast-list --transfers 4 --checkers 8; "
REMOTE_CMD+="rclone copy $(shell_quote "$S3_ROOT/scripts") $(shell_quote "$REMOTE_ROOT/scripts") --include 'timeboxed_8npu_watch_and_launch.sh' --fast-list --transfers 4 --checkers 8; "
REMOTE_CMD+="rclone copy $(shell_quote "$S3_ROOT/training") $(shell_quote "$REMOTE_ROOT/training") --include 'qwen_sft_peft.py' --include 'grpo_trainer.py' --include 'research_plugins.py' --fast-list --transfers 4 --checkers 8; "
REMOTE_CMD+="rclone copy $(shell_quote "$S3_ROOT/research/papers") $(shell_quote "$REMOTE_ROOT/research/papers") --fast-list --transfers 4 --checkers 8; "
REMOTE_CMD+="nohup bash scripts/timeboxed_8npu_pipeline.sh --sft-command $(shell_quote "$SFT_COMMAND") --grpo-command $(shell_quote "$GRPO_COMMAND") --timeout-sec $(shell_quote "$TIMEOUT_SEC") --poll-sec $(shell_quote "$POLL_SEC") --status-file /tmp/quantum_timeboxed_pipeline_status.log --sft-log /tmp/quantum_timeboxed_sft.log --grpo-log /tmp/quantum_timeboxed_grpo.log > /tmp/quantum_timeboxed_pipeline_wrapper.log 2>&1 < /dev/null & "
REMOTE_CMD+="pid=\$!; echo __TIMEBOXED_PIPELINE__ pid=\$pid status=/tmp/quantum_timeboxed_pipeline_status.log wrapper=/tmp/quantum_timeboxed_pipeline_wrapper.log"

HUANXIN_WAIT_MS="$WAIT_MS" bash "$ROOT_DIR/scripts/ai2_shell.sh" "$REMOTE_CMD"
