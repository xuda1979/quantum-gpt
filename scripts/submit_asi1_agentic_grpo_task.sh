#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

REMOTE_ROOT="${ASI1_AGENTIC_TASK_REMOTE_ROOT:-/workspace/quantum-gpt}"
MODEL_NAME="${ASI1_AGENTIC_TASK_MODEL_NAME:-/root/work/filestorage/Qwen3.6-35B-A3B}"
BENCHMARK_FILE="${ASI1_AGENTIC_TASK_BENCHMARK_FILE:-evals/benchmarks/agentic_coding_trajectory_training_v1.txt}"
DOMAIN_FILTER="${ASI1_AGENTIC_TASK_DOMAIN_FILTER:-}"
TASK_NAME="${ASI1_AGENTIC_TASK_NAME:-asi1-grpo-fast}"
IMAGE_NAME="${ASI1_AGENTIC_TASK_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_AGENTIC_TASK_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_AGENTIC_TASK_RESOURCE_GROUP_TYPE:-公共资源组}"
TASK_PRIORITY="${ASI1_AGENTIC_TASK_PRIORITY:-高}"
INSTANCE_COUNT="${ASI1_AGENTIC_TASK_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_AGENTIC_TASK_ACCELERATOR_CARDS:-8}"
CPU_CORES="${ASI1_AGENTIC_TASK_CPU_CORES:-128}"
MEMORY_GB="${ASI1_AGENTIC_TASK_MEMORY_GB:-1920}"
WAIT_MS="${ASI1_AGENTIC_TASK_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_AGENTIC_TASK_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-agentic-grpo-fast}"
TRAIN_DEV_URL="${ASI1_AGENTIC_TASK_URL:-}"
VISIBLE_DEVICES="${ASI1_AGENTIC_TASK_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
NPROC_PER_NODE="${ASI1_AGENTIC_TASK_NPROC_PER_NODE:-8}"
GROUP_SIZE="${ASI1_AGENTIC_TASK_GROUP_SIZE:-8}"
GRPO_STEPS="${ASI1_AGENTIC_TASK_GRPO_STEPS:-128}"
MASTER_PORT="${ASI1_AGENTIC_TASK_MASTER_PORT:-29533}"
MAX_NEW_TOKENS="${ASI1_AGENTIC_TASK_MAX_NEW_TOKENS:-4096}"
MAX_SEQ_LENGTH="${ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH:-32768}"
MAX_TURNS="${ASI1_AGENTIC_TASK_MAX_TURNS:-32}"
ONLINE_EVAL_EVERY_STEPS="${ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS:-8}"
ONLINE_EVAL_MAX_TASKS="${ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS:-8}"
ONLINE_EVAL_BENCHMARK_FILE="${ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE:-evals/benchmarks/quantum_generalization_holdout_v2_hard.txt}"
ONLINE_EVAL_TEMPERATURE="${ASI1_AGENTIC_TASK_ONLINE_EVAL_TEMPERATURE:-0.2}"
CHECKPOINT_INTERVAL_SECONDS="${ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS:-3600}"
CHECKPOINT_EVERY_STEPS="${ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS:-0}"
LORA_RANK="${ASI1_AGENTIC_TASK_LORA_RANK:-64}"
LORA_ALPHA="${ASI1_AGENTIC_TASK_LORA_ALPHA:-128}"
LORA_DROPOUT="${ASI1_AGENTIC_TASK_LORA_DROPOUT:-0.0}"
TARGET_MODULES="${ASI1_AGENTIC_TASK_TARGET_MODULES:-q_proj k_proj v_proj o_proj gate_proj up_proj down_proj}"
TRAIN_LAYER_NORM="${ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM:-1}"
MIN_TRAINABLE_PARAMETERS="${ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS:-200000000}"
MAX_TRAINABLE_PARAMETERS="${ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS:-1000000000}"
RESEARCH_METHODS="${ASI1_AGENTIC_TASK_RESEARCH_METHODS:-clause_aware_verifier_reward ast_anchor_interface_grounding self_consistency_verifier_routing uncertainty_triggered_repair_replay behavior_anchor_coverage_reward}"
TRAINING_MODE="${ASI1_AGENTIC_TASK_TRAINING_MODE:-lora}"
COMPACT_COMMAND="${ASI1_AGENTIC_TASK_COMPACT_COMMAND:-1}"
EMBED_INLINE_SCRIPT="${ASI1_AGENTIC_TASK_EMBED_INLINE_SCRIPT:-0}"
BOOTSTRAP_S3="${ASI1_AGENTIC_TASK_BOOTSTRAP_S3:-0}"
BOOTSTRAP_BUNDLE_URL="${ASI1_AGENTIC_TASK_BOOTSTRAP_BUNDLE_URL:-}"
BOOTSTRAP_BUNDLE_SHA256="${ASI1_AGENTIC_TASK_BOOTSTRAP_BUNDLE_SHA256:-}"
BOOTSTRAP_BUNDLE_NAME="${ASI1_AGENTIC_TASK_BOOTSTRAP_BUNDLE_NAME:-qg_asi1_agentic_grpo_minibundle.tar.gz}"
EMBED_RUNTIME_BUNDLE="${ASI1_AGENTIC_TASK_EMBED_RUNTIME_BUNDLE:-0}"
RUNTIME_BUNDLE_PATH="${ASI1_AGENTIC_TASK_RUNTIME_BUNDLE_PATH:-}"
BOOTSTRAP_WHEELHOUSE="${ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE:-0}"
PUSH_RESULTS_S3="${ASI1_AGENTIC_TASK_PUSH_RESULTS_S3:-0}"
EMBED_WHEELHOUSE="${ASI1_AGENTIC_TASK_EMBED_WHEELHOUSE:-0}"
OVERRIDE_COMMAND_FILE="${ASI1_AGENTIC_TASK_OVERRIDE_COMMAND_FILE:-}"
DIRECT_SUBMIT_ONLY="${ASI1_AGENTIC_TASK_DIRECT_SUBMIT_ONLY:-0}"
TIMESTAMP="${ASI1_AGENTIC_TASK_TIMESTAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
OUTPUT_DIR="${ASI1_AGENTIC_TASK_OUTPUT_DIR:-outputs/qwen36-35b-a3b-agentic-grpo-asi1-task-fast-${TIMESTAMP}}"
LOG_PATH="${ASI1_AGENTIC_TASK_LOG_PATH:-/tmp/qwen36_35b_a3b_agentic_grpo_asi1_task_fast_${TIMESTAMP}.log}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_agentic_grpo_task.sh [--submit] [options]

