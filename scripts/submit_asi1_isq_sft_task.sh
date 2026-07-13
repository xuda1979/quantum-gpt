#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

TASK_NAME="${ASI1_ISQ_SFT_TASK_NAME:-asi1-q36-35b-verified10k-sft}"
IMAGE_NAME="${ASI1_ISQ_SFT_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_ISQ_SFT_RESOURCE_GROUP:-研究院未来院专属资源组}"
RESOURCE_GROUP_TYPE="${ASI1_ISQ_SFT_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_ISQ_SFT_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_ISQ_SFT_ACCELERATOR_CARDS:-5}"
CPU_CORES="${ASI1_ISQ_SFT_CPU_CORES:-100}"
MEMORY_GB="${ASI1_ISQ_SFT_MEMORY_GB:-1200}"
WAIT_MS="${ASI1_ISQ_SFT_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_ISQ_SFT_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-verified10k-sft}"
TRAIN_DEV_URL="${ASI1_ISQ_SFT_URL:-}"
REMOTE_ROOT="${ASI1_ISQ_SFT_REMOTE_ROOT:-/workspace}"
MODEL_NAME="${ASI1_ISQ_SFT_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B-W8A8}"
SPLIT_DIR="${ASI1_ISQ_SFT_SPLIT_DIR:-data/generated/quantum_finetune_verified_chat_sft}"
TRAIN_FILE="${ASI1_ISQ_SFT_TRAIN_FILE:-data/generated/quantum_finetune_verified_chat_sft/train_chatml.jsonl}"
EVAL_FILE="${ASI1_ISQ_SFT_EVAL_FILE:-data/generated/quantum_finetune_verified_chat_sft/eval_chatml.jsonl}"
TIMESTAMP="${ASI1_ISQ_SFT_TIMESTAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT_DIR="${ASI1_ISQ_SFT_OUTPUT_DIR:-outputs/qwen36-35b-a3b-verified10k-sft-asi1-${TIMESTAMP}}"
LOG_PATH="${ASI1_ISQ_SFT_LOG_PATH:-logs/asi1_verified10k_sft_${TIMESTAMP}.log}"
NPROC_PER_NODE="${ASI1_ISQ_SFT_NPROC_PER_NODE:-5}"
VISIBLE_DEVICES="${ASI1_ISQ_SFT_VISIBLE_DEVICES:-0,1,2,3,4}"
MAX_LENGTH="${ASI1_ISQ_SFT_MAX_LENGTH:-512}"
MAX_STEPS="${ASI1_ISQ_SFT_MAX_STEPS:-400}"
NUM_EPOCHS="${ASI1_ISQ_SFT_NUM_EPOCHS:-3}"
PER_DEVICE_BATCH_SIZE="${ASI1_ISQ_SFT_PER_DEVICE_BATCH_SIZE:-1}"
GRAD_ACCUM="${ASI1_ISQ_SFT_GRAD_ACCUM:-4}"
LEARNING_RATE="${ASI1_ISQ_SFT_LEARNING_RATE:-2e-5}"
EVAL_STEPS="${ASI1_ISQ_SFT_EVAL_STEPS:-25}"
LOG_STEPS="${ASI1_ISQ_SFT_LOG_STEPS:-1}"
LORA_RANK="${ASI1_ISQ_SFT_LORA_RANK:-64}"
LORA_ALPHA="${ASI1_ISQ_SFT_LORA_ALPHA:-128}"
LORA_DROPOUT="${ASI1_ISQ_SFT_LORA_DROPOUT:-0.0}"
LORA_BACKEND="${ASI1_ISQ_SFT_LORA_BACKEND:-native}"
TARGET_MODULES="${ASI1_ISQ_SFT_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
TARGET_MODULE_REGEX="${ASI1_ISQ_SFT_TARGET_MODULE_REGEX:-}"
TRAINABLE_PARAM_REGEX="${ASI1_ISQ_SFT_TRAINABLE_PARAM_REGEX:-}"
FREEZE_PARAM_REGEX="${ASI1_ISQ_SFT_FREEZE_PARAM_REGEX:-}"
EXTRA_TRAIN_ARGS="${ASI1_ISQ_SFT_EXTRA_TRAIN_ARGS:-}"
TRAIN_LAYERNORM="${ASI1_ISQ_SFT_TRAIN_LAYERNORM:-1}"
MIN_TRAINABLE_PARAMETERS="${ASI1_ISQ_SFT_MIN_TRAINABLE_PARAMETERS:-200000000}"
MAX_TRAINABLE_PARAMETERS="${ASI1_ISQ_SFT_MAX_TRAINABLE_PARAMETERS:-1000000000}"
EMBED_LOCAL_FILES="${ASI1_ISQ_SFT_EMBED_LOCAL_FILES:-0}"
EMBED_CODE_FILES="${ASI1_ISQ_SFT_EMBED_CODE_FILES:-1}"
EMBED_DATA_FILES="${ASI1_ISQ_SFT_EMBED_DATA_FILES:-1}"
EMBED_RUNTIME_FILES="${ASI1_ISQ_SFT_EMBED_RUNTIME_FILES:-1}"
EMBED_CHUNK_BYTES="${ASI1_ISQ_SFT_EMBED_CHUNK_BYTES:-60000}"
SYNC_CODE_FILES="${ASI1_ISQ_SFT_SYNC_CODE_FILES:-1}"
SYNC_SCRIPT_FILES="${ASI1_ISQ_SFT_SYNC_SCRIPT_FILES:-1}"
SYNC_DATA_FILES="${ASI1_ISQ_SFT_SYNC_DATA_FILES:-1}"
INSTALL_DEPS="${ASI1_ISQ_SFT_INSTALL_DEPS:-0}"
PIP_INSTALL_CMD="${ASI1_ISQ_SFT_PIP_INSTALL_CMD:-}"
SKIP_PREFLIGHT="${ASI1_ISQ_SFT_SKIP_PREFLIGHT:-0}"
SKIP_SYNC="${ASI1_ISQ_SFT_SKIP_SYNC:-0}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_verified10k_sft_task.sh [--submit] [--dry-run]
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  source "$ROOT_DIR/scripts/iner_s3_env.sh"
    python3 - <<'PY' "$ROOT_DIR" "$REMOTE_ROOT" "$MODEL_NAME" "$SPLIT_DIR" "$TRAIN_FILE" "$EVAL_FILE" "$OUTPUT_DIR" "$LOG_PATH" "$NPROC_PER_NODE" "$VISIBLE_DEVICES" "$MAX_LENGTH" "$MAX_STEPS" "$NUM_EPOCHS" "$PER_DEVICE_BATCH_SIZE" "$GRAD_ACCUM" "$LEARNING_RATE" "$EVAL_STEPS" "$LOG_STEPS" "$LORA_RANK" "$LORA_ALPHA" "$LORA_DROPOUT" "$LORA_BACKEND" "$TARGET_MODULES" "$TARGET_MODULE_REGEX" "$TRAINABLE_PARAM_REGEX" "$FREEZE_PARAM_REGEX" "$EXTRA_TRAIN_ARGS" "$TRAIN_LAYERNORM" "$MIN_TRAINABLE_PARAMETERS" "$MAX_TRAINABLE_PARAMETERS" "$INER_S3_ROOT" "$INER_S3_ENDPOINT" "$INER_ACCESS_KEY_ID" "$INER_SECRET_ACCESS_KEY" "$EMBED_LOCAL_FILES" "$EMBED_CODE_FILES" "$EMBED_DATA_FILES" "$EMBED_RUNTIME_FILES" "$EMBED_CHUNK_BYTES" "$SYNC_CODE_FILES" "$SYNC_SCRIPT_FILES" "$SYNC_DATA_FILES" "$INSTALL_DEPS" "$PIP_INSTALL_CMD" "$SKIP_PREFLIGHT" "$SKIP_SYNC"
