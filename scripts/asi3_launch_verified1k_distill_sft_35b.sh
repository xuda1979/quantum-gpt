#!/usr/bin/env bash
# ASI3 launcher: Qwen3.6-35B-A3B LoRA SFT on the 1k dedup GLM5.2 distillation set,
# VERIFIED-PASS-ONLY (strict runnable check), teacher logits dropped (plain cross-entropy SFT).
#
# Source dataset: data/generated/quantum_dedup_1k_glm52_soft_distill_v3 (1000 rows, ~94.75% pass)
# Filtered dataset: data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit
#                  (937 strict-PASS rows, no teacher_logits, 900 train / 37 eval split)
#
# Student: Qwen3.6-35B-A3B (W8A8 decompressed to bf16) with LoRA (rank 16, alpha 32).
# Trainer: training/qwen_sft_peft.py (plain cross-entropy SFT, completions-only).
#
# Usage:
#   scripts/asi3_launch_verified1k_distill_sft_35b.sh launch   # start training
#   scripts/asi3_launch_verified1k_distill_sft_35b.sh status   # tail log + list checkpoints
#
# Optional env overrides (same as asi3_launch_glm52_distill_sft_35b.sh):
#   MODEL_PATH, DATA, OUTPUT_DIR, ADAPTER_INIT, REMOTE_ROOT, NPU_MAX_MEMORY_GIB,
#   MAX_LENGTH, NUM_EPOCHS, PER_DEVICE_BATCH_SIZE, GRAD_ACCUM, LEARNING_RATE,
#   LORA_RANK, LORA_ALPHA, LORA_DROPOUT, TARGET_MODULES, RUN_ID
#
# This wrapper only sets DATA + RUN_ID defaults and delegates to the base launcher,
# so any fix to the base launcher (decompression, NPU flags, etc.) is inherited.

set -euo pipefail

export DATA="${DATA:-data/generated/quantum_dedup_1k_glm52_soft_distill_v3_verified_nologit}"
export RUN_ID="${RUN_ID:-verified1k-distill-35b-$(date -u +%Y%m%dT%H%M%SZ)}"

# Delegate to the base ASI3 35B distill SFT launcher.
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/asi3_launch_glm52_distill_sft_35b.sh" "$@"
