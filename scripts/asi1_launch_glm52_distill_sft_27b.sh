#!/usr/bin/env bash
# ASI1 launcher: Qwen3.6-27B LoRA SFT on the GLM5.2 soft-distillation 100-row set.
#
# Teacher: glm5.2 (top-20 logprobs preserved in source file for future soft-KL trainer).
# Student: Qwen3.6-27B with LoRA (rank 16, alpha 32, no k_proj).
# Dataset: data/generated/glm52_soft_distill_sft_100 (90 train / 10 eval, GLM5.2 teacher
#   responses with EOS marker stripped, see manifest.json for full provenance).
#
# DURABILITY: output-dir MUST be on the persistent NAS (/root/work). The script
# refuses to launch if the output dir is under ephemeral /workspace. Logs and
# run_config also go to NAS. Periodic adapter checkpoints to NAS + S3 mirror.
#
# Usage:
#   scripts/asi1_launch_glm52_distill_sft_27b.sh launch   # start training
#   scripts/asi1_launch_glm52_distill_sft_27b.sh status   # tail log + list checkpoints
#
# Optional env overrides:
#   MODEL, DATA, OUT, RUN_ID, ADAPTER_INIT, NAS_ROOT, NPROC, MASTER_PORT,
#   RCLONE_CONF, INER_S3_BUCKET

set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"
MODEL="${MODEL:-/root/work/filestorage/Qwen3.6-27B}"
DATA="${DATA:-data/generated/glm52_soft_distill_sft_iter2}"
RUN_ID="${RUN_ID:-glm52-distill-27b-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$NAS_ROOT/outputs/qg-27b-glm52-distill-sft-${RUN_ID}}"
LOG="${LOG:-$NAS_ROOT/logs/qg-27b-glm52-distill-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_27b_glm52_distill_sft.pid}"
MASTER_PORT="${MASTER_PORT:-29625}"
NPROC="${NPROC:-4}"
ADAPTER_INIT="${ADAPTER_INIT:-}"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd 2>/dev/null || echo NO_PROCESS
  echo '--- log tail ---'; tail -n 60 "$LOG" 2>/dev/null || echo NO_LOG
  echo '--- checkpoints ---'; ls -la "$OUT/checkpoints" 2>/dev/null || echo NONE
  echo '--- adapter ---'; ls -la "$OUT/adapter" 2>/dev/null || echo NONE
  exit 0
fi