Defaults to filling an ASI1 Huanxin training-task drawer only. It does not
submit unless --submit is explicitly provided.

Options:
  --submit
  --dry-run
  --task-name <name>
  --remote-root <path>
  --model-name <path>
  --benchmark-file <path>
  --domain-filter <domain>
  --output-dir <path>
  --log-path <path>
  --artifact-stem <stem>
  --wait-ms <ms>
  --image-name <name>
  --accelerator-cards <n>
  --cpu-cores <n>
  --memory-gb <n>
  --visible-devices <ids>
  --nproc-per-node <n>
  --group-size <n>
  --grpo-steps <n>
  --master-port <n>
  --max-new-tokens <n>
  --max-seq-length <n>
  --max-turns <n>
  --online-eval-every-steps <n>
  --online-eval-max-tasks <n>
  --online-eval-benchmark-file <path>
  --online-eval-temperature <float>
  --checkpoint-interval-seconds <n>
  --checkpoint-every-steps <n>
  --lora-rank <n>
  --lora-alpha <n>
  --lora-dropout <float>
  --target-modules <space-separated-module-suffixes>
  --train-layernorm <0|1>
  --min-trainable-parameters <n>
  --max-trainable-parameters <n>
  --research-methods <space-separated-methods>
  --training-mode <lora|native>
  --hours <n>
  --bootstrap-s3
  --bootstrap-bundle-url <signed-url>
  --bootstrap-bundle-sha256 <sha256>
  --bootstrap-bundle-name <name>
  --embed-runtime-bundle
  --runtime-bundle-path <local-tar.gz>
  --bootstrap-wheelhouse
  --embed-wheelhouse
  --push-results-s3
  --override-command-file <path>
  --direct-submit-only
  --full-command
  --raw-command
  --inline-compact-command
  --repo-runner-command
  --embed-inline-script
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  if [[ "$EMBED_WHEELHOUSE" == "1" ]]; then
    python3 - "$ROOT_DIR" "$REMOTE_ROOT" "$MODEL_NAME" "$BENCHMARK_FILE" "$DOMAIN_FILTER" "$OUTPUT_DIR" "$LOG_PATH" "$VISIBLE_DEVICES" "$NPROC_PER_NODE" "$GROUP_SIZE" "$GRPO_STEPS" "$MASTER_PORT" "$MAX_NEW_TOKENS" "$MAX_SEQ_LENGTH" "$MAX_TURNS" "$ONLINE_EVAL_EVERY_STEPS" "$ONLINE_EVAL_MAX_TASKS" "$ONLINE_EVAL_BENCHMARK_FILE" "$ONLINE_EVAL_TEMPERATURE" "$CHECKPOINT_INTERVAL_SECONDS" "$CHECKPOINT_EVERY_STEPS" "$LORA_RANK" "$LORA_ALPHA" <<'PY'
import base64
import json
import pathlib
import shlex
import sys

(
    root_dir,
    remote_root,
    model_name,
    benchmark_file,
    domain_filter,
    output_dir,
    log_path,
    visible_devices,
    nproc,
    group_size,
    grpo_steps,
    master_port,
    max_new_tokens,
    max_seq_length,
    max_turns,
    online_eval_every_steps,
    online_eval_max_tasks,
    online_eval_benchmark_file,
    online_eval_temperature,
    checkpoint_interval_seconds,
    checkpoint_every_steps,
    lora_rank,
    lora_alpha,
) = sys.argv[1:]

root = pathlib.Path(root_dir)
wheel_root = "/tmp/asi1-agentic-wheelhouse"
wheel_names = [
    "accelerate-1.4.0-py3-none-any.whl",
    "peft-0.14.0-py3-none-any.whl",
]
commands = [
    "set -euo pipefail",
    f"cd {shlex.quote(remote_root)}",
    "echo ASI1_EMBEDDED_WHEELHOUSE_GRPO_START",
    "pwd",
    "python3 --version",
    f"mkdir -p {shlex.quote(wheel_root)}/tools/wheels",
]
for wheel_name in wheel_names:
    wheel_path = root / "tools" / "wheels" / wheel_name
    encoded = base64.b64encode(wheel_path.read_bytes()).decode("ascii")
    chunk_path = f"{wheel_root}/asi1-wheel-{wheel_name}.b64"
    commands.append(f"rm -f {shlex.quote(chunk_path)}")
    commands.append(f"touch {shlex.quote(chunk_path)}")
    for index in range(0, len(encoded), 3600):
        chunk = encoded[index : index + 3600]
        commands.append(
            "python3 scripts/append_text_file.py "
            f"--path {shlex.quote(chunk_path)} --text {shlex.quote(chunk)}"
        )
    wheel_output = f"{wheel_root}/tools/wheels/{wheel_name}"
    commands.append(
        "python3 scripts/decode_base64_file.py "
        f"--input {shlex.quote(chunk_path)} --output {shlex.quote(wheel_output)}"
    )
    commands.append(f"python3 -m zipfile -t {shlex.quote(wheel_output)}")
