#!/usr/bin/env bash
# ASI2 launcher: RL + soft-distillation loop for quantum SCIENCE (non-coding)
# on Qwen3.6-35B-A3B, 2 NPUs.
#
# Thin wrapper around asi2_launch_rl_distill_35b_2npu.sh. See
# asi1_launch_rl_distill_science_27b_2npu.sh for the science-mode docs and
# docs/rl-science-distill-rd-plan-2026-07-09.md for the full plan.
#
# Science-specific overrides:
#   CONFIG                  -> configs/distill/rl_distill_science_35b_v1.json
#   BUFFER_DIR              -> $NAS_ROOT/data/generated/rl_distill_science_35b_v1
#   VLLM_PORT               -> 8018
#   VLLM_SERVED_NAME        -> qwen36-35b-rl-distill-science
#   VLLM_LORA_ADAPTER_NAME  -> rl_distill_science_latest
#   ABLATION_PRESET         -> E_full
#   RUN_ID                  -> rl-distill-science-35b-<timestamp>
#   EVAL_TASKS              -> quantum_science
#   TEMPERATURE             -> 0.9
#   MAX_LENGTH              -> 3072
#   KL_COEFF                -> 0.4
#   TRAINER_MAX_STEPS_PER_ROUND -> 150

set -euo pipefail

export CONFIG="${CONFIG:-configs/distill/rl_distill_science_35b_v1.json}"
export BUFFER_DIR="${BUFFER_DIR:-${NAS_ROOT:-/root/work/software/quantum-gpt}/data/generated/rl_distill_science_35b_v1}"
export VLLM_PORT="${VLLM_PORT:-8018}"
export VLLM_SERVED_NAME="${VLLM_SERVED_NAME:-qwen36-35b-rl-distill-science}"
export VLLM_LORA_ADAPTER_NAME="${VLLM_LORA_ADAPTER_NAME:-rl_distill_science_latest}"
export ABLATION_PRESET="${ABLATION_PRESET:-E_full}"
export RUN_ID="${RUN_ID:-rl-distill-science-35b-$(date -u +%Y%m%dT%H%M%SZ)}"
export EVAL_TASKS="${EVAL_TASKS:-quantum_science}"
export TEMPERATURE="${TEMPERATURE:-0.9}"
export MAX_LENGTH="${MAX_LENGTH:-3072}"
export KL_COEFF="${KL_COEFF:-0.4}"
export TRAINER_MAX_STEPS_PER_ROUND="${TRAINER_MAX_STEPS_PER_ROUND:-150}"

exec bash "$(dirname "$0")/asi2_launch_rl_distill_35b_2npu.sh" "$@"
