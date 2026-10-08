#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_REQS="training/requirements-huanxin-cpu.txt"
GEMMA_REQS="training/requirements-gemma4-runtime.txt"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
REMOTE_ROOT="/root/work/quantum-gpt"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
ITERATION_PROFILE="${ITERATION_PROFILE:-fast}"
TIMEOUT_SEC="${TIMEOUT_SEC:-}"
POLL_SEC="${POLL_SEC:-}"
VISIBLE_DEVICES="${VISIBLE_DEVICES:-}"
NPROC_PER_NODE="${NPROC_PER_NODE:-}"
REQUIRED_IDLE_NPUS="${REQUIRED_IDLE_NPUS:-}"
STAGE_ONLY=0
DRY_RUN=0
GRPO_GROUP_SIZE="${GRPO_GROUP_SIZE:-}"
GRPO_STEPS="${GRPO_STEPS:-}"
GRPO_MAX_NEW_TOKENS="${GRPO_MAX_NEW_TOKENS:-}"
GRPO_MAX_SEQ_LENGTH="${GRPO_MAX_SEQ_LENGTH:-}"
GRPO_TEMPERATURE="${GRPO_TEMPERATURE:-}"
GRPO_LOG_STEPS="${GRPO_LOG_STEPS:-}"
PAPER_ROUTER_MAX_STEPS="${PAPER_ROUTER_MAX_STEPS:-}"
PAPER_ROUTER_EVAL_STEPS="${PAPER_ROUTER_EVAL_STEPS:-}"
PAPER_ROUTER_LOG_STEPS="${PAPER_ROUTER_LOG_STEPS:-}"
SFT_MAX_STEPS="${SFT_MAX_STEPS:-}"
SFT_EVAL_STEPS="${SFT_EVAL_STEPS:-}"
SFT_LOG_STEPS="${SFT_LOG_STEPS:-}"
TARGET="omnicoder9b"
MODEL_NAME=""
TRAIN_FILE=""
EVAL_FILE=""
BENCHMARK_FILE=""
SFT_ADAPTER_INIT=""
GRPO_ADAPTER_INIT=""
SFT_OUTPUT_DIR=""
GRPO_OUTPUT_DIR=""

shell_quote() {
  local value="${1//\'/\'\"\'\"\'}"
  printf "'%s'" "$value"
}

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/queue_ai2_timeboxed_pipeline.sh [--target <name>] [--iteration-profile <fast|standard>] [--visible-devices <ids>] [--nproc-per-node <n>] [--required-idle-npus <n>] [--stage-only] [--dry-run]

Stages the timeboxed 8-NPU launch payload to S3, syncs it to ai2, and starts
the remote watcher pipeline. Use --stage-only to stop after S3 staging.
Use --dry-run to preview only the S3 staging transfer.
EOF
  exit 1
}

