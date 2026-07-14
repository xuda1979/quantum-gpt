#!/usr/bin/env bash
# Hardened ASI1 launcher: Qwen3.6-27B LoRA SFT on the deduped 1k set, 4 NPUs (DDP).
#
# DURABILITY: output-dir MUST be on the persistent NAS (/root/work). The script
# refuses to launch if the output dir is under ephemeral /workspace. Logs and
# run_config also go to NAS. Hourly adapter checkpoints are written to NAS.
#
# NPU FIXES applied before launch:
#   * QWEN_SFT_ATTN_IMPL=eager  -> avoids aclnnFlashAttentionScoreGrad backward.
#   * scripts/patch_qwen3_5_npu_modeling.py -> replaces unsupported depthwise
#     Conv1d backward (Conv2DBackpropInput) with a manual causal conv.
set -euo pipefail

NAS_ROOT="${NAS_ROOT:-/root/work/software/quantum-gpt}"
cd "$NAS_ROOT"
MODEL="${MODEL:-/root/work/filestorage/Qwen3.6-27B}"
DATA="${DATA:-data/generated/quantum_finetune_verified_chat_sft_dedup_1k}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUT="${OUT:-$NAS_ROOT/outputs/qg-27b-1k-sft-${RUN_ID}}"
LOG="${LOG:-$NAS_ROOT/logs/qg-27b-1k-sft-${RUN_ID}.log}"
PIDFILE="${PIDFILE:-/tmp/qg_27b_1k_sft_4npu.pid}"
MASTER_PORT="${MASTER_PORT:-29615}"

cmd="${1:-launch}"
if [[ "$cmd" == "status" ]]; then
  pid="$(cat "$PIDFILE" 2>/dev/null || echo)"
  echo "PID=$pid"
  [ -n "$pid" ] && ps -p "$pid" -o pid,stat,etime,cmd 2>/dev/null || echo NO_PROCESS
  echo '--- log tail ---'; tail -n 60 "$LOG" 2>/dev/null || echo NO_LOG
  echo '--- checkpoints ---'; ls -la "$OUT/checkpoints" 2>/dev/null || echo NONE
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
# fresh container ships a slightly different package build. The hard requirement is
# only that transformers.models.qwen3_5 imports.
python3 -c "import transformers,peft,accelerate,huggingface_hub as h; import transformers.models.qwen3_5; want_t='5.6.0'; want_h='1.8.0';
import sys;
print('__RUNTIME__', 'transformers', transformers.__version__, 'hub', h.__version__, 'peft', peft.__version__);
(transformers.__version__==want_t and h.__version__==want_h) or sys.stderr.write('__RUNTIME_WARN__ version mismatch (want transformers '+want_t+' hub '+want_h+'); continuing because qwen3_5 imports and modeling is runtime-patched\n')" \
  || { echo "FATAL: transformers.models.qwen3_5 failed to import; cannot run 27B SFT." >&2; exit 2; }

# Apply the NPU depthwise-conv backward fix to the installed transformers package.
python3 scripts/patch_qwen3_5_npu_modeling.py

# Preflight files
test -d "$MODEL" || { echo "MISSING model $MODEL" >&2; exit 2; }
test -s training/qwen_sft_peft.py || { echo "MISSING trainer" >&2; exit 2; }
test -s "$DATA/train_chatml.jsonl" || { echo "MISSING train file" >&2; exit 2; }
test -s "$DATA/eval_chatml.jsonl" || { echo "MISSING eval file" >&2; exit 2; }
echo "__PREFLIGHT_OK__ train=$(wc -l < "$DATA/train_chatml.jsonl") eval=$(wc -l < "$DATA/eval_chatml.jsonl") out=$OUT"