import base64
import gzip
import json
import pathlib
import shlex
import sys

(
    root_dir,
    remote_root,
    model_name,
    split_dir,
    train_file,
    eval_file,
    output_dir,
    log_path,
    nproc,
    visible_devices,
    max_length,
    max_steps,
    num_epochs,
    per_device_batch_size,
    grad_accum,
    learning_rate,
    eval_steps,
    log_steps,
    lora_rank,
    lora_alpha,
    lora_dropout,
    lora_backend,
    target_modules,
    target_module_regex,
    trainable_param_regex,
    freeze_param_regex,
    extra_train_args,
    train_layernorm,
    min_trainable,
    max_trainable,
    s3_root,
    endpoint,
    access_key,
    secret,
    embed_local_files,
    embed_code_files,
    embed_data_files,
    embed_runtime_files,
    embed_chunk_bytes,
    sync_code_files,
    sync_script_files,
    sync_data_files,
    install_deps,
    pip_install_cmd,
    skip_preflight,
    skip_sync,
) = sys.argv[1:]

root_path = pathlib.Path(root_dir)
embed_chunk_bytes = int(embed_chunk_bytes)

def python_exec_line(source):
    return "python3 -c " + shlex.quote("exec(" + repr(source) + ")")

def append_embedded_file(commands, local_rel, remote_rel, tag):
    local_path = root_path / local_rel
    if not local_path.is_file():
        raise SystemExit(f"missing local file for embedding: {local_path}")
    encoded = base64.b64encode(gzip.compress(local_path.read_bytes(), compresslevel=9)).decode()
    remote_path = f"{remote_root.rstrip('/')}/{remote_rel}"
    b64_path = f"/tmp/asi1_verified10k_sft_{tag}.gz.b64"
    commands.extend([
        f"echo __ASI1_ISQ_SFT_EMBED_{tag.upper()}_START__",
        f"mkdir -p {shlex.quote(str(pathlib.PurePosixPath(remote_path).parent))}",
        python_exec_line("import pathlib\n" f"p=pathlib.Path({b64_path!r})\n" "p.unlink(missing_ok=True)\n"),
    ])
    for index in range(0, len(encoded), embed_chunk_bytes):
        chunk = encoded[index:index+embed_chunk_bytes]
        commands.append(
            python_exec_line(
                "import pathlib\n"
                f"p=pathlib.Path({b64_path!r})\n"
                "old=p.read_text() if p.exists() else ''\n"
                f"p.write_text(old+{chunk!r})\n"
            )
        )
    commands.extend([
        python_exec_line(
            "import base64\n"
            "import gzip\n"
            "import pathlib\n"
            f"src=pathlib.Path({b64_path!r})\n"
            f"dst=pathlib.Path({remote_path!r})\n"
            "dst.parent.mkdir(parents=True, exist_ok=True)\n"
            "dst.write_bytes(gzip.decompress(base64.b64decode(src.read_text())))\n"
        ),
        f"test -s {shlex.quote(remote_path)}",
        f"echo __ASI1_ISQ_SFT_EMBED_{tag.upper()}_DONE__",
    ])

