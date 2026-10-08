#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ENV_NAME="${ASI2_DISTILL_ENV:-ASI2}"
REMOTE_ROOT="${ASI2_DISTILL_REMOTE_ROOT:-/vllm-workspace/quantum-gpt}"
TASK_NAME="${ASI2_DISTILL_TASK_NAME:-asi2-dlora-allnpu-0604}"
IMAGE_NAME="${ASI2_DISTILL_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI2_DISTILL_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI2_DISTILL_RESOURCE_GROUP_TYPE:-公共资源组}"
TASK_PRIORITY="${ASI2_DISTILL_TASK_PRIORITY:-中}"
INSTANCE_COUNT="${ASI2_DISTILL_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI2_DISTILL_ACCELERATOR_CARDS:-8}"
CPU_CORES="${ASI2_DISTILL_CPU_CORES:-160}"
MEMORY_GB="${ASI2_DISTILL_MEMORY_GB:-1920}"
WAIT_MS="${ASI2_DISTILL_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI2_DISTILL_ARTIFACT_STEM:-huanxin-submit-task-run-asi2-distillation-lora-sft}"
TRAIN_DEV_URL="${ASI2_DISTILL_URL:-}"

MODEL_NAME="${ASI2_DISTILL_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B}"
SPLIT_DIR="${ASI2_DISTILL_SPLIT_DIR:-data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100}"
NPROC_PER_NODE="${ASI2_DISTILL_NPROC_PER_NODE:-$ACCELERATOR_CARDS}"
OUTPUT_DIR="${ASI2_DISTILL_OUTPUT_DIR:-outputs/qwen36-35b-a3b-distill-uniform-lora-asi2-allnpu-r64-broad-ln-l512-s40-100hq}"
LOG_PATH="${ASI2_DISTILL_LOG_PATH:-logs/asi2_distillation_uniform_lora_35b_allnpu_r64_broad_ln_l512_s40_100hq.log}"
MAX_LENGTH="${ASI2_DISTILL_MAX_LENGTH:-512}"
MAX_STEPS="${ASI2_DISTILL_MAX_STEPS:-40}"
NUM_EPOCHS="${ASI2_DISTILL_NUM_EPOCHS:-3}"
LORA_RANK="${ASI2_DISTILL_LORA_RANK:-64}"
LORA_ALPHA="${ASI2_DISTILL_LORA_ALPHA:-128}"
LORA_DROPOUT="${ASI2_DISTILL_LORA_DROPOUT:-0.0}"
MIN_TRAINABLE_PARAMETERS="${ASI2_DISTILL_MIN_TRAINABLE_PARAMETERS:-200000000}"
MAX_TRAINABLE_PARAMETERS="${ASI2_DISTILL_MAX_TRAINABLE_PARAMETERS:-1000000000}"
LEARNING_RATE="${ASI2_DISTILL_LEARNING_RATE:-5e-5}"
EVAL_STEPS="${ASI2_DISTILL_EVAL_STEPS:-10}"
LOG_STEPS="${ASI2_DISTILL_LOG_STEPS:-5}"
TARGET_MODULES="${ASI2_DISTILL_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
EMBED_PATCHES="${ASI2_DISTILL_EMBED_PATCHES:-0}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi2_distillation_lora_sft_task.sh [--submit] [options]

Submits or dry-renders an ASI2 Huanxin training task for the verified
Qwen3.6-35B-A3B hard-distillation uniform-LoRA SFT path. Defaults to a compact command
that uses the already-materialized remote workspace; pass --embed-patches only
when remote code freshness is more important than create-payload size.
EOF
}