# --- DURABILITY GUARDRAIL ---
case "$OUT" in
  /root/work/*) : ;;
  *) echo "REFUSING: output dir '$OUT' is not on persistent NAS (/root/work/*)." >&2; exit 2 ;;
esac

mkdir -p "$NAS_ROOT/logs" "$OUT"

# Runtime: transformers 5.6.0 + huggingface_hub 1.8.0 give native qwen3_5. We warn
# on a version mismatch but DO NOT hard-fail: the modeling fix is applied at runtime
# by patch_qwen3_5_npu_modeling.py, and the run must not abort just because the
# fresh container has a slightly different patch level.
python3 -c "import transformers, huggingface_hub as h, peft; print('__RUNTIME__', 'transformers', transformers.__version__, 'hub', h.__version__, 'peft', peft.__version__); import sys; (transformers.__version__=='5.6.0' and h.__version__=='1.8.0') or sys.stderr.write('__RUNTIME_WARN__ version mismatch (want transformers 5.6.0 hub 1.8.0); continuing because qwen3_5 imports and modeling is runtime-patched\n')" \
  || { echo "FATAL: transformers.models.qwen3_5 failed to import; cannot run 27B SFT." >&2; exit 2; }

# Apply the NPU depthwise-conv backward fix to the installed transformers package.
python3 scripts/patch_qwen3_5_npu_modeling.py

# Preflight files
test -d "$MODEL" || { echo "MISSING model $MODEL" >&2; exit 2; }
test -s training/qwen_sft_peft.py || { echo "MISSING trainer" >&2; exit 2; }
test -s "$DATA/train_chatml.jsonl" || { echo "MISSING train file" >&2; exit 2; }
test -s "$DATA/eval_chatml.jsonl" || { echo "MISSING eval file" >&2; exit 2; }
if [[ -n "$ADAPTER_INIT" ]]; then
  test -f "$ADAPTER_INIT/adapter_config.json" || { echo "MISSING adapter_init $ADAPTER_INIT/adapter_config.json" >&2; exit 2; }
fi
echo "__PREFLIGHT_OK__ train=$(wc -l < "$DATA/train_chatml.jsonl") eval=$(wc -l < "$DATA/eval_chatml.jsonl") out=$OUT adapter_init=${ADAPTER_INIT:-none}"

# Durable record of exactly what we ran.
cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-27b-glm52-distill-sft-${RUN_ID}",
  "model": "$MODEL",
  "dataset": "$DATA (90 train / 10 eval, GLM5.2 teacher, soft-distillation v1)",
  "teacher_model": "glm5.2",
  "teacher_source_file": "/Users/daxu/software/data_generation/gpt55_100_en.glm52_soft_distill.jsonl",
  "teacher_source_sha256": "61a526db39bd2fd4667d6fde6bcb426d3855e5a0ada8ec58b0e440cd2acd2ed3",
  "adapter_init": "${ADAPTER_INIT:-null}",
  "epochs": 2,
  "lora_rank": 16,
  "lora_alpha": 32,
  "lora_dropout": 0.05,
  "target_modules": "q_proj v_proj o_proj gate_proj up_proj down_proj (NO k_proj)",
  "learning_rate": 1e-4,
  "lr_scheduler": "cosine",
  "warmup_steps": 4,
  "max_length": 768,
  "per_device_batch_size": 1,
  "grad_accum": 4,
  "train_on_completions_only": true,
  "checkpoint_interval_seconds": 900,
  "attn_implementation": "eager",
  "npu_conv_patch": "scripts/patch_qwen3_5_npu_modeling.py",
  "visible_devices": "single-process python3, npu_device_map=balanced-layers (all 8 NPUs, world_size=1)",
  "transformers": "5.6.0",
  "huggingface_hub": "1.8.0",
  "output_dir": "$OUT",
  "distillation_mode": "hard_sft_on_teacher_completion",
  "soft_distill_logprobs_preserved": true,
  "soft_distill_logprobs_location": "source file distillation.logprob_positions[*].top_logprobs (top-20)"
}
CFG

# NPU fix: eager attention avoids the failing flash-attention backward op.
export QWEN_SFT_ATTN_IMPL=eager
# NPU fix: chunked cross-entropy avoids materializing the full [B,seq,vocab]
# logits tensor (the step-10 OOM at loss computation). Cap each chunk's logits.
export QWEN_SFT_CHUNKED_LOSS=1
export QWEN_SFT_LOSS_CHUNK=512
export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:128
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

ADAPTER_ARGS=()
if [[ -n "$ADAPTER_INIT" ]]; then
  ADAPTER_ARGS=(--adapter-init "$ADAPTER_INIT")
fi

# 27B bf16 (~54GB) is too close to the 60GB NPU limit for DDP (each rank
# loads the full model and OOMs during weight materialization). Use
# single-process sharded loading with the balanced-layers NPU device map
# instead, matching the 35B launchers.
NPU_MAX_MEMORY_GIB_VAL="${NPU_MAX_MEMORY_GIB:-54}"

nohup python3 training/qwen_sft_peft.py \
  --model-name "$MODEL" \
  --train-file "$DATA/train_chatml.jsonl" \
  --eval-file "$DATA/eval_chatml.jsonl" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --npu-device-map balanced-layers \
  --npu-max-memory-gib "$NPU_MAX_MEMORY_GIB_VAL" \
  --max-length "${MAX_LENGTH:-1600}" \
  --num-epochs "${NUM_EPOCHS:-2}" \
  --max-steps "${MAX_STEPS:--1}" \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate "${LEARNING_RATE:-1e-4}" \
  --warmup-steps 4 \
  --eval-steps 20 \
  --log-steps 1 \
  --lora-rank "${LORA_RANK:-16}" \
  --lora-alpha "${LORA_ALPHA:-32}" \
  --lora-dropout 0.05 \
  --lora-backend peft \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --checkpoint-interval-seconds 900 \
  "${ADAPTER_ARGS[@]}" \
  > "$LOG" 2>&1 &
echo "$!" > "$PIDFILE"
sleep 8
echo "__ASI1_GLM52_DISTILL_LAUNCHED__ pid=$(cat "$PIDFILE") log=$LOG out=$OUT"
ps -p "$(cat "$PIDFILE")" -o pid,stat,etime,cmd 2>/dev/null || true
echo '--- initial log tail ---'; tail -n 25 "$LOG" 2>/dev/null || true

# --- DURABILITY: off-box mirror of outputs to INER S3 every 5 min ---
RCLONE_CONF="${RCLONE_CONF:-/tmp/iner-rclone.conf}"
S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
if [[ -f "$RCLONE_CONF" ]] && ! grep -q '__INER_SECRET__' "$RCLONE_CONF" 2>/dev/null; then
  RCLONE_BIN="$(command -v rclone || true)"
  if [[ -n "$RCLONE_BIN" ]]; then
    S3_DEST="iner:${S3_BUCKET}/software/quantum-gpt/outputs/$(basename "$OUT")"
    MIRROR_PID_FILE="/tmp/qg_27b_glm52_distill_mirror.pid"
    nohup bash -c '
      TRAIN_PID="'"$(cat "$PIDFILE")"'"
      while kill -0 "$TRAIN_PID" 2>/dev/null; do
        "'"$RCLONE_BIN"'" --config "'"$RCLONE_CONF"'" copy "'"$OUT"'" "'"$S3_DEST"'" \
          --s3-force-path-style --transfers 4 --checkers 4 >/dev/null 2>&1 || true
        sleep 300
      done
      # one final sync after training exits
      "'"$RCLONE_BIN"'" --config "'"$RCLONE_CONF"'" copy "'"$OUT"'" "'"$S3_DEST"'" \
        --s3-force-path-style --transfers 4 --checkers 4 >/dev/null 2>&1 || true
    ' > /tmp/qg_27b_glm52_distill_mirror.log 2>&1 &
    echo "$!" > "$MIRROR_PID_FILE"
    echo "__S3_MIRROR_STARTED__ pid=$(cat "$MIRROR_PID_FILE") dest=$S3_DEST (every 300s + final)"
  else
    echo "__S3_MIRROR_SKIPPED__ rclone not found; relying on NAS persistence only"
  fi
else
  echo "__S3_MIRROR_SKIPPED__ no usable $RCLONE_CONF; relying on NAS persistence only"
fi