apply_iteration_profile_defaults() {
  case "$ITERATION_PROFILE" in
    fast)
      VISIBLE_DEVICES="${VISIBLE_DEVICES:-6,7}"
      NPROC_PER_NODE="${NPROC_PER_NODE:-2}"
      REQUIRED_IDLE_NPUS="${REQUIRED_IDLE_NPUS:-2}"
      TIMEOUT_SEC="${TIMEOUT_SEC:-2700}"
      POLL_SEC="${POLL_SEC:-20}"
      PAPER_ROUTER_MAX_STEPS="${PAPER_ROUTER_MAX_STEPS:-8}"
      PAPER_ROUTER_EVAL_STEPS="${PAPER_ROUTER_EVAL_STEPS:-8}"
      PAPER_ROUTER_LOG_STEPS="${PAPER_ROUTER_LOG_STEPS:-1}"
      SFT_MAX_STEPS="${SFT_MAX_STEPS:-12}"
      SFT_EVAL_STEPS="${SFT_EVAL_STEPS:-6}"
      SFT_LOG_STEPS="${SFT_LOG_STEPS:-1}"
      GRPO_GROUP_SIZE="${GRPO_GROUP_SIZE:-2}"
      GRPO_STEPS="${GRPO_STEPS:-2}"
      GRPO_MAX_NEW_TOKENS="${GRPO_MAX_NEW_TOKENS:-96}"
      GRPO_MAX_SEQ_LENGTH="${GRPO_MAX_SEQ_LENGTH:-1536}"
      GRPO_TEMPERATURE="${GRPO_TEMPERATURE:-0.4}"
      GRPO_LOG_STEPS="${GRPO_LOG_STEPS:-1}"
      ;;
    standard)
      VISIBLE_DEVICES="${VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
      NPROC_PER_NODE="${NPROC_PER_NODE:-8}"
      REQUIRED_IDLE_NPUS="${REQUIRED_IDLE_NPUS:-8}"
      TIMEOUT_SEC="${TIMEOUT_SEC:-7200}"
      POLL_SEC="${POLL_SEC:-60}"
      PAPER_ROUTER_MAX_STEPS="${PAPER_ROUTER_MAX_STEPS:-20}"
      PAPER_ROUTER_EVAL_STEPS="${PAPER_ROUTER_EVAL_STEPS:-1000}"
      PAPER_ROUTER_LOG_STEPS="${PAPER_ROUTER_LOG_STEPS:-5}"
      SFT_MAX_STEPS="${SFT_MAX_STEPS:-40}"
      SFT_EVAL_STEPS="${SFT_EVAL_STEPS:-1000}"
      SFT_LOG_STEPS="${SFT_LOG_STEPS:-5}"
      GRPO_GROUP_SIZE="${GRPO_GROUP_SIZE:-4}"
      GRPO_STEPS="${GRPO_STEPS:-8}"
      GRPO_MAX_NEW_TOKENS="${GRPO_MAX_NEW_TOKENS:-128}"
      GRPO_MAX_SEQ_LENGTH="${GRPO_MAX_SEQ_LENGTH:-2048}"
      GRPO_TEMPERATURE="${GRPO_TEMPERATURE:-0.7}"
      GRPO_LOG_STEPS="${GRPO_LOG_STEPS:-1}"
      ;;
    *)
      echo "Unsupported iteration profile: $ITERATION_PROFILE" >&2
      exit 1
      ;;
  esac
}

apply_target_defaults() {
  case "$TARGET" in
    omnicoder9b)
      MODEL_NAME="${MODEL_NAME:-models/OmniCoder-9B}"
      TRAIN_FILE="${TRAIN_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl}"
      EVAL_FILE="${EVAL_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl}"
      BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v1.txt}"
      SFT_ADAPTER_INIT="${SFT_ADAPTER_INIT:-outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter}"
      GRPO_ADAPTER_INIT="${GRPO_ADAPTER_INIT:-outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter}"
      if [[ "$ITERATION_PROFILE" == "fast" ]]; then
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/omnicoder9b-quantum-generalization-grpo-8npu-fastiter}"
      else
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/omnicoder9b-quantum-generalization-sft-8npu-true40}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/omnicoder9b-quantum-generalization-grpo-8npu-true8}"
      fi
      ;;
    gemma4-e2b-it)
      MODEL_NAME="${MODEL_NAME:-models/gemma-4-E2B-it}"
      TRAIN_FILE="${TRAIN_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl}"
      EVAL_FILE="${EVAL_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl}"
      BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v1.txt}"
      if [[ "$ITERATION_PROFILE" == "fast" ]]; then
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-e2b-it-quantum-generalization-sft-8npu-fastiter}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-e2b-it-quantum-generalization-grpo-8npu-fastiter}"
      else
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-e2b-it-quantum-generalization-sft-8npu-true40}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-e2b-it-quantum-generalization-grpo-8npu-true8}"
      fi
      GRPO_ADAPTER_INIT="${GRPO_ADAPTER_INIT:-${SFT_OUTPUT_DIR}/adapter}"
      ;;
    gemma4-e4b-it)
      MODEL_NAME="${MODEL_NAME:-models/gemma-4-E4B-it}"
      TRAIN_FILE="${TRAIN_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl}"
      EVAL_FILE="${EVAL_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl}"
      BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v1.txt}"
      if [[ "$ITERATION_PROFILE" == "fast" ]]; then
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-e4b-it-quantum-generalization-sft-8npu-fastiter}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-e4b-it-quantum-generalization-grpo-8npu-fastiter}"
      else
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-e4b-it-quantum-generalization-sft-8npu-true40}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-e4b-it-quantum-generalization-grpo-8npu-true8}"
      fi
      GRPO_ADAPTER_INIT="${GRPO_ADAPTER_INIT:-${SFT_OUTPUT_DIR}/adapter}"
      ;;
    gemma4-26b-a4b-it)
      MODEL_NAME="${MODEL_NAME:-models/gemma-4-26B-A4B-it}"
      TRAIN_FILE="${TRAIN_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl}"
      EVAL_FILE="${EVAL_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl}"
      BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v1.txt}"
      if [[ "$ITERATION_PROFILE" == "fast" ]]; then
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-26b-a4b-it-quantum-generalization-sft-8npu-fastiter}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-26b-a4b-it-quantum-generalization-grpo-8npu-fastiter}"
      else
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-26b-a4b-it-quantum-generalization-sft-8npu-true40}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-26b-a4b-it-quantum-generalization-grpo-8npu-true8}"
      fi
      GRPO_ADAPTER_INIT="${GRPO_ADAPTER_INIT:-${SFT_OUTPUT_DIR}/adapter}"
      ;;
    gemma4-31b-it)
      MODEL_NAME="${MODEL_NAME:-models/gemma-4-31B-it}"
      TRAIN_FILE="${TRAIN_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl}"
      EVAL_FILE="${EVAL_FILE:-data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl}"
      BENCHMARK_FILE="${BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v1.txt}"
      if [[ "$ITERATION_PROFILE" == "fast" ]]; then
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-31b-it-quantum-generalization-sft-8npu-fastiter}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-31b-it-quantum-generalization-grpo-8npu-fastiter}"
      else
        SFT_OUTPUT_DIR="${SFT_OUTPUT_DIR:-outputs/gemma4-31b-it-quantum-generalization-sft-8npu-true40}"
        GRPO_OUTPUT_DIR="${GRPO_OUTPUT_DIR:-outputs/gemma4-31b-it-quantum-generalization-grpo-8npu-true8}"
      fi
      GRPO_ADAPTER_INIT="${GRPO_ADAPTER_INIT:-${SFT_OUTPUT_DIR}/adapter}"
      ;;
    *)
      echo "Unsupported target: $TARGET" >&2
      exit 1
      ;;
  esac
}

