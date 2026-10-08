#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT_DIR/scripts/iner_s3_env.sh"

S3_ROOT="${HUANXIN_S3_ROOT:-$INER_S3_ROOT}"
REMOTE_ROOT="${AI_REMOTE_ROOT:-/root/software/quantum-gpt}"

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
  REMOTE_CONFIG="/tmp/iner-rclone.conf"
  REMOTE_SETUP="$(iner_remote_rclone_setup_script "$REMOTE_CONFIG")"
  REMOTE_CMD="$REMOTE_SETUP cd '$REMOTE_ROOT' && if [[ -d '$remote_path' ]]; then rclone copy '$remote_path' '$S3_ROOT/$remote_path' --config '$REMOTE_CONFIG' --s3-no-check-bucket --progress"
  if [[ $DRY_RUN -eq 1 ]]; then
    REMOTE_CMD+=" --dry-run"
  fi
  REMOTE_CMD+="; elif [[ -f '$remote_path' ]]; then rclone copy '$remote_path' '$remote_file_dest' --config '$REMOTE_CONFIG' --s3-no-check-bucket --progress"
  if [[ $DRY_RUN -eq 1 ]]; then
    REMOTE_CMD+=" --dry-run"
  fi
  REMOTE_CMD+="; else echo 'skip missing: $remote_path'; fi"
  JSON_OUT="$(bash scripts/huanxin_shell.sh AI "$REMOTE_CMD")"
  python3 - <<'PY' "$JSON_OUT"
import json
import sys

payload = json.loads(sys.argv[1])
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
bad_markers = ("ERROR :", "NOTICE: Failed", "AccessDenied", "Failed to")
if any(marker in text for marker in bad_markers):
    raise SystemExit(text)
PY
done