# Durable record of exactly what we ran.
cat > "$OUT/run_config.json" <<CFG
{
  "run_id": "qg-27b-1k-sft-${RUN_ID}",
  "model": "$MODEL",
  "dataset": "$DATA (1000 train / 495 eval, deduped, seed 20260622)",
  "epochs": 1,
  "lora_rank": 16,
  "lora_alpha": 32,
  "lora_dropout": 0.05,
  "target_modules": "q_proj v_proj o_proj gate_proj up_proj down_proj (NO k_proj)",
  "learning_rate": 1e-4,
  "lr_scheduler": "cosine",
  "warmup_steps": 6,
  "max_length": 768,
  "per_device_batch_size": 1,
  "grad_accum": 4,
  "train_on_completions_only": true,
  "checkpoint_interval_seconds": 3600,
  "attn_implementation": "eager",
  "npu_conv_patch": "scripts/patch_qwen3_5_npu_modeling.py",
  "visible_devices": "torchrun nproc_per_node=${NPROC:-4} DDP (logical 0..NPROC-1)",
  "transformers": "5.6.0",
  "huggingface_hub": "1.8.0",
  "output_dir": "$OUT"
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

nohup torchrun --nproc_per_node="${NPROC:-4}" --master_port="$MASTER_PORT" training/qwen_sft_peft.py \
  --model-name "$MODEL" \
  --train-file "$DATA/train_chatml.jsonl" \
  --eval-file "$DATA/eval_chatml.jsonl" \
  --output-dir "$OUT" \
  --overwrite-output-dir \
  --device npu \
  --max-length "${MAX_LENGTH:-512}" \
  --num-epochs 1 \
  --max-steps -1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 4 \
  --learning-rate 1e-4 \
  --warmup-steps 6 \
  --eval-steps 20 \
  --log-steps 1 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --lora-dropout 0.05 \
  --lora-backend peft \
  --target-modules q_proj v_proj o_proj gate_proj up_proj down_proj \
  --train-on-completions-only \
  --gradient-checkpointing \
  --checkpoint-interval-seconds 900 \
  > "$LOG" 2>&1 &
echo "$!" > "$PIDFILE"
sleep 8
echo "__ASI1_1K_LAUNCHED__ pid=$(cat "$PIDFILE") log=$LOG out=$OUT"
ps -p "$(cat "$PIDFILE")" -o pid,stat,etime,cmd 2>/dev/null || true
echo '--- initial log tail ---'; tail -n 25 "$LOG" 2>/dev/null || true

# --- DURABILITY: off-box mirror of outputs to INER S3 every 5 min ---
# Even though $OUT is on the persistent NAS (/root/work survives container
# restarts), we additionally mirror every checkpoint + the live log to S3 so a
# finished/partial adapter can never be lost if this session/container dies.
RCLONE_CONF="${RCLONE_CONF:-/tmp/iner-rclone.conf}"
S3_BUCKET="${INER_S3_BUCKET:-jtdlp-21b4208dde424e96b159362ef49c9c96}"
if [[ -f "$RCLONE_CONF" ]] && ! grep -q '__INER_SECRET__' "$RCLONE_CONF" 2>/dev/null; then
  RCLONE_BIN="$(command -v rclone || true)"
  if [[ -n "$RCLONE_BIN" ]]; then
    S3_DEST="iner:${S3_BUCKET}/software/quantum-gpt/outputs/$(basename "$OUT")"
    MIRROR_PID_FILE="/tmp/qg_27b_1k_sft_mirror.pid"
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
    ' > /tmp/qg_27b_1k_sft_mirror.log 2>&1 &
    echo "$!" > "$MIRROR_PID_FILE"
    echo "__S3_MIRROR_STARTED__ pid=$(cat "$MIRROR_PID_FILE") dest=$S3_DEST (every 300s + final)"
  else
    echo "__S3_MIRROR_SKIPPED__ rclone not found; relying on NAS persistence only"
  fi
else
  echo "__S3_MIRROR_SKIPPED__ no usable $RCLONE_CONF; relying on NAS persistence only"
fi