commands.extend(
    [
        f"python3 -m pip install --no-cache-dir --no-input --no-index --find-links {shlex.quote(wheel_root + '/tools/wheels')} accelerate==1.4.0 peft==0.14.0",
        "python3 -c \"import accelerate; import peft; print('accelerate=' + accelerate.__version__); print('peft=' + peft.__version__)\"",
        f"export ASI1_AGENTIC_TASK_MODEL_NAME={shlex.quote(model_name)}",
        f"export ASI1_AGENTIC_TASK_BENCHMARK_FILE={shlex.quote(benchmark_file)}",
        f"export ASI1_AGENTIC_TASK_DOMAIN_FILTER={shlex.quote(domain_filter)}",
        f"export ASI1_AGENTIC_TASK_OUTPUT_DIR={shlex.quote(output_dir)}",
        f"export ASI1_AGENTIC_TASK_LOG_PATH={shlex.quote(log_path)}",
        f"export ASI1_AGENTIC_TASK_VISIBLE_DEVICES={shlex.quote(visible_devices)}",
        f"export ASI1_AGENTIC_TASK_NPROC_PER_NODE={shlex.quote(nproc)}",
        f"export ASI1_AGENTIC_TASK_GROUP_SIZE={shlex.quote(group_size)}",
        f"export ASI1_AGENTIC_TASK_GRPO_STEPS={shlex.quote(grpo_steps)}",
        f"export ASI1_AGENTIC_TASK_MASTER_PORT={shlex.quote(master_port)}",
        f"export ASI1_AGENTIC_TASK_MAX_NEW_TOKENS={shlex.quote(max_new_tokens)}",
        f"export ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH={shlex.quote(max_seq_length)}",
        f"export ASI1_AGENTIC_TASK_MAX_TURNS={shlex.quote(max_turns)}",
        f"export ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS={shlex.quote(online_eval_every_steps)}",
        f"export ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS={shlex.quote(online_eval_max_tasks)}",
        f"export ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE={shlex.quote(online_eval_benchmark_file)}",
        f"export ASI1_AGENTIC_TASK_ONLINE_EVAL_TEMPERATURE={shlex.quote(online_eval_temperature)}",
        f"export ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS={shlex.quote(checkpoint_interval_seconds)}",
        f"export ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS={shlex.quote(checkpoint_every_steps)}",
        f"export ASI1_AGENTIC_TASK_LORA_RANK={shlex.quote(lora_rank)}",
        f"export ASI1_AGENTIC_TASK_LORA_ALPHA={shlex.quote(lora_alpha)}",
        "export ASI1_AGENTIC_TASK_LORA_DROPOUT=0.0",
        "export ASI1_AGENTIC_TASK_TARGET_MODULES='q_proj k_proj v_proj o_proj gate_proj up_proj down_proj'",
        "export ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM=1",
        "export ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS=200000000",
        "export ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS=1000000000",
        "export ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE=0",
        "bash scripts/run_asi1_agentic_grpo_from_env.sh",
        "echo ASI1_EMBEDDED_WHEELHOUSE_GRPO_DONE",
    ]
)
execution_command = "\n".join(commands)
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": output_dir,
            "log_path": log_path,
            "job_name": "asi1-agentic-grpo-fast",
            "remote_command": execution_command,
            "execution_command": execution_command,
            "compact_command": "embedded-wheelhouse",
            "bootstrap_s3": False,
            "bootstrap_wheelhouse": True,
            "embed_wheelhouse": True,
            "push_results_s3": False,
        },
        indent=2,
    )
)
PY
    return
  fi

  if [[ "$COMPACT_COMMAND" == "repo-runner" ]]; then
    local remote_setup=""
    local s3_root=""
    if [[ "$BOOTSTRAP_S3" != "1" && -z "$BOOTSTRAP_BUNDLE_URL" && "$EMBED_RUNTIME_BUNDLE" != "1" ]]; then
      echo "repo-runner mode requires --bootstrap-s3, --bootstrap-bundle-url, or --embed-runtime-bundle so the remote runner script exists" >&2
      return 2
    fi
    if [[ "$BOOTSTRAP_S3" == "1" || "$PUSH_RESULTS_S3" == "1" ]]; then
      # Shell-task execution starts before /workspace/quantum-gpt exists, so the
      # bootstrap command must carry the minimal rclone config with it.
      source "$ROOT_DIR/scripts/iner_s3_env.sh"
      remote_setup="$(
        python3 - <<'PY' "$INER_S3_ENDPOINT" "$INER_ACCESS_KEY_ID" "$INER_SECRET_ACCESS_KEY"
import base64
import shlex
import sys

endpoint, access_key_id, secret = sys.argv[1:]
content = f"""[iner]
type = s3
provider = Other
access_key_id = {access_key_id}
secret_access_key = {secret}
endpoint = {endpoint}
acl = private
force_path_style = true
"""
encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
script = (
    "import base64,pathlib; "
    "pathlib.Path('/tmp/iner-rclone.conf').write_bytes(base64.b64decode("
    + repr(encoded)
    + ")); "
    "pathlib.Path('/tmp/iner-rclone.conf').chmod(0o600)"
)
print("umask 077 && python3 -c " + shlex.quote(script))
PY
      )"
      s3_root="$INER_S3_ROOT"
    fi
    python3 - "$ROOT_DIR" "$REMOTE_ROOT" "$MODEL_NAME" "$BENCHMARK_FILE" "$DOMAIN_FILTER" "$OUTPUT_DIR" "$LOG_PATH" "$VISIBLE_DEVICES" "$NPROC_PER_NODE" "$GROUP_SIZE" "$GRPO_STEPS" "$MASTER_PORT" "$MAX_NEW_TOKENS" "$MAX_SEQ_LENGTH" "$MAX_TURNS" "$ONLINE_EVAL_EVERY_STEPS" "$ONLINE_EVAL_MAX_TASKS" "$ONLINE_EVAL_BENCHMARK_FILE" "$ONLINE_EVAL_TEMPERATURE" "$CHECKPOINT_INTERVAL_SECONDS" "$CHECKPOINT_EVERY_STEPS" "$LORA_RANK" "$LORA_ALPHA" "$TRAINING_MODE" "$RESEARCH_METHODS" "$BOOTSTRAP_WHEELHOUSE" "$PUSH_RESULTS_S3" "$remote_setup" "$s3_root" "$BOOTSTRAP_BUNDLE_URL" "$BOOTSTRAP_BUNDLE_SHA256" "$BOOTSTRAP_BUNDLE_NAME" "$EMBED_RUNTIME_BUNDLE" "$RUNTIME_BUNDLE_PATH" <<'PY'
import base64
import hashlib
import json
import os
import pathlib
import shlex
import sys

(
    root_dir,
    remote_root,
    model_name,
    benchmark_file,
    domain_filter,
    output_dir,
    log_path,
    visible_devices,
    nproc,
    group_size,
    grpo_steps,
    master_port,
    max_new_tokens,
    max_seq_length,
    max_turns,
    online_eval_every_steps,
    online_eval_max_tasks,
    online_eval_benchmark_file,
    online_eval_temperature,
    checkpoint_interval_seconds,
    checkpoint_every_steps,
    lora_rank,
    lora_alpha,
    training_mode,
    research_methods,
    bootstrap_wheelhouse,
    push_results_s3,
    remote_setup,
    s3_root,
    bootstrap_bundle_url,
    bootstrap_bundle_sha256,
    bootstrap_bundle_name,
    embed_runtime_bundle,
    runtime_bundle_path,
) = sys.argv[1:]

