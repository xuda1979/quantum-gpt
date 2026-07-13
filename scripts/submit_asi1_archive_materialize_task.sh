#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

TASK_NAME="${ASI1_ARCHIVE_TASK_NAME:-asi1-archive-0524}"
IMAGE_NAME="${ASI1_ARCHIVE_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_ARCHIVE_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_ARCHIVE_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_ARCHIVE_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_ARCHIVE_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI1_ARCHIVE_CPU_CORES:-4}"
MEMORY_GB="${ASI1_ARCHIVE_MEMORY_GB:-16}"
WAIT_MS="${ASI1_ARCHIVE_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_ARCHIVE_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-archive-20260524}"
TRAIN_DEV_URL="${ASI1_ARCHIVE_URL:-}"
REMOTE_ROOT="${ASI1_ARCHIVE_REMOTE_ROOT:-/workspace}"
DEST_DIR="${ASI1_ARCHIVE_DEST_DIR:-/workspace/quantum-gpt-archive/20260524}"
ARCHIVE_OBJECT="${ASI1_ARCHIVE_OBJECT:-software/quantum-gpt-archives/quantum-gpt-large-local-archive-20260524.tar.gz}"
ARCHIVE_NAME="${ASI1_ARCHIVE_NAME:-quantum-gpt-large-local-archive-20260524.tar.gz}"
ARCHIVE_SHA256="${ASI1_ARCHIVE_SHA256:-e1fe68fc290518be96f03c85a6c1998f8821f62de2869135b150b5d5c9a7ba9f}"
EXTRACT_MODE="${ASI1_ARCHIVE_EXTRACT_MODE:-archive}"
SIGNED_URL="${ASI1_ARCHIVE_SIGNED_URL:-}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_archive_materialize_task.sh [--submit] [options]