default_train_dev_url() {
  "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$ENV_NAME" --field train_dev_url 2>/dev/null \
    || python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$ENV_NAME" --field train_dev_url
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  python3 - <<'PY' "$ROOT_DIR" "$REMOTE_ROOT" "$MODEL_NAME" "$SPLIT_DIR" "$OUTPUT_DIR" "$LOG_PATH" "$MAX_STEPS" "$NUM_EPOCHS" "$NPROC_PER_NODE"
import base64
import json
import shlex
import sys
from pathlib import Path

root_dir, remote_root, model_name, split_dir, output_dir, log_path, max_steps, num_epochs, nproc_per_node = sys.argv[1:]
root = Path(root_dir)

def read_secret(root_dir: Path) -> str:
    secret = ""
    skill_file = root_dir / "skills" / "iner-s3-transfer" / "SKILL.md"
    if skill_file.exists():
        prefix = "- Secret access key: `"
        for line in skill_file.read_text(encoding="utf-8").splitlines():
            if line.startswith(prefix) and line.endswith("`"):
                secret = line[len(prefix):-1]
                break
    if not secret:
        raise SystemExit("INER_SECRET_ACCESS_KEY is required or must be present in skills/iner-s3-transfer/SKILL.md")
    return secret

secret = read_secret(root)
s3_root = "iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt"
env_assignments = {
    "INER_SECRET_ACCESS_KEY": secret,
    "HUANXIN_DISTILL_REMOTE_ROOT": remote_root,
    "HUANXIN_DISTILL_S3_ROOT": s3_root,
    "HUANXIN_DISTILL_MODEL_NAME": model_name,
    "HUANXIN_DISTILL_SPLIT_DIR": split_dir,
    "HUANXIN_DISTILL_OUTPUT_DIR": output_dir,
    "HUANXIN_DISTILL_LOG_PATH": log_path,
    "HUANXIN_DISTILL_MAX_STEPS": max_steps,
    "HUANXIN_DISTILL_NUM_EPOCHS": num_epochs,
    "HUANXIN_DISTILL_NPROC_PER_NODE": nproc_per_node,
}
assignments = " ".join(
    f"{key}={shlex.quote(str(value))}"
    for key, value in env_assignments.items()
)
remote_script_body = "\n".join([
    "set -euo pipefail",
    "echo __ASI2_DISTILL_LORA_TASK_START__",
    "pwd",
    "python3 --version",
    f"mkdir -p {remote_root}",
    "python3 -c \"import pathlib; import base64; pathlib.Path('/tmp/iner-rclone-distill.conf').write_bytes(base64.b64decode('W2luZXJdCnR5cGUgPSBzMwpwcm92aWRlciA9IE90aGVyCmFjY2Vzc19rZXlfaWQgPSBPWEY1YXI0eQpzZWNyZXRfYWNjZXNzX2tleSA9IHRTZDJqRDFlUngKZW5kcG9pbnQgPSBodHRwczovL2luZXIuYWlodWFueGluLmNuCmFjbCA9IHByaXZhdGUKZm9yY2VfcGF0aF9zdHlsZSA9IHRydWUK'))\"",
    "chmod 600 /tmp/iner-rclone-distill.conf",
    "if command -v rclone; then export BOOTSTRAP_RCLONE=rclone; elif [ -f /root/work/filestorage/rclone-bin ]; then cp /root/work/filestorage/rclone-bin /tmp/rclone ; chmod +x /tmp/rclone ; export BOOTSTRAP_RCLONE=/tmp/rclone; elif [ -f /vllm-workspace/quantum-gpt/tools/preseed/rclone-linux-arm64 ]; then cp /vllm-workspace/quantum-gpt/tools/preseed/rclone-linux-arm64 /tmp/rclone ; chmod +x /tmp/rclone ; export BOOTSTRAP_RCLONE=/tmp/rclone; else echo 'Offline fallback: No rclone found.' ; exit 1; fi",
    f"if [ -d /root/work/filestorage/quantum-gpt ]; then echo __ASI2_SYNC_MODE_NAS__ ; echo \"NAS copy detected - syncing offline...\" ; command -v tar ; test -d /root/work/filestorage/quantum-gpt ; test -d /root/work/filestorage/Qwen3.6-35B-A3B ; mkdir -p {remote_root} ; echo __ASI2_SYNC_NAS_BEGIN__ ; ( cd /root/work/filestorage/quantum-gpt && tar -cf - --exclude=.git --exclude=.venv --exclude=.local-python --exclude=models --exclude=outputs --exclude=logs --exclude=browser-automation/profile --exclude=browser-automation/profile.last-known-good . ) | ( cd {remote_root} && tar -xf - ) ; echo __ASI2_SYNC_NAS_DONE__ ; else echo __ASI2_SYNC_MODE_S3__ ; \"$BOOTSTRAP_RCLONE\" copy {s3_root} {remote_root} --config /tmp/iner-rclone-distill.conf --s3-no-check-bucket --fast-list --transfers 8 --checkers 16 --exclude '.git/**' --exclude '.venv/**' --exclude '.local-python/**' --exclude 'models/**' --exclude 'outputs/**' --exclude 'logs/**' --exclude 'browser-automation/profile/**' --exclude 'browser-automation/profile.last-known-good/**' || [ $? -eq 6 ] ; echo __ASI2_SYNC_S3_DONE__ ; fi",
    f"cd {remote_root}",
    "test -d /root/work/filestorage/Qwen3.6-35B-A3B",
    "test -s training/qwen_sft_peft.py",
    "test -s data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_chatml.jsonl",
    "python3 - <<'PYSLICE'",
    "import json",
    "from pathlib import Path",
    "split_dir = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100')",
    "train_file = split_dir / 'train_chatml.jsonl'",
    "eval_file = split_dir / 'eval_chatml.jsonl'",
    "if not train_file.exists() or not eval_file.exists():",
    "    src = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_chatml.jsonl')",
    "    rows = [json.loads(line) for line in src.read_text(encoding='utf-8').splitlines() if line.strip()]",
    "    assert len(rows) >= 120, len(rows)",
    "    split_dir.mkdir(parents=True, exist_ok=True)",
    "    for path, subset in ((train_file, rows[:100]), (eval_file, rows[100:120])):",
    "        with path.open('w', encoding='utf-8') as handle:",
    "            for row in subset:",
    "                handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + '\\n')",
    "    manifest = split_dir / 'manifest.json'",
    "    manifest.write_text(json.dumps({'ok': True, 'source': str(src), 'train_rows': 100, 'eval_rows': 20}, indent=2, sort_keys=True) + '\\n', encoding='utf-8')",
    "print(json.dumps({'ok': True, 'train_exists': train_file.exists(), 'eval_exists': eval_file.exists()}, sort_keys=True))",
    "PYSLICE",
    "test -s data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100/train_chatml.jsonl",
    "test -s data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100/eval_chatml.jsonl",
    "python3 - <<'PYDATA'",
    "import json",
    "from pathlib import Path",
    "train = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100/train_chatml.jsonl')",
    "evalf = Path('data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100/eval_chatml.jsonl')",
    "train_rows = sum(1 for line in train.read_text(encoding='utf-8').splitlines() if line.strip())",
    "eval_rows = sum(1 for line in evalf.read_text(encoding='utf-8').splitlines() if line.strip())",
    "assert train_rows == 100, train_rows",
    "assert eval_rows == 20, eval_rows",
    "print(json.dumps({'ok': True, 'train_rows': train_rows, 'eval_rows': eval_rows}, sort_keys=True))",
    "PYDATA",
    f"rm -rf {output_dir}",
    "mkdir -p logs reports",
    f"python3 scripts/preflight_qwen36_ascend_hf_training.py --model-name {shlex.quote(model_name)} --device npu --json",
    "export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
    "export TOKENIZERS_PARALLELISM=false",
    "echo __ASI2_DISTILL_LORA_BEFORE_TORCHRUN__",
    f"torchrun --nproc_per_node={nproc_per_node} training/qwen_sft_peft.py --model-name {shlex.quote(model_name)} --train-file data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100/train_chatml.jsonl --eval-file data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_100/eval_chatml.jsonl --output-dir {shlex.quote(output_dir)} --device npu --max-length 512 --max-steps {shlex.quote(max_steps)} --num-epochs {shlex.quote(num_epochs)} --per-device-batch-size 1 --gradient-accumulation-steps 1 --learning-rate 5e-5 --eval-steps 10 --log-steps 5 --lora-rank 64 --lora-alpha 128 --lora-dropout 0.0 --target-modules q_proj k_proj v_proj o_proj gate_proj up_proj down_proj --train-on-completions-only --gradient-checkpointing --train-layernorm --min-trainable-parameters 200000000 --max-trainable-parameters 1000000000 | tee {shlex.quote(log_path)}",
    "echo __ASI2_DISTILL_LORA_AFTER_TORCHRUN__",
    f"test -f {shlex.quote(output_dir)}/metrics.json",
    f"test -d {shlex.quote(output_dir)}/adapter",
    f"cp {shlex.quote(output_dir)}/metrics.json reports/asi2_distillation_lora_sft_task_metrics.json",
    "echo __ASI2_DISTILL_LORA_SUMMARY__",
    "echo __ASI2_DISTILL_LORA_TASK_DONE__",
])
payload_b64 = base64.b64encode(remote_script_body.encode("utf-8")).decode("ascii")
execution_command = (
    "python3 -c "
    + shlex.quote(
        "b=__import__('base64');"
        "p=__import__('pathlib').Path('/tmp/asi2_distill_lora_run_full.sh');"
        f"p.write_bytes(b.b64decode('{payload_b64}'));"
        "p.chmod(0o700);"
        "s=__import__('subprocess');"
        "raise SystemExit(s.run(['bash',str(p)]).returncode)"
    )
)
print(json.dumps({
    "remote_root": remote_root,
    "output_dir": output_dir,
    "log_path": log_path,
    "job_name": "asi2-distillation-lora-sft",
    "remote_command": execution_command,
    "execution_command": execution_command,
    "remote_script_body": remote_script_body,
    "embed_patches": False,
    "single_line_execution": True,
    "nproc_per_node": nproc_per_node,
    "num_epochs": num_epochs,
    "uniform_lora_policy": "all matching transformer layers, shared rank, attention plus mlp projection targets",
    "train_layernorm": True,
    "min_trainable_parameters": 200000000,
    "max_trainable_parameters": 1000000000,
    "remote_script_path": None,
    "remote_b64_path": None,
}, indent=2))
PY
}