def append_embedded_tree(commands, local_rel, remote_rel, tag):
    local_path = root_path / local_rel
    if not local_path.is_dir():
        raise SystemExit(f"missing local directory for embedding: {local_path}")
    for file_path in sorted(path for path in local_path.rglob("*") if path.is_file() and path.suffix == ".py"):
        rel = file_path.relative_to(root_path).as_posix()
        remote_file = f"{remote_rel.rstrip('/')}/{file_path.relative_to(local_path).as_posix()}"
        safe_tag = tag + "_" + file_path.relative_to(local_path).as_posix().replace("/", "_").replace(".", "_")
        append_embedded_file(commands, rel, remote_file, safe_tag)

target_modules_parts = [shlex.quote(part) for part in target_modules.split()]
target_module_regex_parts = [shlex.quote(part) for part in shlex.split(target_module_regex)]
trainable_param_regex_parts = [shlex.quote(part) for part in shlex.split(trainable_param_regex)]
freeze_param_regex_parts = [shlex.quote(part) for part in shlex.split(freeze_param_regex)]
extra_train_args_parts = [shlex.quote(part) for part in shlex.split(extra_train_args)]
trainer = [
    "python3",
    "training/qwen_sft_peft.py",
    "--model-name", model_name,
    "--train-file", train_file,
    "--output-dir", output_dir,
    "--overwrite-output-dir",
    "--device", "npu",
    "--npu-device-map", "balanced-layers",
    "--npu-max-memory-gib", "54",
    "--max-length", max_length,
    "--max-steps", max_steps,
    "--num-epochs", num_epochs,
    "--per-device-batch-size", per_device_batch_size,
    "--gradient-accumulation-steps", grad_accum,
    "--learning-rate", learning_rate,
    "--eval-steps", eval_steps,
    "--log-steps", log_steps,
    "--lora-rank", lora_rank,
    "--lora-alpha", lora_alpha,
    "--lora-dropout", lora_dropout,
    "--lora-backend", lora_backend,
    "--target-modules",
]
if eval_file:
    output_index = trainer.index("--output-dir")
    trainer[output_index:output_index] = ["--eval-file", eval_file]