env_lines = {
    "ASI1_AGENTIC_TASK_MODEL_NAME": model_name,
    "ASI1_AGENTIC_TASK_BENCHMARK_FILE": benchmark_file,
    "ASI1_AGENTIC_TASK_DOMAIN_FILTER": domain_filter,
    "ASI1_AGENTIC_TASK_OUTPUT_DIR": output_dir,
    "ASI1_AGENTIC_TASK_LOG_PATH": log_path,
    "ASI1_AGENTIC_TASK_VISIBLE_DEVICES": visible_devices,
    "ASI1_AGENTIC_TASK_NPROC_PER_NODE": nproc,
    "ASI1_AGENTIC_TASK_GROUP_SIZE": group_size,
    "ASI1_AGENTIC_TASK_GRPO_STEPS": grpo_steps,
    "ASI1_AGENTIC_TASK_MASTER_PORT": master_port,
    "ASI1_AGENTIC_TASK_MAX_NEW_TOKENS": max_new_tokens,
    "ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH": max_seq_length,
    "ASI1_AGENTIC_TASK_MAX_TURNS": max_turns,
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS": online_eval_every_steps,
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS": online_eval_max_tasks,
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE": online_eval_benchmark_file,
    "ASI1_AGENTIC_TASK_ONLINE_EVAL_TEMPERATURE": online_eval_temperature,
    "ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS": checkpoint_interval_seconds,
    "ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS": checkpoint_every_steps,
    "ASI1_AGENTIC_TASK_LORA_RANK": lora_rank,
    "ASI1_AGENTIC_TASK_LORA_ALPHA": lora_alpha,
    "ASI1_AGENTIC_TASK_LORA_DROPOUT": os.environ.get("ASI1_AGENTIC_TASK_LORA_DROPOUT", "0.0"),
    "ASI1_AGENTIC_TASK_TARGET_MODULES": os.environ.get("ASI1_AGENTIC_TASK_TARGET_MODULES", "q_proj k_proj v_proj o_proj gate_proj up_proj down_proj"),
    "ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM": os.environ.get("ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM", "1"),
    "ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS": os.environ.get("ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS", "200000000"),
    "ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS": os.environ.get("ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS", "1000000000"),
    "ASI1_AGENTIC_TASK_TRAINING_MODE": training_mode,
    "ASI1_AGENTIC_TASK_RESEARCH_METHODS": research_methods,
    "ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE": bootstrap_wheelhouse,
    "ASI1_AGENTIC_TASK_PUSH_RESULTS_S3": push_results_s3,
    "ASI1_AGENTIC_TASK_S3_ROOT": s3_root,
    "ASI1_AGENTIC_TASK_RCLONE_CONFIG": "/tmp/iner-rclone.conf",
}
commands = [
    "set -euo pipefail",
    "echo __ASI1_REPO_RUNNER_BOOT__",
    "pwd",
    "whoami",
    "python3 --version",
    remote_setup.strip(),
    f"mkdir -p {shlex.quote(remote_root)}",
]
if embed_runtime_bundle == "1":
    bundle_source = pathlib.Path(runtime_bundle_path) if runtime_bundle_path else None
    if bundle_source is None or not bundle_source.exists():
        candidates = sorted(
            (pathlib.Path(root_dir) / "artifacts" / "runtime-bundles").glob("qg_asi1_agentic_grpo_minibundle_*.tar.gz"),
            key=lambda path: path.stat().st_mtime,
        )
        if not candidates:
            raise SystemExit("missing runtime bundle; create artifacts/runtime-bundles/qg_asi1_agentic_grpo_minibundle_*.tar.gz")
        bundle_source = candidates[-1]
    bundle_bytes = bundle_source.read_bytes()
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    bundle_name = bootstrap_bundle_name or bundle_source.name
    bundle_path = f"/tmp/{bundle_name}"
    bundle_b64_path = f"/tmp/{bundle_name}.b64"
    encoded_bundle = base64.b64encode(bundle_bytes).decode("ascii")
    commands.extend(
        [
            "echo __ASI1_REPO_RUNNER_EMBEDDED_BUNDLE_RESTORE__",
            f"rm -f {shlex.quote(bundle_b64_path)} {shlex.quote(bundle_path)}",
        ]
    )
    for index in range(0, len(encoded_bundle), 3600):
        chunk = encoded_bundle[index : index + 3600]
        commands.append(
            "python3 -c "
            + shlex.quote(
                "import pathlib\n"
                f"p=pathlib.Path({bundle_b64_path!r})\n"
                "old=p.read_text() if p.exists() else ''\n"
                f"p.write_text(old+{chunk!r})"
            )
        )
    commands.extend(
        [
            "python3 -c "
            + shlex.quote(
                "import base64,pathlib\n"
                f"src=pathlib.Path({bundle_b64_path!r})\n"
                f"dst=pathlib.Path({bundle_path!r})\n"
                "dst.write_bytes(base64.b64decode(src.read_text()))"
            ),
            f"echo {shlex.quote(bundle_sha256 + '  ' + bundle_path)} | sha256sum -c -",
            f"tar -xzf {shlex.quote(bundle_path)} -C {shlex.quote(remote_root)}",
            "echo __ASI1_REPO_RUNNER_AFTER_SYNC__",
            f"cd {shlex.quote(remote_root)}",
        ]
    )
elif bootstrap_bundle_url:
    encoded_url = base64.b64encode(bootstrap_bundle_url.encode("utf-8")).decode("ascii")
    bundle_path = f"/tmp/{bootstrap_bundle_name}"
    commands.extend(
        [
            "echo __ASI1_REPO_RUNNER_BUNDLE_FETCH__",
            (
                "url=$(python3 -c "
                + shlex.quote(f"import base64; print(base64.b64decode({encoded_url!r}).decode())")
                + "); "
                f"curl -fL --retry 3 --connect-timeout 20 --max-time 300 \"$url\" -o {shlex.quote(bundle_path)}"
            ),
            f"test -s {shlex.quote(bundle_path)}",
        ]
    )
    if bootstrap_bundle_sha256:
        commands.append(
            f"echo {shlex.quote(bootstrap_bundle_sha256 + '  ' + bundle_path)} | sha256sum -c -"
        )
    commands.extend(
        [
            f"tar -xzf {shlex.quote(bundle_path)} -C {shlex.quote(remote_root)}",
            "echo __ASI1_REPO_RUNNER_AFTER_SYNC__",
            f"cd {shlex.quote(remote_root)}",
        ]
    )
