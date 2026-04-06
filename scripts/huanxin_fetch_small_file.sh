#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_fetch_small_file.sh <ai1|ai2> <remote-path> <local-path> [max-bytes]

Fetch a small remote file through the Huanxin shell and write it locally.
Intended for metrics, configs, logs, and small JSON reports when remote -> S3 is failing.
EOF
  exit 1
}

if [[ $# -lt 3 || $# -gt 4 ]]; then
  usage
fi

ENV_NAME="$1"
REMOTE_PATH="$2"
LOCAL_PATH="$3"
MAX_BYTES="${4:-524288}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"

case "$ENV_NAME" in
  ai1|ai2) ;;
  *)
    echo "Unsupported env: $ENV_NAME" >&2
    exit 1
    ;;
esac

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REMOTE_CMD="$(python3 - <<'PY' "$REMOTE_PATH" "$MAX_BYTES"
import shlex
import sys

remote_path = sys.argv[1]
max_bytes = sys.argv[2]
code = """
import base64
import hashlib
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
limit = int(sys.argv[2])
if not path.exists():
    print("__HX_FETCH_MISSING__")
    raise SystemExit(0)

data = path.read_bytes()
print(f"__HX_FETCH_SIZE__ {len(data)}")
print(f"__HX_FETCH_SHA256__ {hashlib.sha256(data).hexdigest()}")
if len(data) > limit:
    print("__HX_FETCH_TOO_LARGE__")
    raise SystemExit(0)

print("__HX_FETCH_BEGIN__")
print(base64.b64encode(data).decode("ascii"))
print("__HX_FETCH_END__")
"""
print(
    "python3 -c "
    + shlex.quote(code)
    + " "
    + shlex.quote(remote_path)
    + " "
    + shlex.quote(max_bytes)
)
PY
)"

JSON_OUT="$(
  HUANXIN_USE_DAEMON=1 HUANXIN_WAIT_MS="$WAIT_MS" \
    "$ROOT_DIR/scripts/huanxin_shell.sh" "$ENV_NAME" "$REMOTE_CMD"
)"

python3 - <<'PY' "$JSON_OUT" "$ENV_NAME" "$REMOTE_PATH" "$LOCAL_PATH" "$MAX_BYTES"
import base64
import hashlib
import json
import re
import sys
from pathlib import Path

payload = json.loads(sys.argv[1])
env_name = sys.argv[2]
remote_path = sys.argv[3]
local_path = Path(sys.argv[4])
max_bytes = int(sys.argv[5])

if not payload.get("ok"):
    raise SystemExit(f"Huanxin shell command failed: {payload}")

combined = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
if "__HX_FETCH_MISSING__" in combined:
    raise SystemExit(f"Remote file does not exist on {env_name}: {remote_path}")
if "__HX_FETCH_TOO_LARGE__" in combined:
    size_match = re.search(r"__HX_FETCH_SIZE__ (\d+)", combined)
    size_text = size_match.group(1) if size_match else "unknown"
    raise SystemExit(
        f"Remote file exceeds limit on {env_name}: {remote_path} (size={size_text}, max_bytes={max_bytes})"
    )

size_match = re.search(r"__HX_FETCH_SIZE__ (\d+)", combined)
sha_match = re.search(r"__HX_FETCH_SHA256__ ([0-9a-f]{64})", combined)
blob_match = re.search(r"__HX_FETCH_BEGIN__\n(.*?)\n__HX_FETCH_END__", combined, re.S)
if size_match is None or sha_match is None or blob_match is None:
    raise SystemExit(f"Did not observe complete fetch markers for {remote_path} on {env_name}")

data = base64.b64decode(blob_match.group(1).strip())
size = int(size_match.group(1))
sha256 = sha_match.group(1)
if len(data) != size:
    raise SystemExit(
        f"Decoded byte count mismatch for {remote_path} on {env_name}: decoded={len(data)} expected={size}"
    )
if hashlib.sha256(data).hexdigest() != sha256:
    raise SystemExit(f"SHA256 mismatch for {remote_path} on {env_name}")

local_path.parent.mkdir(parents=True, exist_ok=True)
local_path.write_bytes(data)
print(
    json.dumps(
        {
            "env": env_name,
            "remote_path": remote_path,
            "local_path": str(local_path),
            "bytes": size,
            "sha256": sha256,
            "transport": payload.get("transport"),
            "duration_ms": payload.get("durationMs"),
        },
        indent=2,
    )
)
PY
