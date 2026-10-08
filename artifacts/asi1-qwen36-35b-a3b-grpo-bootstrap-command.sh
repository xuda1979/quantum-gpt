set -euo pipefail
mkdir -p /tmp /workspace/quantum-gpt
python3 - <<'PY'
import base64, pathlib
path = pathlib.Path('/tmp/iner-rclone.conf')
raise SystemExit('Use scripts/render_asi1_grpo_huanxin_bootstrap_command.py locally to generate this command; embedded config is intentionally not stored.')
path.chmod(0o600)
PY
export HUANXIN_GRPO_REMOTE_ROOT=/workspace/quantum-gpt
export HUANXIN_GRPO_S3_ROOT=iner:jtdlp-21b4208dde424e96b159362ef49c9c96/software/quantum-gpt
export HUANXIN_GRPO_RCLONE_CONFIG=/tmp/iner-rclone.conf
export HUANXIN_GRPO_MODEL_NAME=/root/work/filestorage/Qwen3.6-35B-A3B
export HUANXIN_GRPO_FULL_STEPS=200000
export HUANXIN_GRPO_CHECKPOINT_INTERVAL_SECONDS=3600
export HUANXIN_GRPO_LORA_RANK=64
export HUANXIN_GRPO_LORA_ALPHA=128
export HUANXIN_GRPO_MIN_TRAINABLE_PARAMETERS=200000000
export HUANXIN_GRPO_MAX_TRAINABLE_PARAMETERS=1000000000
export HUANXIN_GRPO_TARGET_MODULES='q_proj k_proj v_proj o_proj gate_proj up_proj down_proj'
export HUANXIN_GRPO_TRAIN_LAYER_NORM=1
export HUANXIN_GRPO_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export HUANXIN_GRPO_NPROC_PER_NODE=8
cd /workspace/quantum-gpt
bash scripts/huanxin_pull_and_start_asi1_grpo.sh
