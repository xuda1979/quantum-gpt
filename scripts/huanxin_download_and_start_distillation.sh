#!/usr/bin/env bash
set -euo pipefail

REMOTE_ROOT="${HUANXIN_DISTILL_REMOTE_ROOT:-/vllm-workspace/quantum-gpt}"
S3_ROOT="${HUANXIN_DISTILL_S3_ROOT:-iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt}"
S3_ENDPOINT="${INER_S3_ENDPOINT:-https://iner.aihuanxin.cn}"
S3_ACCESS_KEY_ID="${INER_ACCESS_KEY_ID:-OXF5ar4y}"
MODEL_NAME="${HUANXIN_DISTILL_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B}"
SPLIT_DIR="${HUANXIN_DISTILL_SPLIT_DIR:-data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft}"
OUTPUT_DIR="${HUANXIN_DISTILL_OUTPUT_DIR:-outputs/qwen36-35b-a3b-distill-uniform-lora-asi2-allnpu-r64-broad-ln-l512-s40}"
LOG_PATH="${HUANXIN_DISTILL_LOG_PATH:-logs/asi2_distillation_uniform_lora_35b_allnpu_r64_broad_ln_l512_s40.log}"
MAX_LENGTH="${HUANXIN_DISTILL_MAX_LENGTH:-512}"
MAX_STEPS="${HUANXIN_DISTILL_MAX_STEPS:-40}"
NUM_EPOCHS="${HUANXIN_DISTILL_NUM_EPOCHS:-3}"
LORA_RANK="${HUANXIN_DISTILL_LORA_RANK:-64}"
LORA_ALPHA="${HUANXIN_DISTILL_LORA_ALPHA:-128}"
LORA_DROPOUT="${HUANXIN_DISTILL_LORA_DROPOUT:-0.0}"
MAX_TRAINABLE_PARAMETERS="${HUANXIN_DISTILL_MAX_TRAINABLE_PARAMETERS:-1000000000}"
MIN_TRAINABLE_PARAMETERS="${HUANXIN_DISTILL_MIN_TRAINABLE_PARAMETERS:-200000000}"
LEARNING_RATE="${HUANXIN_DISTILL_LEARNING_RATE:-5e-5}"
EVAL_STEPS="${HUANXIN_DISTILL_EVAL_STEPS:-10}"
LOG_STEPS="${HUANXIN_DISTILL_LOG_STEPS:-5}"
TARGET_MODULES="${HUANXIN_DISTILL_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
MASTER_PORT="${HUANXIN_DISTILL_MASTER_PORT:-29542}"
DRY_RUN=0
SKIP_SYNC=0

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/huanxin_download_and_start_distillation.sh [options]

Run this inside the target Huanxin shell or task pod. It downloads the uploaded
quantum-gpt snapshot from the INER S3 relay, then starts Qwen3.6-35B-A3B LoRA
distillation SFT on all visible NPUs.

Required unless INER_RCLONE_CONFIG points to an existing rclone config:
  INER_SECRET_ACCESS_KEY

Options:
  --dry-run             Print the planned sync and torchrun commands only.
  --skip-sync           Do not copy from S3 before launching.
  --remote-root PATH    Huanxin project root. Default: /vllm-workspace/quantum-gpt
  --s3-root REMOTE      Rclone S3 source. Default: active INER project root.
  --model-name PATH     Qwen3.6-35B-A3B model path. Default: /root/work/filestorage/Qwen3.6-35B-A3B
  --output-dir PATH     Training output directory under the project root.
  --max-steps N         Default: 40.
  --num-epochs N        Default: 3, enough for 40 steps with 8-way DDP.
  --nproc-per-node N    Override all-visible-NPU detection.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --skip-sync)
      SKIP_SYNC=1
      shift
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
      shift 2
      ;;
    --s3-root)
      S3_ROOT="${2:-}"
      shift 2
      ;;
    --model-name)
      MODEL_NAME="${2:-}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --max-steps)
      MAX_STEPS="${2:-}"
      shift 2
      ;;
    --num-epochs)
      NUM_EPOCHS="${2:-}"
      shift 2
      ;;
    --nproc-per-node)
      export HUANXIN_DISTILL_NPROC_PER_NODE="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_non_empty() {
  local name="$1"
  local value="$2"
  if [[ -z "$value" ]]; then
    echo "$name must not be empty" >&2
    exit 2
  fi
}