trainer_shell = " ".join(shlex.quote(part) for part in trainer) + " " + " ".join(target_modules_parts) + " --train-on-completions-only --gradient-checkpointing"
if train_layernorm == "1":
    trainer_shell += " --train-layernorm"
if target_module_regex_parts:
    trainer_shell += " --target-module-regex " + " ".join(target_module_regex_parts)
if trainable_param_regex_parts:
    trainer_shell += " --trainable-param-regex " + " ".join(trainable_param_regex_parts)
if freeze_param_regex_parts:
    trainer_shell += " --freeze-param-regex " + " ".join(freeze_param_regex_parts)
trainer_shell += " --min-trainable-parameters " + shlex.quote(min_trainable) + " --max-trainable-parameters " + shlex.quote(max_trainable)
if extra_train_args_parts:
    trainer_shell += " " + " ".join(extra_train_args_parts)
try:
    nproc_int = int(nproc)
except ValueError:
    nproc_int = 1
if nproc_int > 1:
    trainer_shell = (
        "torchrun --nproc_per_node="
        + shlex.quote(str(nproc_int))
        + " --master_port=${MASTER_PORT:-29635} "
        + trainer_shell
    )
commands = [
    "set -euo pipefail",
    "echo __ASI1_ISQ_SFT_BOOT__",
    "pwd",
    "whoami",
    "python3 --version",
    f"mkdir -p {shlex.quote(remote_root)}",
    f"cd {shlex.quote(remote_root)}",
]
if embed_local_files == "1":
    commands.extend([
        "echo __ASI1_ISQ_SFT_EMBED_START__",
        "mkdir -p training " + shlex.quote(str(pathlib.PurePosixPath(train_file).parent)),
    ])
    if embed_code_files == "1":
        append_embedded_file(commands, "training/qwen_sft_peft.py", "training/qwen_sft_peft.py", "trainer")
        append_embedded_file(commands, "training/model_backend.py", "training/model_backend.py", "model_backend")
        append_embedded_file(commands, "training/model_family_preflight.py", "training/model_family_preflight.py", "model_family_preflight")
        append_embedded_file(commands, "training/text_preprocessor_backend.py", "training/text_preprocessor_backend.py", "text_preprocessor_backend")
        append_embedded_file(commands, "training/runtime_overlay.py", "training/runtime_overlay.py", "runtime_overlay")
        append_embedded_file(commands, "training/research_plugins.py", "training/research_plugins.py", "research_plugins")
        append_embedded_file(commands, "scripts/preflight_qwen36_ascend_hf_training.py", "scripts/preflight_qwen36_ascend_hf_training.py", "preflight_qwen36")
    if embed_runtime_files == "1":
        runtime_src = "artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src/transformers"
        remote_runtime = "artifacts/runtime-overlays/qwen35-moe-min/transformers"
        append_embedded_file(commands, f"{runtime_src}/modeling_rope_utils.py", f"{remote_runtime}/modeling_rope_utils.py", "rt_modeling_rope_utils")
        runtime_root = "artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src/transformers/models"
        remote_runtime_models = "artifacts/runtime-overlays/qwen35-moe-min/transformers/models"
        append_embedded_tree(commands, f"{runtime_root}/qwen3_5", f"{remote_runtime_models}/qwen3_5", "rt_qwen3_5")
        append_embedded_tree(commands, f"{runtime_root}/qwen3_5_moe", f"{remote_runtime_models}/qwen3_5_moe", "rt_qwen3_5_moe")
        append_embedded_tree(commands, f"{runtime_root}/qwen3_next", f"{remote_runtime_models}/qwen3_next", "rt_qwen3_next")
        commands.append("export QUANTUM_TRANSFORMERS_RUNTIME_SRC=artifacts/runtime-overlays/qwen35-moe-min")
    if embed_data_files == "1":
        append_embedded_file(commands, train_file, train_file, "train")
        if eval_file:
            append_embedded_file(commands, eval_file, eval_file, "eval")
        manifest_path = root_path / split_dir / "manifest.json"
        if manifest_path.is_file():
            append_embedded_file(commands, f"{split_dir}/manifest.json", f"{split_dir}/manifest.json", "manifest")
    commands.append("echo __ASI1_ISQ_SFT_EMBED_DONE__")