if [[ "${1:-}" == "--dry-run" && "${2:-}" == "__launch-spec" ]]; then
  render_launch_spec
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --submit)
      SUBMIT=1
      shift
      ;;
    --dry-run)
      PRINT_ONLY=1
      shift
      ;;
    --task-name)
      TASK_NAME="${2:-}"
      shift 2
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --log-path)
      LOG_PATH="${2:-}"
      shift 2
      ;;
    --nproc-per-node)
      NPROC_PER_NODE="${2:-}"
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
    --embed-patches)
      EMBED_PATCHES=1
      shift
      ;;
    --artifact-stem)
      ARTIFACT_STEM="${2:-}"
      shift 2
      ;;
    --wait-ms)
      WAIT_MS="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

export ASI2_DISTILL_REMOTE_ROOT="$REMOTE_ROOT"
export ASI2_DISTILL_MODEL_NAME="$MODEL_NAME"
export ASI2_DISTILL_SPLIT_DIR="$SPLIT_DIR"
export ASI2_DISTILL_NPROC_PER_NODE="$NPROC_PER_NODE"
export ASI2_DISTILL_OUTPUT_DIR="$OUTPUT_DIR"
export ASI2_DISTILL_LOG_PATH="$LOG_PATH"
export ASI2_DISTILL_MAX_STEPS="$MAX_STEPS"
export ASI2_DISTILL_NUM_EPOCHS="$NUM_EPOCHS"
export ASI2_DISTILL_LORA_RANK="$LORA_RANK"
export ASI2_DISTILL_LORA_ALPHA="$LORA_ALPHA"
export ASI2_DISTILL_LORA_DROPOUT="$LORA_DROPOUT"
export ASI2_DISTILL_MIN_TRAINABLE_PARAMETERS="$MIN_TRAINABLE_PARAMETERS"
export ASI2_DISTILL_MAX_TRAINABLE_PARAMETERS="$MAX_TRAINABLE_PARAMETERS"
export ASI2_DISTILL_TARGET_MODULES="$TARGET_MODULES"

CMD=(
  node
  "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
  --url "$TRAIN_DEV_URL"
  --wait-ms "$WAIT_MS"
  --task-name "$TASK_NAME"
  --image-name "$IMAGE_NAME"
  --resource-group "$RESOURCE_GROUP"
  --resource-group-type "$RESOURCE_GROUP_TYPE"
  --priority "$TASK_PRIORITY"
  --instance-count "$INSTANCE_COUNT"
  --accelerator-cards "$ACCELERATOR_CARDS"
  --cpu-cores "$CPU_CORES"
  --memory-gb "$MEMORY_GB"
  --remote-root "$REMOTE_ROOT"
  --launcher-script "$ROOT_DIR/scripts/submit_asi2_distillation_lora_sft_task.sh"
  --launcher-arg "__launch-spec"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
  --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
)

if [[ "$SUBMIT" == "1" ]]; then
  CMD+=(--submit)
fi

if [[ "$PRINT_ONLY" == "1" ]]; then
  shell_quote "${CMD[@]}"
  exit 0
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