require_non_empty REMOTE_ROOT "$REMOTE_ROOT"
require_non_empty S3_ROOT "$S3_ROOT"
require_non_empty MODEL_NAME "$MODEL_NAME"

ensure_rclone() {
  if command -v rclone >/dev/null 2>&1; then
    command -v rclone
    return 0
  fi
  if [[ -x "$REMOTE_ROOT/tools/preseed/rclone-linux-arm64" ]]; then
    echo "$REMOTE_ROOT/tools/preseed/rclone-linux-arm64"
    return 0
  fi
  if [[ -x tools/preseed/rclone-linux-arm64 ]]; then
    echo "tools/preseed/rclone-linux-arm64"
    return 0
  fi
  local install_dir="${TMPDIR:-/tmp}/huanxin-rclone-bin"
  local zip_path="${TMPDIR:-/tmp}/rclone-current-linux-arm64.zip"
  mkdir -p "$install_dir"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://downloads.rclone.org/rclone-current-linux-arm64.zip -o "$zip_path"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$zip_path" https://downloads.rclone.org/rclone-current-linux-arm64.zip
  fi
  if [[ -s "$zip_path" ]]; then
    python3 - <<'PY' "$zip_path" "$install_dir"
import pathlib
import shutil
import sys
import zipfile

zip_path = pathlib.Path(sys.argv[1])
install_dir = pathlib.Path(sys.argv[2])
with zipfile.ZipFile(zip_path) as archive:
    members = [name for name in archive.namelist() if name.endswith('/rclone')]
    if not members:
        raise SystemExit('rclone binary missing from archive')
    with archive.open(members[0]) as src, (install_dir / 'rclone').open('wb') as dst:
        shutil.copyfileobj(src, dst)
(install_dir / 'rclone').chmod(0o755)
PY
    if [[ -x "$install_dir/rclone" ]]; then
      echo "$install_dir/rclone"
      return 0
    fi
  fi
  echo "rclone not found; install rclone or set PATH before running this script." >&2
  return 1
}

write_rclone_config() {
  if [[ -n "${INER_RCLONE_CONFIG:-}" ]]; then
    test -f "$INER_RCLONE_CONFIG"
    echo "$INER_RCLONE_CONFIG"
    return 0
  fi
  if [[ -z "${INER_SECRET_ACCESS_KEY:-}" ]]; then
    echo "INER_SECRET_ACCESS_KEY is required when INER_RCLONE_CONFIG is not set." >&2
    return 2
  fi
  local config_path="${TMPDIR:-/tmp}/iner-rclone-distill.conf"
  umask 077
  cat > "$config_path" <<EOF
[iner]
type = s3
provider = Other
access_key_id = $S3_ACCESS_KEY_ID
secret_access_key = $INER_SECRET_ACCESS_KEY
endpoint = $S3_ENDPOINT
acl = private
force_path_style = true
EOF
  echo "$config_path"
}

detect_npu_count() {
  if [[ -n "${HUANXIN_DISTILL_NPROC_PER_NODE:-}" ]]; then
    echo "$HUANXIN_DISTILL_NPROC_PER_NODE"
    return 0
  fi
  if [[ -n "${ASCEND_RT_VISIBLE_DEVICES:-}" ]]; then
    python3 - <<'PY' "$ASCEND_RT_VISIBLE_DEVICES"
import sys
visible = [part.strip() for part in sys.argv[1].split(',') if part.strip() and part.strip().lower() != 'none']
print(max(1, len(visible)))
PY
    return 0
  fi
  python3 - <<'PY' 2>/dev/null && return 0
try:
    import torch
    import torch_npu  # noqa: F401
    print(max(1, int(torch.npu.device_count())))
except Exception:
    raise SystemExit(1)
PY
  if command -v npu-smi >/dev/null 2>&1; then
    npu-smi info | awk '/^[[:space:]]*[0-9]+[[:space:]]+[0-9]+/ {ids[$1]=1} END {count=0; for (id in ids) count++; if (count < 1) count=1; print count}'
    return 0
  fi
  echo 1
}

comma_range() {
  python3 - <<'PY' "$1"
import sys
n = max(1, int(sys.argv[1]))
print(','.join(str(i) for i in range(n)))
PY
}