if skip_sync == "1":
    commands.append("echo __ASI1_ISQ_SFT_SYNC_SKIPPED__")
else:
    commands.extend([
        "export PATH=/tmp:/root/work/filestorage:$PATH",
        "ln -sf /root/work/filestorage/rclone-bin /tmp/rclone",
        "command -v rclone",
        "export RCLONE_CONFIG_INER_TYPE=s3",
        "export RCLONE_CONFIG_INER_PROVIDER=Other",
        "export RCLONE_CONFIG_INER_ACCESS_KEY_ID=" + shlex.quote(access_key),
        "export RCLONE_CONFIG_INER_SECRET_ACCESS_KEY=" + shlex.quote(secret),
        "export RCLONE_CONFIG_INER_ENDPOINT=" + shlex.quote(endpoint),
        "export RCLONE_CONFIG_INER_ACL=private",
        "export RCLONE_CONFIG_INER_FORCE_PATH_STYLE=true",
        "unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY",
        "echo __ASI1_ISQ_SFT_SYNC_START__",
    ])
    if sync_code_files == "1":
        commands.append(
            f"rclone copy {shlex.quote(s3_root + '/training')} training "
            "--s3-endpoint " + shlex.quote(endpoint) + " --s3-no-check-bucket --no-traverse --transfers 8 --checkers 16 --low-level-retries 1 --retries 1 --contimeout 10s --timeout 60s"
        )
    else:
        commands.append("echo __ASI1_ISQ_SFT_SYNC_TRAINING_SKIPPED__")
    if sync_script_files == "1":
        commands.append(
            f"rclone copy {shlex.quote(s3_root + '/scripts')} scripts "
            "--s3-endpoint " + shlex.quote(endpoint) + " --s3-no-check-bucket --no-traverse --transfers 8 --checkers 16 --low-level-retries 1 --retries 1 --contimeout 10s --timeout 60s"
        )
    else:
        commands.append("echo __ASI1_ISQ_SFT_SYNC_SCRIPTS_SKIPPED__")
    if sync_data_files == "1":
        commands.append(
            f"rclone copy {shlex.quote(s3_root + '/' + split_dir)} {shlex.quote(split_dir)} "
            "--s3-endpoint " + shlex.quote(endpoint) + " --s3-no-check-bucket --no-traverse --transfers 8 --checkers 16 --low-level-retries 1 --retries 1 --contimeout 10s --timeout 60s"
        )
    else:
        commands.append("echo __ASI1_ISQ_SFT_SYNC_DATA_SKIPPED__")
    commands.append("echo __ASI1_ISQ_SFT_SYNC_DONE__")
commands.extend([
    f"test -d {shlex.quote(model_name)}",
    "test -s training/qwen_sft_peft.py",
    f"test -s {shlex.quote(train_file)}",
    f"mkdir -p {shlex.quote('/'.join(log_path.split('/')[:-1]) or '.')} reports outputs",
    "python3 -m py_compile training/qwen_sft_peft.py",
])
if eval_file:
    commands.append(f"test -s {shlex.quote(eval_file)}")
if install_deps == "1":
    split_wheel_dir = "tools/wheels"
    peft_wheel = f"{split_wheel_dir}/peft-0.14.0-py3-none-any.whl"
    accelerate_wheel = f"{split_wheel_dir}/accelerate-1.4.0-py3-none-any.whl"
    commands.extend([
        "echo __ASI1_ISQ_SFT_DEPS_START__",
        f"test -s {shlex.quote(accelerate_wheel)}",
        f"test -s {shlex.quote(peft_wheel)}",
        f"python3 -m pip install --no-index --no-deps {shlex.quote(accelerate_wheel)}",
        f"python3 -m pip install --no-index --no-deps {shlex.quote(peft_wheel)}",
        "python3 -c 'import transformers; print(transformers.__version__)'",
        "python3 -c 'import peft; print(peft.__version__)'",
        "python3 -c 'import accelerate; print(accelerate.__version__)'",
        "echo __ASI1_ISQ_SFT_DEPS_DONE__",
    ])