else:
    commands.extend(
        [
            (
        "if command -v rclone; then echo using_system_rclone; fi; "
        "if ! command -v rclone && "
        f"test -f {shlex.quote(remote_root)}/tools/preseed/rclone-linux-arm64; then "
        "mkdir -p /tmp/asi1-rclone-bin; "
        f"cp {shlex.quote(remote_root)}/tools/preseed/rclone-linux-arm64 /tmp/asi1-rclone-bin/rclone; "
        "chmod +x /tmp/asi1-rclone-bin/rclone; export PATH=/tmp/asi1-rclone-bin:$PATH; "
        "echo using_preseed_rclone; fi; "
        "if ! command -v rclone && command -v curl; then "
        "tmpd=$(mktemp -d /tmp/asi1-rclone.XXXXXX); "
        "if curl -fsSL --retry 3 https://downloads.rclone.org/rclone-current-linux-arm64.zip -o $tmpd/rclone.zip; then "
        "python3 -m zipfile -e $tmpd/rclone.zip $tmpd; "
        "mkdir -p /tmp/asi1-rclone-bin; "
        "find $tmpd -type f -name rclone -exec cp {} /tmp/asi1-rclone-bin/rclone \\; -quit; "
        "chmod +x /tmp/asi1-rclone-bin/rclone; export PATH=/tmp/asi1-rclone-bin:$PATH; "
        "echo using_downloaded_rclone; "
        "else echo rclone_curl_download_failed; fi; fi; "
        "if ! command -v rclone && command -v apt-get; then "
        "apt-get update && apt-get install -y --no-install-recommends rclone || echo rclone_apt_install_failed; fi; "
        "if ! command -v rclone; then echo missing_rclone_after_all_bootstraps; exit 52; fi"
            ),
            "command -v rclone",
            "echo __ASI1_REPO_RUNNER_BEFORE_SYNC__",
            (
        f"rclone sync {shlex.quote(s3_root)} {shlex.quote(remote_root)} "
        "--config /tmp/iner-rclone.conf --s3-no-check-bucket "
        "--exclude 'outputs/**' --exclude 'models/**' --exclude 'artifacts/**' "
        "--exclude 'memory/**' --exclude 'logs/**' "
        "--exclude 'browser-automation/profile/**' "
        "--exclude 'browser-automation/*.png' --exclude 'browser-automation/*.html' "
        "--exclude 'browser-automation/*.json' --progress"
            ),
            "echo __ASI1_REPO_RUNNER_AFTER_SYNC__",
            f"cd {shlex.quote(remote_root)}",
        ]
    )
commands.extend(f"export {key}={shlex.quote(value)}" for key, value in env_lines.items())
commands.append("bash scripts/run_asi1_agentic_grpo_from_env.sh")
inner = "\n".join(command for command in commands if command)
encoded_script = base64.b64encode(inner.encode("utf-8")).decode("ascii")
chunks = [encoded_script[index : index + 1800] for index in range(0, len(encoded_script), 1800)]
remote_b64_path = "/tmp/asi1_agentic_grpo_run.b64"
remote_script_path = "/tmp/asi1_agentic_grpo_run.sh"


def comma_free_python(source: str) -> str:
    source = ";".join(line.strip() for line in source.splitlines() if line.strip())
    if "," in source:
        raise ValueError(f"generated python command contains comma: {source}")
    return "python3 -c " + shlex.quote(source)


execution_lines = [
    "set -euo pipefail",
    f"rm -f {remote_b64_path} {remote_script_path}",
]
for chunk in chunks:
    # Huanxin task creation can split codeContents around commas. Keep each
    # shell line comma-free so the UI/API preserves the command exactly.
    append_source = (
        "import pathlib\n"
        f"p=pathlib.Path({remote_b64_path!r})\n"
        "old=p.read_text() if p.exists() else ''\n"
        f"p.write_text(old+{chunk!r})"
  )
    execution_lines.append(comma_free_python(append_source))
decode_source = (
    "import base64\n"
    "import pathlib\n"
    f"src=pathlib.Path({remote_b64_path!r})\n"
    f"dst=pathlib.Path({remote_script_path!r})\n"
    "dst.write_bytes(base64.b64decode(src.read_text()))\n"
    "dst.chmod(0o700)"
)
execution_lines.append(comma_free_python(decode_source))
execution_lines.append(f"bash {remote_script_path}")
execution_command = "\n".join(execution_lines)
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": output_dir,
            "log_path": log_path,
            "job_name": "asi1-agentic-grpo-fast",
            "remote_command": inner,
            "execution_command": execution_command,
            "multi_line_execution_command": execution_command,
            "remote_script_path": remote_script_path,
            "remote_b64_path": remote_b64_path,
            "single_line_execution": True,
            "compact_command": "repo-runner",
            "bootstrap_s3": True,
            "embed_runtime_bundle": embed_runtime_bundle == "1",
            "bootstrap_wheelhouse": bootstrap_wheelhouse == "1",
            "push_results_s3": push_results_s3 == "1",
        },
        indent=2,
    )
)
PY
    return
  fi

  local launch_json
  launch_json="$(
    ASCEND_RT_VISIBLE_DEVICES="$VISIBLE_DEVICES" \
    NPROC_PER_NODE="$NPROC_PER_NODE" \
    GROUP_SIZE="$GROUP_SIZE" \
    GRPO_STEPS="$GRPO_STEPS" \
    MASTER_PORT="$MASTER_PORT" \
    MAX_NEW_TOKENS="$MAX_NEW_TOKENS" \
    MAX_SEQ_LENGTH="$MAX_SEQ_LENGTH" \
    MAX_TURNS="$MAX_TURNS" \
    ONLINE_EVAL_EVERY_STEPS="$ONLINE_EVAL_EVERY_STEPS" \
    ONLINE_EVAL_MAX_TASKS="$ONLINE_EVAL_MAX_TASKS" \
    ONLINE_EVAL_BENCHMARK_FILE="$ONLINE_EVAL_BENCHMARK_FILE" \
    ONLINE_EVAL_TEMPERATURE="$ONLINE_EVAL_TEMPERATURE" \
    CHECKPOINT_INTERVAL_SECONDS="$CHECKPOINT_INTERVAL_SECONDS" \
    CHECKPOINT_EVERY_STEPS="$CHECKPOINT_EVERY_STEPS" \
    ASI1_AGENTIC_TASK_LORA_DROPOUT="$LORA_DROPOUT" \
    ASI1_AGENTIC_TASK_TARGET_MODULES="$TARGET_MODULES" \
    TRAINING_MODE="$TRAINING_MODE" \
    ASI1_AGENTIC_TASK_DOMAIN_FILTER="$DOMAIN_FILTER" \
      bash "$ROOT_DIR/scripts/launch_huanxin_agentic_grpo.sh" \
        --env ASI1 \
        --remote-root "$REMOTE_ROOT" \
        --dry-run \
        --model-name "$MODEL_NAME" \
        --benchmark-file "$BENCHMARK_FILE" \
        --domain-filter "$DOMAIN_FILTER" \
        --output-dir "$OUTPUT_DIR" \
        --log-path "$LOG_PATH" \
        --visible-devices "$VISIBLE_DEVICES" \
        --nproc-per-node "$NPROC_PER_NODE" \
        --group-size "$GROUP_SIZE" \
        --grpo-steps "$GRPO_STEPS" \
        --master-port "$MASTER_PORT" \
        --max-new-tokens "$MAX_NEW_TOKENS" \
        --max-seq-length "$MAX_SEQ_LENGTH" \
        --max-turns "$MAX_TURNS" \
        --online-eval-every-steps "$ONLINE_EVAL_EVERY_STEPS" \
        --online-eval-max-tasks "$ONLINE_EVAL_MAX_TASKS" \
        --online-eval-benchmark-file "$ONLINE_EVAL_BENCHMARK_FILE" \
        --online-eval-temperature "$ONLINE_EVAL_TEMPERATURE" \
        --checkpoint-interval-seconds "$CHECKPOINT_INTERVAL_SECONDS" \
        --checkpoint-every-steps "$CHECKPOINT_EVERY_STEPS" \
        --training-mode "$TRAINING_MODE"
  )"
  if [[ "$EMBED_INLINE_SCRIPT" == "1" ]]; then
    python3 - "$launch_json" "$BOOTSTRAP_WHEELHOUSE" <<'PY'