TRAIN_FILE="$SPLIT_DIR/train_chatml.jsonl"
EVAL_FILE="$SPLIT_DIR/eval_chatml.jsonl"
NPROC_PER_NODE="$(detect_npu_count)"
if [[ -z "${ASCEND_RT_VISIBLE_DEVICES:-}" ]]; then
  export ASCEND_RT_VISIBLE_DEVICES="$(comma_range "$NPROC_PER_NODE")"
fi
export PYTORCH_NPU_ALLOC_CONF="${PYTORCH_NPU_ALLOC_CONF:-max_split_size_mb:256}"
export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"

SYNC_CMD=(rclone copy "$S3_ROOT" "$REMOTE_ROOT" --s3-no-check-bucket --fast-list --transfers 8 --checkers 16 --exclude '.git/**' --exclude '.venv/**' --exclude '.local-python/**' --exclude 'models/**' --exclude 'outputs/**' --exclude 'logs/**' --exclude 'browser-automation/profile/**' --exclude 'browser-automation/profile.last-known-good/**')
TRAIN_CMD=(torchrun --nproc_per_node="$NPROC_PER_NODE" --master_port="$MASTER_PORT" training/qwen_sft_peft.py --model-name "$MODEL_NAME" --train-file "$TRAIN_FILE" --eval-file "$EVAL_FILE" --output-dir "$OUTPUT_DIR" --device npu --max-length "$MAX_LENGTH" --max-steps "$MAX_STEPS" --num-epochs "$NUM_EPOCHS" --per-device-batch-size 1 --gradient-accumulation-steps 1 --learning-rate "$LEARNING_RATE" --eval-steps "$EVAL_STEPS" --log-steps "$LOG_STEPS" --lora-rank "$LORA_RANK" --lora-alpha "$LORA_ALPHA" --lora-dropout "$LORA_DROPOUT" --target-modules $TARGET_MODULES --train-on-completions-only --gradient-checkpointing --train-layernorm --max-trainable-parameters "$MAX_TRAINABLE_PARAMETERS" --min-trainable-parameters "$MIN_TRAINABLE_PARAMETERS")

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf 'remote_root=%q\n' "$REMOTE_ROOT"
  printf 's3_root=%q\n' "$S3_ROOT"
  printf 'nproc_per_node=%q\n' "$NPROC_PER_NODE"
  printf 'num_epochs=%q\n' "$NUM_EPOCHS"
  printf 'max_trainable_parameters=%q\n' "$MAX_TRAINABLE_PARAMETERS"
  printf 'min_trainable_parameters=%q\n' "$MIN_TRAINABLE_PARAMETERS"
  printf 'ascend_rt_visible_devices=%q\n' "$ASCEND_RT_VISIBLE_DEVICES"
  printf 'sync_command='
  printf '%q ' "${SYNC_CMD[@]}"
  printf '\ntrain_command='
  printf '%q ' "${TRAIN_CMD[@]}"
  printf '\n'
  exit 0
fi

RCLONE_BIN="$(ensure_rclone)"
RCLONE_CONFIG="$(write_rclone_config)"
mkdir -p "$REMOTE_ROOT"

if [[ "$SKIP_SYNC" -eq 0 ]]; then
  "$RCLONE_BIN" "${SYNC_CMD[@]:1}" --config "$RCLONE_CONFIG"
fi

cd "$REMOTE_ROOT"
test -s training/qwen_sft_peft.py
test -s scripts/preflight_qwen36_ascend_hf_training.py
test -s "$TRAIN_FILE"
test -s "$EVAL_FILE"
test -d "$MODEL_NAME"
mkdir -p logs reports
python3 scripts/preflight_qwen36_ascend_hf_training.py --model-name "$MODEL_NAME" --device npu --json
echo "__HUANXIN_DISTILL_ALL_NPU_START__ nproc_per_node=$NPROC_PER_NODE visible=$ASCEND_RT_VISIBLE_DEVICES"
"${TRAIN_CMD[@]}" 2>&1 | tee "$LOG_PATH"
test -f "$OUTPUT_DIR/metrics.json"
test -d "$OUTPUT_DIR/adapter"
cp "$OUTPUT_DIR/metrics.json" reports/huanxin_distillation_lora_allnpu_metrics.json
echo "__HUANXIN_DISTILL_ALL_NPU_DONE__ $OUTPUT_DIR"