if pip_install_cmd:
    commands.extend([
        "echo __ASI1_ISQ_SFT_PIP_INSTALL_START__",
        pip_install_cmd,
        "python3 -c 'import transformers; print(transformers.__version__)'",
        "python3 -c 'import peft; print(peft.__version__)'",
        "python3 -c 'import accelerate; print(accelerate.__version__)'",
        "echo __ASI1_ISQ_SFT_PIP_INSTALL_DONE__",
    ])
commands.extend([
    python_exec_line(
        "import os\n"
        f"os.environ['ASCEND_RT_VISIBLE_DEVICES'] = {visible_devices!r}\n"
        "with open('/tmp/asi1_visible_devices.env', 'w', encoding='utf-8') as f:\n"
        "    f.write('ASCEND_RT_VISIBLE_DEVICES=' + os.environ['ASCEND_RT_VISIBLE_DEVICES'] + '\\n')\n"
    ),
    "set -a && . /tmp/asi1_visible_devices.env && set +a",
    "export QUANTUM_TRANSFORMERS_RUNTIME_SRC=${QUANTUM_TRANSFORMERS_RUNTIME_SRC:-artifacts/runtime-overlays/qwen35-moe-min}",
    "export PYTORCH_NPU_ALLOC_CONF=max_split_size_mb:256",
    "export TOKENIZERS_PARALLELISM=false",
    "export PYTHONUNBUFFERED=1",
])
if skip_preflight != "1":
    commands.append("python3 scripts/preflight_qwen36_ascend_hf_training.py --model-name " + shlex.quote(model_name) + " --device npu --json")
commands.extend([
    "echo __ASI1_ISQ_SFT_BEFORE_TRAIN__",
    trainer_shell,
    "echo __ASI1_ISQ_SFT_AFTER_TRAIN__",
    f"test -f {shlex.quote(output_dir + '/metrics.json')}",
    f"test -d {shlex.quote(output_dir + '/adapter')}",
    f"cp {shlex.quote(output_dir + '/metrics.json')} reports/asi1_verified10k_sft_metrics.json",
    "echo __ASI1_ISQ_SFT_DONE__",
])
inner = "\n".join(commands)
encoded = base64.b64encode(inner.encode()).decode()
remote_b64 = "/tmp/asi1_verified10k_sft.b64"
remote_script = "/tmp/asi1_verified10k_sft.sh"
lines = ["set -euo pipefail", f"rm -f {remote_b64} {remote_script}"]
for index in range(0, len(encoded), 1800):
    chunk = encoded[index:index+1800]
    source = "import pathlib\np=pathlib.Path(%r)\nold=p.read_text() if p.exists() else ''\np.write_text(old+%r)" % (remote_b64, chunk)
    lines.append("python3 -c " + shlex.quote(";".join(line.strip() for line in source.splitlines())))
decode = "import base64\nimport pathlib\nsrc=pathlib.Path(%r)\ndst=pathlib.Path(%r)\ndst.write_bytes(base64.b64decode(src.read_text()))\ndst.chmod(0o700)" % (remote_b64, remote_script)
lines.append("python3 -c " + shlex.quote(";".join(line.strip() for line in decode.splitlines())))
lines.append(f"bash {remote_script}")
execution_command = "\n".join(lines)
print(json.dumps({
    "remote_root": remote_root,
    "output_dir": output_dir,
    "log_path": log_path,
    "job_name": "asi1-verified10k-sft",
    "remote_command": inner,
    "execution_command": execution_command,
}, indent=2))
PY
}

if [[ "${1:-}" == "--dry-run" && "${2:-}" == "__launch-spec" ]]; then
  render_launch_spec
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --submit) SUBMIT=1; shift ;;
    --dry-run) PRINT_ONLY=1; shift ;;
    --task-name) TASK_NAME="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

CMD=(
  node "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
  --url "$TRAIN_DEV_URL"
  --wait-ms "$WAIT_MS"
  --task-name "$TASK_NAME"
  --image-name "$IMAGE_NAME"
  --resource-group "$RESOURCE_GROUP"
  --resource-group-type "$RESOURCE_GROUP_TYPE"
  --instance-count "$INSTANCE_COUNT"
  --accelerator-cards "$ACCELERATOR_CARDS"
  --cpu-cores "$CPU_CORES"
  --memory-gb "$MEMORY_GB"
  --remote-root "$REMOTE_ROOT"
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_isq_sft_task.sh"
  --launcher-arg "__launch-spec"
  --ignore-project-quota-text
  --no-direct-submit-fallback
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