import base64
import json
import shlex
import sys

payload = json.loads(sys.argv[1])
bootstrap_wheelhouse = sys.argv[2] == "1"
remote_root = payload["remote_root"]
inner_lines = ["set -euo pipefail", f"cd {shlex.quote(remote_root)}"]
if bootstrap_wheelhouse:
    inner_lines.extend(
        [
            "echo __ASI1_BOOTSTRAP_WHEELHOUSE__",
            "test -d tools/wheels",
            "ls -l tools/wheels",
            (
                "python3 -m pip install --no-cache-dir --no-input --no-index "
                "--find-links tools/wheels accelerate==1.4.0 peft==0.14.0"
            ),
            (
                "python3 -c \"import accelerate; import peft; "
                "print('accelerate=' + accelerate.__version__); "
                "print('peft=' + peft.__version__)\""
            ),
        ]
    )
inner_lines.append(payload["remote_command"])
inner = "\n".join(inner_lines)
encoded = base64.b64encode(inner.encode("utf-8")).decode("ascii")
remote_b64_path = "/tmp/asi1_agentic_grpo_inline.b64"
remote_script_path = "/tmp/asi1_agentic_grpo_inline.sh"
execution_lines = [
    "set -euo pipefail",
    f"rm -f {remote_b64_path} {remote_script_path}",
]
for index in range(0, len(encoded), 3600):
    chunk = encoded[index : index + 3600]
    execution_lines.append(
        "python3 -c "
        + shlex.quote(
            "import pathlib\n"
            f"p=pathlib.Path({remote_b64_path!r})\n"
            "old=p.read_text() if p.exists() else ''\n"
            f"p.write_text(old+{chunk!r})"
        )
    )
execution_lines.append(
    "python3 -c "
    + shlex.quote(
        "import base64\n"
        "import pathlib\n"
        f"src=pathlib.Path({remote_b64_path!r})\n"
        f"dst=pathlib.Path({remote_script_path!r})\n"
        "dst.write_bytes(base64.b64decode(src.read_text()))\n"
        "dst.chmod(0o700)"
    )
)
execution_lines.append(f"bash {remote_script_path}")
payload["job_name"] = "asi1-agentic-grpo-fast"
payload["bootstrap_s3"] = False
payload["bootstrap_wheelhouse"] = bootstrap_wheelhouse
payload["push_results_s3"] = False
payload["compact_command"] = "embed-inline-script"
payload["execution_command"] = "\n".join(execution_lines)
payload["remote_script_path"] = remote_script_path
payload["remote_b64_path"] = remote_b64_path
payload["embed_inline_script"] = True
print(json.dumps(payload, indent=2))
PY
    return
  fi
  python3 - "$launch_json" "$BOOTSTRAP_S3" "$BOOTSTRAP_WHEELHOUSE" "$PUSH_RESULTS_S3" "$COMPACT_COMMAND" <<'PY'
import base64
import json
import shlex
import sys

payload = json.loads(sys.argv[1])
bootstrap_s3, bootstrap_wheelhouse, push_results_s3, compact_command = sys.argv[2:6]
remote_root = payload["remote_root"]
remote_command = payload["remote_command"]
if bootstrap_wheelhouse == "1":
    install_wheels = (
        "echo __ASI1_BOOTSTRAP_WHEELHOUSE__ && "
        "test -d tools/wheels && "
        "ls -l tools/wheels && "
        "python3 -m pip install --no-cache-dir --no-input --no-index "
        "--find-links tools/wheels accelerate==1.4.0 peft==0.14.0 && "
        "python3 -c \"import accelerate; import peft; "
        "print('accelerate=' + accelerate.__version__); "
        "print('peft=' + peft.__version__)\""
    )
    remote_command = install_wheels + " && " + remote_command
payload["job_name"] = "asi1-agentic-grpo-fast"
payload["bootstrap_s3"] = bootstrap_s3 == "1"
payload["bootstrap_wheelhouse"] = bootstrap_wheelhouse == "1"
payload["push_results_s3"] = push_results_s3 == "1"
payload["compact_command"] = "inline" if compact_command == "1" else "full"
inner = "\n".join(
    [
        "set -euo pipefail",
        f"cd {shlex.quote(remote_root)}",
        remote_command,
    ]
)
if compact_command == "1":
    encoded = base64.b64encode(inner.encode("utf-8")).decode("ascii")
    chunks = [encoded[index : index + 240] for index in range(0, len(encoded), 240)]
    remote_b64_path = "/tmp/asi1_agentic_grpo_run_inline.b64"
    remote_script_path = "/tmp/asi1_agentic_grpo_run_inline.sh"

    def comma_free_python(source: str) -> str:
        source = ";".join(line.strip() for line in source.splitlines() if line.strip())
        if "," in source:
            raise ValueError(f"generated python command contains comma: {source}")
        return "python3 -c " + shlex.quote(source)

    lines = ["set -euo pipefail", f"rm -f {remote_b64_path} {remote_script_path}"]
    for chunk in chunks:
        append_source = (
            "import pathlib\n"
            f"p=pathlib.Path({remote_b64_path!r})\n"
            "old=p.read_text() if p.exists() else ''\n"
            f"p.write_text(old+{chunk!r})"
        )
        lines.append(comma_free_python(append_source))
    decode_source = (
        "import base64\n"
        "import pathlib\n"
        f"src=pathlib.Path({remote_b64_path!r})\n"
        f"dst=pathlib.Path({remote_script_path!r})\n"
        "dst.write_bytes(base64.b64decode(src.read_text()))\n"
        "dst.chmod(0o700)"
    )
    lines.append(comma_free_python(decode_source))
    lines.append(f"bash {remote_script_path}")
    payload["execution_command"] = "\n".join(lines)
    payload["remote_script_path"] = remote_script_path
    payload["remote_b64_path"] = remote_b64_path