append_arg() {
  local command="$1"
  local flag="$2"
  local value="$3"
  printf '%s %s %s' "$command" "$flag" "$(shell_quote "$value")"
}

build_sft_command() {
  local command=""
  command="cd ${REMOTE_ROOT} && PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 TOKENIZERS_PARALLELISM=false ASCEND_RT_VISIBLE_DEVICES=${VISIBLE_DEVICES} torchrun --nproc_per_node=${NPROC_PER_NODE} training/qwen_sft_peft.py"
  command="$(append_arg "$command" --model-name "$MODEL_NAME")"
  if [[ -n "$SFT_ADAPTER_INIT" ]]; then
    command="$(append_arg "$command" --adapter-init "$SFT_ADAPTER_INIT")"
  fi
  command="$(append_arg "$command" --train-file "$TRAIN_FILE")"
  command="$(append_arg "$command" --eval-file "$EVAL_FILE")"
  command="$(append_arg "$command" --output-dir "$SFT_OUTPUT_DIR")"
  command+=" --device npu --max-length 512 --per-device-batch-size 1 --gradient-accumulation-steps 2 --learning-rate 2e-4 --num-epochs 1"
  command+=" --max-steps ${SFT_MAX_STEPS} --eval-steps ${SFT_EVAL_STEPS} --log-steps ${SFT_LOG_STEPS}"
  command+=" --train-on-completions-only --research-methods verifier_guided_repair_curriculum ast_anchor_interface_grounding"
  printf '%s' "$command"
}

