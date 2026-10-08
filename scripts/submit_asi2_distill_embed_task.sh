#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ENV_NAME="${ASI2_DISTILL_ENV:-ASI2}"
REMOTE_ROOT="${ASI2_DISTILL_REMOTE_ROOT:-/vllm-workspace/quantum-gpt}"
TASK_NAME="${ASI2_DISTILL_TASK_NAME:-asi2-distill-embed}"
IMAGE_NAME="${ASI2_DISTILL_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI2_DISTILL_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI2_DISTILL_RESOURCE_GROUP_TYPE:-公共资源组}"
TASK_PRIORITY="${ASI2_DISTILL_TASK_PRIORITY:-中}"
INSTANCE_COUNT="${ASI2_DISTILL_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI2_DISTILL_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI2_DISTILL_CPU_CORES:-20}"
MEMORY_GB="${ASI2_DISTILL_MEMORY_GB:-240}"
WAIT_MS="${ASI2_DISTILL_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI2_DISTILL_ARTIFACT_STEM:-huanxin-submit-task-run-asi2-distill-embed}"
TRAIN_DEV_URL="${ASI2_DISTILL_URL:-}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi2_distill_embed_task.sh [--submit] [options]

Submit an ASI2 task that embeds gzip+base64 distillation seed artifacts into
the task command and verifies the materialized dataset on remote.
EOF
}

default_train_dev_url() {
  "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$ENV_NAME" --field train_dev_url 2>/dev/null \
    || python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env "$ENV_NAME" --field train_dev_url
}

render_launch_spec() {
  python3 - <<'PY' "$ROOT_DIR" "$REMOTE_ROOT"
import base64
import gzip
import hashlib
import json
import shlex
import sys
from pathlib import Path

root = Path(sys.argv[1])
remote_root = sys.argv[2]
files = [
    "scripts/build_quantum_distillation_seed_questions.py",
    "tests/test_build_quantum_distillation_seed_questions.py",
    "data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl",
    "data/seed/quantum_distillation_seed_questions_asi2_v1_manifest.json",
]

commands = [
    "set -euo pipefail",
    "echo __ASI2_DISTILL_EMBED_START__",
    "pwd",
    "python3 --version",
    f"mkdir -p {shlex.quote(remote_root)}",
    "mkdir -p /tmp/asi2-distill-embed",
]
sha_map = {}
for index, rel_path in enumerate(files):
    local_path = root / rel_path
    raw = local_path.read_bytes()
    sha_map[rel_path] = hashlib.sha256(raw).hexdigest()
    encoded = base64.b64encode(gzip.compress(raw, compresslevel=9)).decode("ascii")
    tmp_b64 = f"/tmp/asi2-distill-embed/file_{index}.b64"
    dest = f"{remote_root}/{rel_path}"
    commands.append(f"rm -f {shlex.quote(tmp_b64)}")
    for offset in range(0, len(encoded), 3500):
        commands.append(f"printf '%s' {shlex.quote(encoded[offset:offset + 3500])} >> {shlex.quote(tmp_b64)}")
    commands.append(f"mkdir -p {shlex.quote(dest.rsplit('/', 1)[0])}")
    commands.append(
        "python3 - <<'PYDECODE'\n"
        "import base64, gzip, pathlib\n"
        f"src = pathlib.Path({tmp_b64!r})\n"
        f"dst = pathlib.Path({dest!r})\n"
        "dst.write_bytes(gzip.decompress(base64.b64decode(src.read_text())))\n"
        "PYDECODE"
    )

commands.extend(
    [
        f"cd {shlex.quote(remote_root)}",
        "python3 - <<'PYVERIFY'\n"
        "import hashlib, json\n"
        "from pathlib import Path\n"
        f"expected = {json.dumps(sha_map, sort_keys=True)!r}\n"
        "for rel, sha in expected.items():\n"
        "    actual = hashlib.sha256(Path(rel).read_bytes()).hexdigest()\n"
        "    assert actual == sha, (rel, actual, sha)\n"
        "jsonl = Path('data/seed/quantum_distillation_seed_questions_asi2_v1.jsonl')\n"
        "manifest = Path('data/seed/quantum_distillation_seed_questions_asi2_v1_manifest.json')\n"
        "rows = sum(1 for line in jsonl.read_text(encoding='utf-8').splitlines() if line.strip())\n"
        "payload = json.loads(manifest.read_text(encoding='utf-8'))\n"
        "assert rows == 360, rows\n"
        "assert payload['summary']['target_env'] == 'ASI2'\n"
        "report = {'ok': True, 'rows': rows, 'target_env': payload['summary']['target_env'], 'remote_root': str(Path.cwd())}\n"
        "Path('reports').mkdir(exist_ok=True)\n"
        "Path('reports/asi2_distill_embed_seed_v1.json').write_text(json.dumps(report, indent=2) + '\\n', encoding='utf-8')\n"
        "print(json.dumps(report, sort_keys=True))\n"
        "PYVERIFY",
        "echo __ASI2_DISTILL_EMBED_DONE__",
    ]
)
execution_command = "\n".join(commands)
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": "asi2-distill-embed",
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
  --launcher-script "$ROOT_DIR/scripts/submit_asi2_distill_embed_task.sh"
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