elif compact_command == "raw":
    payload["compact_command"] = "raw"
    payload["execution_command"] = inner
    payload["remote_script_path"] = None
else:
    compact_command = "shell-b64"
    encoded = base64.b64encode(inner.encode("utf-8")).decode("ascii")
    runner = (
        "b=__import__('base64');"
        "p=__import__('pathlib').Path('/tmp/asi1_agentic_grpo_run_full.sh');"
        f"p.write_bytes(b.b64decode({encoded!r}));"
        "p.chmod(0o700);"
        "s=__import__('subprocess');"
        "raise SystemExit(s.run(['bash']+[str(p)]).returncode)"
    )
    payload["compact_command"] = "shell-b64"
    payload["execution_command"] = f"python3 -c {shlex.quote(runner)}"
    payload["remote_script_path"] = "/tmp/asi1_agentic_grpo_run_full.sh"
print(json.dumps(payload, indent=2))
PY
}

if [[ "${1:-}" == "--dry-run" && "${2:-}" == "__launch-spec" ]]; then
  render_launch_spec
  exit 0
fi

if [[ "${1:-}" == "__launch-spec" ]]; then
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
    --model-name)
      MODEL_NAME="${2:-}"
      shift 2
      ;;
    --benchmark-file)
      BENCHMARK_FILE="${2:-}"
      shift 2
      ;;
    --domain-filter)
      DOMAIN_FILTER="${2:-}"
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
    --artifact-stem)
      ARTIFACT_STEM="${2:-}"
      shift 2
      ;;
    --wait-ms)
      WAIT_MS="${2:-}"
      shift 2
      ;;
    --image-name)
      IMAGE_NAME="${2:-}"
      shift 2
      ;;
    --accelerator-cards)
      ACCELERATOR_CARDS="${2:-}"
      shift 2
      ;;
    --cpu-cores)
      CPU_CORES="${2:-}"
      shift 2
      ;;
    --memory-gb)
      MEMORY_GB="${2:-}"
      shift 2
      ;;
    --visible-devices)
      VISIBLE_DEVICES="${2:-}"
      shift 2
      ;;
    --nproc-per-node)
      NPROC_PER_NODE="${2:-}"
      shift 2
      ;;
    --group-size)
      GROUP_SIZE="${2:-}"
      shift 2
      ;;
    --grpo-steps)
      GRPO_STEPS="${2:-}"
      shift 2
      ;;
    --master-port)
      MASTER_PORT="${2:-}"
      shift 2
      ;;
    --max-new-tokens)
      MAX_NEW_TOKENS="${2:-}"
      shift 2
      ;;
    --max-seq-length)
      MAX_SEQ_LENGTH="${2:-}"
      shift 2
      ;;
    --max-turns)
      MAX_TURNS="${2:-}"
      shift 2
      ;;
    --online-eval-every-steps)
      ONLINE_EVAL_EVERY_STEPS="${2:-}"
      shift 2
      ;;
    --online-eval-max-tasks)
      ONLINE_EVAL_MAX_TASKS="${2:-}"
      shift 2
      ;;
    --online-eval-benchmark-file)
      ONLINE_EVAL_BENCHMARK_FILE="${2:-}"
      shift 2
      ;;
    --online-eval-temperature)
      ONLINE_EVAL_TEMPERATURE="${2:-}"
      shift 2
      ;;
    --checkpoint-interval-seconds)
      CHECKPOINT_INTERVAL_SECONDS="${2:-}"
      shift 2
      ;;
    --checkpoint-every-steps)
      CHECKPOINT_EVERY_STEPS="${2:-}"
      shift 2
      ;;
    --lora-rank)
      LORA_RANK="${2:-}"
      shift 2
      ;;
    --lora-alpha)
      LORA_ALPHA="${2:-}"
      shift 2
      ;;
    --lora-dropout)
      LORA_DROPOUT="${2:-}"
      shift 2
      ;;
    --target-modules)
      TARGET_MODULES="${2:-}"
      shift 2
      ;;
    --train-layernorm)
      TRAIN_LAYER_NORM="${2:-}"
      shift 2
      ;;
    --min-trainable-parameters)
      MIN_TRAINABLE_PARAMETERS="${2:-}"
      shift 2
      ;;
    --max-trainable-parameters)
      MAX_TRAINABLE_PARAMETERS="${2:-}"
      shift 2
      ;;
    --research-methods)
      RESEARCH_METHODS="${2:-}"
      shift 2
      ;;
    --training-mode)
      TRAINING_MODE="${2:-}"
      shift 2
      ;;
    --hours)
      shift 2
      ;;
    --bootstrap-s3)
      BOOTSTRAP_S3=1
      shift
      ;;
    --bootstrap-bundle-url)
      BOOTSTRAP_BUNDLE_URL="${2:-}"
      shift 2
      ;;
    --bootstrap-bundle-sha256)
      BOOTSTRAP_BUNDLE_SHA256="${2:-}"
      shift 2
      ;;
    --bootstrap-bundle-name)
      BOOTSTRAP_BUNDLE_NAME="${2:-}"
      shift 2
      ;;
    --bootstrap-wheelhouse)
      BOOTSTRAP_WHEELHOUSE=1
      shift
      ;;
    --embed-wheelhouse)
      EMBED_WHEELHOUSE=1
      BOOTSTRAP_WHEELHOUSE=1
      COMPACT_COMMAND=embedded-wheelhouse
      shift
      ;;
    --push-results-s3)
      PUSH_RESULTS_S3=1
      shift
      ;;
    --override-command-file)
      OVERRIDE_COMMAND_FILE="${2:-}"
      shift 2
      ;;
    --direct-submit-only)
      DIRECT_SUBMIT_ONLY=1
      shift
      ;;
    --inline-compact-command)
      COMPACT_COMMAND=1
      shift
      ;;
    --repo-runner-command)
      COMPACT_COMMAND=repo-runner
      BOOTSTRAP_S3=1
      shift
      ;;
    --embed-runtime-bundle)
      EMBED_RUNTIME_BUNDLE=1
      COMPACT_COMMAND=repo-runner
      BOOTSTRAP_S3=0
      shift
      ;;
    --runtime-bundle-path)
      RUNTIME_BUNDLE_PATH="${2:-}"
      shift 2
      ;;
    --embed-inline-script)
      EMBED_INLINE_SCRIPT=1
      shift
      ;;
    --full-command)
      COMPACT_COMMAND=0
      shift
      ;;
    --raw-command)
      COMPACT_COMMAND=raw
      shift
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