Fills or submits an ASI1 Huanxin task that downloads an archive from INER S3,
verifies SHA256, and extracts it on ASI1.
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  (
    cd "$ROOT_DIR"
    source scripts/iner_s3_env.sh
    tmp_cfg="$(mktemp /tmp/iner-rclone.XXXXXX)"
    trap 'rm -f "$tmp_cfg"' EXIT
    iner_write_rclone_config "$tmp_cfg"
    signed_url="$SIGNED_URL"
    if [[ -z "$signed_url" ]]; then
      if [[ -z "$RCLONE_BIN" ]]; then
        echo "rclone not found. Set RCLONE_BIN or install rclone." >&2
        exit 127
      fi
      signed_url="$("$RCLONE_BIN" link "iner:${INER_S3_BUCKET}/${ARCHIVE_OBJECT}" --config "$tmp_cfg" --s3-no-check-bucket)"
    fi
    python3 - <<'PY' "$REMOTE_ROOT" "$DEST_DIR" "$ARCHIVE_NAME" "$ARCHIVE_SHA256" "$signed_url" "$EXTRACT_MODE"
import base64
import json
import shlex
import sys

remote_root, dest_dir, archive_name, expected_sha, signed_url, extract_mode = sys.argv[1:7]
url_b64 = base64.b64encode(signed_url.encode("utf-8")).decode("ascii")
commands = [
    "set -euo pipefail",
    "echo __ASI1_ARCHIVE_MATERIALIZE_START__",
    "pwd",
    "whoami",
    "python3 --version",
    f"mkdir -p {shlex.quote(dest_dir)}",
    f"cd {shlex.quote(dest_dir)}",
    f"rm -f {shlex.quote(archive_name)}",
    f"url=$(python3 -c {shlex.quote('import base64;print(base64.b64decode(' + repr(url_b64) + ').decode())')})",
    f"curl -fL --retry 5 --connect-timeout 30 --max-time 300 \"$url\" -o {shlex.quote(archive_name)}",
    f"sha256sum {shlex.quote(archive_name)}",
    f"echo {shlex.quote(expected_sha + '  ' + archive_name)} | sha256sum -c -",
]
if extract_mode == "direct":
    commands.extend(
        [
            f"tar -xzf {shlex.quote(archive_name)} -C {shlex.quote(dest_dir)}",
            "mkdir -p scripts evals/benchmarks",
            "for f in run_asi1_agentic_grpo_from_env.sh iner_s3_env.sh append_text_file.py decode_base64_file.py; do test ! -f \"$f\" || mv -f \"$f\" scripts/; done",
            "test ! -d benchmarks || cp -R benchmarks/. evals/benchmarks/",
            "test -f scripts/run_asi1_agentic_grpo_from_env.sh",
            "test -f training/agentic_grpo_trainer.py",
            "test -f evals/benchmarks/agentic_coding_trajectory_training_v1.txt",
            "chmod +x scripts/run_asi1_agentic_grpo_from_env.sh",
            "find scripts training evals/benchmarks -maxdepth 2 -type f | wc -l",
        ]
    )
else:
    commands.extend(
        [
            "rm -rf extracted",
            "mkdir -p extracted",
            f"tar -xzf {shlex.quote(archive_name)} -C extracted",
            "du -sh extracted extracted/outputs extracted/artifacts/runtime-bundles extracted/artifacts/quantum-rag extracted/artifacts/branch-switch-backups extracted/artifacts/downloads",
            "find extracted/outputs extracted/artifacts/runtime-bundles extracted/artifacts/quantum-rag extracted/artifacts/branch-switch-backups extracted/artifacts/downloads -type f | wc -l",
        ]
    )
commands.append("echo __ASI1_ARCHIVE_MATERIALIZE_DONE__")
execution_command = "; ".join([commands[0], f"cd {shlex.quote(remote_root)}", *commands[1:]])
print(
    json.dumps(
        {
            "remote_root": remote_root,
            "output_dir": "",
            "log_path": "",
            "job_name": "asi1-archive-materialize",
            "extract_mode": extract_mode,
            "remote_command": execution_command,
            "execution_command": execution_command,
        },
        indent=2,
    )
)
PY
  )
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
    --remote-root) REMOTE_ROOT="${2:-}"; shift 2 ;;
    --dest-dir) DEST_DIR="${2:-}"; shift 2 ;;
    --artifact-stem) ARTIFACT_STEM="${2:-}"; shift 2 ;;
    --wait-ms) WAIT_MS="${2:-}"; shift 2 ;;
    --image-name) IMAGE_NAME="${2:-}"; shift 2 ;;
    --resource-group) RESOURCE_GROUP="${2:-}"; shift 2 ;;
    --resource-group-type) RESOURCE_GROUP_TYPE="${2:-}"; shift 2 ;;
    --instance-count) INSTANCE_COUNT="${2:-}"; shift 2 ;;
    --accelerator-cards) ACCELERATOR_CARDS="${2:-}"; shift 2 ;;
    --cpu-cores) CPU_CORES="${2:-}"; shift 2 ;;
    --memory-gb) MEMORY_GB="${2:-}"; shift 2 ;;
    --archive-object) ARCHIVE_OBJECT="${2:-}"; shift 2 ;;
    --archive-name) ARCHIVE_NAME="${2:-}"; shift 2 ;;
    --archive-sha256) ARCHIVE_SHA256="${2:-}"; shift 2 ;;
    --signed-url) SIGNED_URL="${2:-}"; shift 2 ;;
    --extract-mode) EXTRACT_MODE="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

export ASI1_ARCHIVE_REMOTE_ROOT="$REMOTE_ROOT"
export ASI1_ARCHIVE_DEST_DIR="$DEST_DIR"
export ASI1_ARCHIVE_OBJECT="$ARCHIVE_OBJECT"
export ASI1_ARCHIVE_NAME="$ARCHIVE_NAME"
export ASI1_ARCHIVE_SHA256="$ARCHIVE_SHA256"
export ASI1_ARCHIVE_EXTRACT_MODE="$EXTRACT_MODE"
export ASI1_ARCHIVE_SIGNED_URL="$SIGNED_URL"

CMD=(
  node
  "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
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
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_archive_materialize_task.sh"
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