build_grpo_command() {
  local command=""
  command="cd ${REMOTE_ROOT} && PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256 TOKENIZERS_PARALLELISM=false ASCEND_RT_VISIBLE_DEVICES=${VISIBLE_DEVICES} torchrun --nproc_per_node=${NPROC_PER_NODE} --master_port=29531 training/grpo_trainer.py"
  command="$(append_arg "$command" --model-name "$MODEL_NAME")"
  if [[ -n "$GRPO_ADAPTER_INIT" ]]; then
    command="$(append_arg "$command" --adapter-init "$GRPO_ADAPTER_INIT")"
  fi
  command="$(append_arg "$command" --benchmark-file "$BENCHMARK_FILE")"
  command="$(append_arg "$command" --output-dir "$GRPO_OUTPUT_DIR")"
  command+=" --domain-filter quantum --device npu"
  command+=" --group-size ${GRPO_GROUP_SIZE} --grpo-steps ${GRPO_STEPS} --max-new-tokens ${GRPO_MAX_NEW_TOKENS} --max-seq-length ${GRPO_MAX_SEQ_LENGTH} --temperature ${GRPO_TEMPERATURE}"
  command+=" --lr 5e-6 --kl-coeff 0.05 --reward-pass-weight 0.6 --reward-syntax-weight 0.1 --reward-interface-weight 0.15 --reward-verifier-weight 0.15 --ratio-clip-log-delta 4.0 --logit-clip 30.0 --min-reward-std 0.02 --curriculum-ema-decay 0.8 --curriculum-min-weight 0.1 --quantum-priority 1.1 --curriculum-uncertainty-bonus 0.2 --log-steps ${GRPO_LOG_STEPS} --research-methods clause_aware_verifier_reward ast_anchor_interface_grounding"
  printf '%s' "$command"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="$2"
      shift 2
      ;;
    --iteration-profile)
      ITERATION_PROFILE="$2"
      shift 2
      ;;
    --visible-devices)
      VISIBLE_DEVICES="$2"
      shift 2
      ;;
    --nproc-per-node)
      NPROC_PER_NODE="$2"
      shift 2
      ;;
    --required-idle-npus)
      REQUIRED_IDLE_NPUS="$2"
      shift 2
      ;;
    --model-name)
      MODEL_NAME="$2"
      shift 2
      ;;
    --train-file)
      TRAIN_FILE="$2"
      shift 2
      ;;
    --eval-file)
      EVAL_FILE="$2"
      shift 2
      ;;
    --benchmark-file)
      BENCHMARK_FILE="$2"
      shift 2
      ;;
    --sft-adapter-init)
      SFT_ADAPTER_INIT="$2"
      shift 2
      ;;
    --grpo-adapter-init)
      GRPO_ADAPTER_INIT="$2"
      shift 2
      ;;
    --sft-output-dir)
      SFT_OUTPUT_DIR="$2"
      shift 2
      ;;
    --grpo-output-dir)
      GRPO_OUTPUT_DIR="$2"
      shift 2
      ;;
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

apply_iteration_profile_defaults
apply_target_defaults
SFT_COMMAND="$(build_sft_command)"
GRPO_COMMAND="$(build_grpo_command)"

# Gemma 4 remote launch blocker removed 2026-04-13:
# transformers >= 5.6.0.dev0 supports AutoModelForCausalLM for Gemma4ForConditionalGeneration text-only use.
# Ensure the remote runtime has the same upgraded stack before launching.
if [[ "$TARGET" == gemma4-* ]]; then
  echo "INFO: Gemma 4 target selected. Ensure remote has transformers >= 5.5.0 (pip install git+https://github.com/huggingface/transformers.git)." >&2
fi

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
REMOTE_CMD+="nohup bash scripts/timeboxed_8npu_pipeline.sh --sft-command $(shell_quote "$SFT_COMMAND") --grpo-command $(shell_quote "$GRPO_COMMAND") --timeout-sec $(shell_quote "$TIMEOUT_SEC") --poll-sec $(shell_quote "$POLL_SEC") --required-idle-npus $(shell_quote "$REQUIRED_IDLE_NPUS") --status-file /tmp/quantum_timeboxed_pipeline_status.log --sft-log /tmp/quantum_timeboxed_sft.log --grpo-log /tmp/quantum_timeboxed_grpo.log > /tmp/quantum_timeboxed_pipeline_wrapper.log 2>&1 < /dev/null & "
REMOTE_CMD+="pid=\$!; echo __TIMEBOXED_PIPELINE__ pid=\$pid status=/tmp/quantum_timeboxed_pipeline_status.log wrapper=/tmp/quantum_timeboxed_pipeline_wrapper.log"

HUANXIN_WAIT_MS="$WAIT_MS" bash "$ROOT_DIR/scripts/ai2_fast_path.sh" exec "$REMOTE_CMD"