export ASI1_AGENTIC_TASK_REMOTE_ROOT="$REMOTE_ROOT"
export ASI1_AGENTIC_TASK_MODEL_NAME="$MODEL_NAME"
export ASI1_AGENTIC_TASK_BENCHMARK_FILE="$BENCHMARK_FILE"
export ASI1_AGENTIC_TASK_DOMAIN_FILTER="$DOMAIN_FILTER"
export ASI1_AGENTIC_TASK_VISIBLE_DEVICES="$VISIBLE_DEVICES"
export ASI1_AGENTIC_TASK_NPROC_PER_NODE="$NPROC_PER_NODE"
export ASI1_AGENTIC_TASK_GROUP_SIZE="$GROUP_SIZE"
export ASI1_AGENTIC_TASK_GRPO_STEPS="$GRPO_STEPS"
export ASI1_AGENTIC_TASK_MASTER_PORT="$MASTER_PORT"
export ASI1_AGENTIC_TASK_MAX_NEW_TOKENS="$MAX_NEW_TOKENS"
export ASI1_AGENTIC_TASK_MAX_SEQ_LENGTH="$MAX_SEQ_LENGTH"
export ASI1_AGENTIC_TASK_MAX_TURNS="$MAX_TURNS"
export ASI1_AGENTIC_TASK_ONLINE_EVAL_EVERY_STEPS="$ONLINE_EVAL_EVERY_STEPS"
export ASI1_AGENTIC_TASK_ONLINE_EVAL_MAX_TASKS="$ONLINE_EVAL_MAX_TASKS"
export ASI1_AGENTIC_TASK_ONLINE_EVAL_BENCHMARK_FILE="$ONLINE_EVAL_BENCHMARK_FILE"
export ASI1_AGENTIC_TASK_ONLINE_EVAL_TEMPERATURE="$ONLINE_EVAL_TEMPERATURE"
export ASI1_AGENTIC_TASK_CHECKPOINT_INTERVAL_SECONDS="$CHECKPOINT_INTERVAL_SECONDS"
export ASI1_AGENTIC_TASK_CHECKPOINT_EVERY_STEPS="$CHECKPOINT_EVERY_STEPS"
export ASI1_AGENTIC_TASK_LORA_RANK="$LORA_RANK"
export ASI1_AGENTIC_TASK_LORA_ALPHA="$LORA_ALPHA"
export ASI1_AGENTIC_TASK_LORA_DROPOUT="$LORA_DROPOUT"
export ASI1_AGENTIC_TASK_TARGET_MODULES="$TARGET_MODULES"
export ASI1_AGENTIC_TASK_TRAIN_LAYER_NORM="$TRAIN_LAYER_NORM"
export ASI1_AGENTIC_TASK_MIN_TRAINABLE_PARAMETERS="$MIN_TRAINABLE_PARAMETERS"
export ASI1_AGENTIC_TASK_MAX_TRAINABLE_PARAMETERS="$MAX_TRAINABLE_PARAMETERS"
export ASI1_AGENTIC_TASK_RESEARCH_METHODS="$RESEARCH_METHODS"
export ASI1_AGENTIC_TASK_TRAINING_MODE="$TRAINING_MODE"
export ASI1_AGENTIC_TASK_BOOTSTRAP_S3="$BOOTSTRAP_S3"
export ASI1_AGENTIC_TASK_BOOTSTRAP_BUNDLE_URL="$BOOTSTRAP_BUNDLE_URL"
export ASI1_AGENTIC_TASK_BOOTSTRAP_BUNDLE_SHA256="$BOOTSTRAP_BUNDLE_SHA256"
export ASI1_AGENTIC_TASK_BOOTSTRAP_BUNDLE_NAME="$BOOTSTRAP_BUNDLE_NAME"
export ASI1_AGENTIC_TASK_EMBED_RUNTIME_BUNDLE="$EMBED_RUNTIME_BUNDLE"
export ASI1_AGENTIC_TASK_RUNTIME_BUNDLE_PATH="$RUNTIME_BUNDLE_PATH"
export ASI1_AGENTIC_TASK_BOOTSTRAP_WHEELHOUSE="$BOOTSTRAP_WHEELHOUSE"
export ASI1_AGENTIC_TASK_PUSH_RESULTS_S3="$PUSH_RESULTS_S3"
export ASI1_AGENTIC_TASK_COMPACT_COMMAND="$COMPACT_COMMAND"
export ASI1_AGENTIC_TASK_EMBED_WHEELHOUSE="$EMBED_WHEELHOUSE"
export ASI1_AGENTIC_TASK_OUTPUT_DIR="$OUTPUT_DIR"
export ASI1_AGENTIC_TASK_LOG_PATH="$LOG_PATH"

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
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_agentic_grpo_task.sh"
  --launcher-arg "__launch-spec"
  --output-dir "$OUTPUT_DIR"
  --log-path "$LOG_PATH"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
  --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
)

if [[ -n "$OVERRIDE_COMMAND_FILE" ]]; then
  CMD+=(--override-command-file "$OVERRIDE_COMMAND_FILE")
fi
if [[ "$DIRECT_SUBMIT_ONLY" == "1" ]]; then
  CMD+=(--direct-submit-only)
fi

if [[ "${HUANXIN_AUTO_OVERRIDE_CODECONTENTS:-1}" == "0" ]]; then
  CMD+=(--no-auto-codecontents-override)
fi

if [[ "$SUBMIT" == "1" ]]; then
  CMD+=(--submit)
fi

if [[ "$PRINT_ONLY" == "1" ]]; then
  shell_quote "${CMD[@]}"
  exit 0
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
