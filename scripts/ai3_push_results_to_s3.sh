#!/usr/bin/env bash
set -euo pipefail

# Push selected remote paths from Huanxin ai3 to S3 (training checkpoints,
# logs, outputs).
#
# Usage:
#   scripts/ai3_push_results_to_s3.sh [--dry-run] outputs reports

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/ai3_nm_s3_env.sh"

S3_ROOT="${AI3_NM_S3_ROOT:-${HUANXIN_S3_ROOT:-nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main}}"
REMOTE_ROOT="${AI3_REMOTE_ROOT:-/root/work/quantum-gpt}"

cd "$ROOT_DIR"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

REMOTE_PATHS=("$@")
if [[ ${#REMOTE_PATHS[@]} -eq 0 ]]; then
  REMOTE_PATHS=(outputs)
fi

for remote_path in "${REMOTE_PATHS[@]}"; do
  remote_parent="$(dirname "$remote_path")"
  if [[ "$remote_parent" == "." ]]; then
    remote_file_dest="$S3_ROOT"
  else
    remote_file_dest="$S3_ROOT/$remote_parent"
  fi
  REMOTE_CONFIG="/tmp/nm-aihuanxin-rclone.conf"
  REMOTE_SETUP="$(ai3_remote_nm_rclone_setup_script "$REMOTE_CONFIG")"
  REMOTE_CMD="$REMOTE_SETUP cd '$REMOTE_ROOT' && if [[ -d '$remote_path' ]]; then rclone copy '$remote_path' '$S3_ROOT/$remote_path' --config '$REMOTE_CONFIG' --s3-no-check-bucket --fast-list --progress"
  if [[ $DRY_RUN -eq 1 ]]; then
    REMOTE_CMD+=" --dry-run"
  fi
  REMOTE_CMD+="; elif [[ -f '$remote_path' ]]; then rclone copy '$remote_path' '$remote_file_dest' --config '$REMOTE_CONFIG' --s3-no-check-bucket --fast-list --progress"
  if [[ $DRY_RUN -eq 1 ]]; then
    REMOTE_CMD+=" --dry-run"
  fi
  REMOTE_CMD+="; else echo 'skip missing: $remote_path'; fi"
  JSON_OUT="$(bash scripts/huanxin_shell.sh ai3 "$REMOTE_CMD")"
  python3 - <<'PY' "$JSON_OUT"
import json
import sys

payload = json.loads(sys.argv[1])
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
bad_markers = ("ERROR :", "NOTICE: Failed", "AccessDenied", "Failed to")
if any(marker in text for marker in bad_markers):
    raise SystemExit(text)
print(text)
PY
done
