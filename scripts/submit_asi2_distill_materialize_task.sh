#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"

ENV_NAME="${ASI2_DISTILL_ENV:-ASI2}"
REMOTE_ROOT="${ASI2_DISTILL_REMOTE_ROOT:-/vllm-workspace/quantum-gpt}"
TASK_NAME="${ASI2_DISTILL_TASK_NAME:-asi2-distill-seed}"
IMAGE_NAME="${ASI2_DISTILL_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI2_DISTILL_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI2_DISTILL_RESOURCE_GROUP_TYPE:-公共资源组}"
TASK_PRIORITY="${ASI2_DISTILL_TASK_PRIORITY:-中}"
INSTANCE_COUNT="${ASI2_DISTILL_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI2_DISTILL_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI2_DISTILL_CPU_CORES:-20}"
MEMORY_GB="${ASI2_DISTILL_MEMORY_GB:-240}"
WAIT_MS="${ASI2_DISTILL_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI2_DISTILL_ARTIFACT_STEM:-huanxin-submit-task-run-asi2-distill-seed}"
TRAIN_DEV_URL="${ASI2_DISTILL_URL:-}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi2_distill_materialize_task.sh [--submit] [options]

Submits or dry-renders an ASI2 Huanxin task that materializes the RAG
distillation seed artifacts from INER S3 into /vllm-workspace/quantum-gpt.

Options:
  --submit
  --dry-run
  --task-name <name>
  --remote-root <path>
  --artifact-stem <stem>
  --wait-ms <ms>
  --image-name <name>
  --resource-group <name>
  --resource-group-type <label>
  --instance-count <n>
  --accelerator-cards <n>
  --cpu-cores <n>
  --memory-gb <n>
EOF
}

default_train_dev_url() {
  "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$ENV_NAME" --field train_dev_url 2>/dev/null \
    || python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$ENV_NAME" --field train_dev_url
}

render_launch_spec() {
  local remote_config="/tmp/iner-rclone.conf"
  local remote_setup
  remote_setup="$(iner_remote_rclone_setup_script "$remote_config")"
  python3 - <<'PY' "$REMOTE_ROOT" "${HUANXIN_S3_ROOT:-$INER_S3_ROOT}" "$remote_config" "$remote_setup"
import json
import shlex
import sys

remote_root, s3_root, remote_config, remote_setup = sys.argv[1:5]
files = [
    "scripts/build_quantum_distillation_seed_questions.py",
    "tests/test_build_quantum_distillation_seed_questions.py",
    "data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl",
    "data/seed/quantum_distillation_seed_questions_asi2_v1_manifest.json",
]
commands = [
    "set -euo pipefail",
    "echo __ASI2_DISTILL_MATERIALIZE_START__",
    "pwd",
    "python3 --version",
    "mkdir -p /tmp/asi2-distill-tools",
    remote_setup,
    "if ! command -v rclone >/dev/null 2>&1; then "
    "candidate_version=$(apt-cache policy rclone | sed -n 's/^  Candidate: //p' | head -n 1); "
    "test -n \"$candidate_version\" || candidate_version='1.53.3-4ubuntu1.22.04.3'; "
    "arch=$(dpkg --print-architecture); "
    "deb_url=\"https://ports.ubuntu.com/ubuntu-ports/pool/universe/r/rclone/rclone_${candidate_version}_${arch}.deb\"; "
    "curl -fsSL \"$deb_url\" -o /tmp/asi2-distill-tools/rclone.deb; "
    "dpkg -i /tmp/asi2-distill-tools/rclone.deb; "
    "fi",
    "command -v rclone",
    "rclone version | sed -n '1,2p'",
    f"mkdir -p {shlex.quote(remote_root)}",
]
for rel_path in files:
    source = f"{s3_root}/{rel_path}"
    dest = f"{remote_root}/{rel_path}"
    commands.append(f"mkdir -p {shlex.quote(dest.rsplit('/', 1)[0])}")
    commands.append(
        "rclone copyto "
        f"{shlex.quote(source)} {shlex.quote(dest)} "
        f"--config {shlex.quote(remote_config)} --s3-no-check-bucket"
    )
commands.extend(
    [
        f"cd {shlex.quote(remote_root)}",
        "python3 - <<'PYVERIFY'\n"
        "import json\n"
        "from pathlib import Path\n"
        "jsonl = Path('data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl')\n"
        "manifest = Path('data/seed/quantum_distillation_seed_questions_asi2_v1_manifest.json')\n"
        "rows = sum(1 for line in jsonl.read_text(encoding='utf-8').splitlines() if line.strip())\n"
        "payload = json.loads(manifest.read_text(encoding='utf-8'))\n"
        "assert rows == 360, rows\n"
        "assert payload['summary']['target_env'] == 'ASI2'\n"
        "assert payload['summary']['distillation_strategy'] == 'hard_sft_black_box_teacher'\n"
        "report = {'ok': True, 'rows': rows, 'target_env': payload['summary']['target_env'], 'remote_root': str(Path.cwd())}\n"
        "Path('reports').mkdir(exist_ok=True)\n"
        "Path('reports/asi2_distill_materialize_seed_v1.json').write_text(json.dumps(report, indent=2) + '\\n', encoding='utf-8')\n"
        "print(json.dumps(report, sort_keys=True))\n"
        "PYVERIFY",
        "echo __ASI2_DISTILL_MATERIALIZE_DONE__",
    ]
)
execution_command = "\n".join(commands)
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": "asi2-distill-seed",
            "remote_command": execution_command,
            "execution_command": execution_command,
        },
        indent=2,
    )
)
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
    --resource-group)
      RESOURCE_GROUP="${2:-}"
      shift 2
      ;;
    --resource-group-type)
      RESOURCE_GROUP_TYPE="${2:-}"
      shift 2
      ;;
    --instance-count)
      INSTANCE_COUNT="${2:-}"
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
  --launcher-script "$ROOT_DIR/scripts/submit_asi2_distill_materialize_task.sh"
  --launcher-arg "__launch-spec"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
  --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
)

if [[ "$SUBMIT" == "1" ]]; then
  CMD+=(--submit)
fi

if [[ "$PRINT_ONLY" == "1" ]]; then
  printf '%q ' "${CMD[@]}"
  printf '\n'
  exit 0
fi

"${CMD[@]}"
