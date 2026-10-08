#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
REMOTE_ROOT="/root/work/quantum-gpt"

cd "$ROOT_DIR"

DRY_RUN=0
ALLOW_BULKY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --all)
      ALLOW_BULKY=1
      shift
      ;;
    *)
      break
      ;;
  esac
done

REMOTE_PATHS=("$@")
if [[ ${#REMOTE_PATHS[@]} -eq 0 ]]; then
  REMOTE_PATHS=(.)
fi

build_copy_cmd() {
  local src="$1"
  local dest="$2"
  shift 2
  local args=(rclone copy "$src" "$dest" --s3-no-check-bucket --fast-list --progress)
  while [[ $# -gt 0 ]]; do
    args+=("$1")
    shift
  done
  printf '%q ' "${args[@]}"
}

BASE_EXCLUDES=(
  --exclude ".git/**"
  --exclude "__pycache__/**"
  --exclude ".pytest_cache/**"
  --exclude ".mypy_cache/**"
  --exclude ".ruff_cache/**"
  --exclude "*.pyc"
  --exclude "*.npy"
  --exclude "node_modules/**"
  --exclude ".venv/**"
  --exclude "venv/**"
  --exclude "browser-automation/profile/**"
)

BULKY_EXCLUDES=(
  --exclude "outputs/**"
  --exclude "models/**"
  --exclude "artifacts/**"
  --exclude "memory/**"
  --exclude "logs/**"
  --exclude "browser-automation/*.png"
  --exclude "browser-automation/*.html"
  --exclude "browser-automation/*.json"
  --exclude "*.pt"
  --exclude "*.pth"
  --exclude "*.bin"
  --exclude "*.safetensors"
  --exclude "*.ckpt"
  --exclude "*.tar"
  --exclude "*.zip"
)

if [[ $DRY_RUN -eq 1 ]]; then
  BASE_EXCLUDES+=(--dry-run)
fi

run_local_or_remote() {
  local remote_cmd="$1"
  if [[ "$(uname -s)" == "Linux" && "$ROOT_DIR" == "$REMOTE_ROOT" ]]; then
    eval "$remote_cmd"
    return 0
  fi

  local json_out
  json_out="$(bash scripts/ai2_fast_path.sh exec "$remote_cmd")"
  python3 - <<'PY' "$json_out"
import json
import re
import sys

payload = json.loads(sys.argv[1])
combined = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
matches = re.findall(r"__AI2_PUSH_TO_S3_RC__:[^:]+:(\d+)", combined)
if not matches:
    raise SystemExit(f"Did not observe push completion marker.\n{combined}")
if any(code != "0" for code in matches):
    raise SystemExit(combined)
PY
}

for remote_path in "${REMOTE_PATHS[@]}"; do
  label="${remote_path//[^A-Za-z0-9._-]/_}"
  exclude_args=("${BASE_EXCLUDES[@]}")
  if [[ "$remote_path" == "." && $ALLOW_BULKY -eq 0 ]]; then
    exclude_args+=("${BULKY_EXCLUDES[@]}")
    copy_cmd="$(build_copy_cmd "$REMOTE_ROOT" "$S3_ROOT" "${exclude_args[@]}")"
    remote_log="/tmp/ai2_push_to_s3_${label}.log"
    remote_cmd="cd '$REMOTE_ROOT' && { ${copy_cmd}; } >'$remote_log' 2>&1; rc=\$?; echo __AI2_PUSH_TO_S3_RC__:${label}:\$rc; tail -n 40 '$remote_log'"
    run_local_or_remote "$remote_cmd"
    continue
  fi

  copy_cmd="$(build_copy_cmd "$remote_path" "$S3_ROOT/$remote_path" "${exclude_args[@]}")"
  remote_log="/tmp/ai2_push_to_s3_${label}.log"
  remote_cmd="cd '$REMOTE_ROOT' && if [[ -e '$remote_path' ]]; then { ${copy_cmd}; } >'$remote_log' 2>&1; rc=\$?; echo __AI2_PUSH_TO_S3_RC__:${label}:\$rc; tail -n 40 '$remote_log'; else echo 'skip missing: $remote_path'; echo __AI2_PUSH_TO_S3_RC__:${label}:0; fi"
  run_local_or_remote "$remote_cmd"
done
