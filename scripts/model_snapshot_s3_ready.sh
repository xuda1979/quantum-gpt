#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
RCLONE_BIN="${RCLONE_BIN:-$(command -v rclone || true)}"
if [[ -z "$RCLONE_BIN" && -x /Users/daxu/homebrew/bin/rclone ]]; then
  RCLONE_BIN=/Users/daxu/homebrew/bin/rclone
fi

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/model_snapshot_s3_ready.sh <model-subdir>
EOF
  exit 1
}

if [[ $# -ne 1 ]]; then
  usage
fi

MODEL_SUBDIR="$1"
if [[ "$MODEL_SUBDIR" == /* ]]; then
  echo "model-subdir must be relative, for example: gemma-4-31B-it" >&2
  exit 1
fi

if [[ -z "$RCLONE_BIN" || ! -x "$RCLONE_BIN" ]]; then
  echo 'rclone not found. Set RCLONE_BIN or install rclone.' >&2
  exit 1
fi

cd "$ROOT_DIR"
S3_MODEL_DIR="$S3_ROOT/models/$MODEL_SUBDIR"
LISTING="$("$RCLONE_BIN" lsf "$S3_MODEL_DIR" 2>/dev/null || true)"

if [[ -z "$LISTING" ]]; then
  echo "model dir not present in S3: $S3_MODEL_DIR" >&2
  exit 1
fi

if printf '%s\n' "$LISTING" | rg -qx 'model.safetensors|pytorch_model.bin'; then
  exit 0
fi

INDEX_NAME=""
if printf '%s\n' "$LISTING" | rg -qx 'model.safetensors.index.json'; then
  INDEX_NAME="model.safetensors.index.json"
elif printf '%s\n' "$LISTING" | rg -qx 'pytorch_model.bin.index.json'; then
  INDEX_NAME="pytorch_model.bin.index.json"
else
  echo "no model weight file or index found in S3: $S3_MODEL_DIR" >&2
  exit 1
fi

INDEX_JSON="$("$RCLONE_BIN" cat "$S3_MODEL_DIR/$INDEX_NAME")"

python3 - <<'PY' "$LISTING" "$INDEX_JSON" "$S3_MODEL_DIR/$INDEX_NAME"
import json
import sys

listing = {line.strip() for line in sys.argv[1].splitlines() if line.strip()}
index_payload = json.loads(sys.argv[2])
index_path = sys.argv[3]
weight_map = index_payload.get("weight_map")
if not isinstance(weight_map, dict):
    raise SystemExit(f"weight index missing weight_map: {index_path}")
missing = [name for name in sorted({str(value) for value in weight_map.values()}) if name not in listing]
if missing:
    raise SystemExit("missing indexed shards: " + ", ".join(missing))
PY
