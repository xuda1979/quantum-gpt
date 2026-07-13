#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_upload_small_file.sh --env <env-name> --source <local-path> --remote-path <remote-path> [--max-bytes N] [--chunk-bytes N] [--dry-run]

Upload one small local file through the Huanxin shell/control plane and verify
the remote SHA256. This is intended for tiny probes, configs, and emergency
bootstrap snippets when S3 ingress from the target environment is unavailable.
It is not a replacement for S3 or a bulk archive transfer.
EOF
  exit 1
}

ENV_NAME=""
SOURCE_PATH=""
REMOTE_PATH=""
MAX_BYTES=131072
CHUNK_BYTES=49152
CHUNKS_PER_COMMAND=8
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --source)
      SOURCE_PATH="${2:-}"
      shift 2
      ;;
    --remote-path)
      REMOTE_PATH="${2:-}"
      shift 2
      ;;
    --max-bytes)
      MAX_BYTES="${2:-}"
      shift 2
      ;;
    --chunk-bytes)
      CHUNK_BYTES="${2:-}"
      shift 2
      ;;
    --chunks-per-command)
      CHUNKS_PER_COMMAND="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help|-h)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

if [[ -z "$ENV_NAME" || -z "$SOURCE_PATH" || -z "$REMOTE_PATH" ]]; then
  usage
fi

if ! [[ "$MAX_BYTES" =~ ^[0-9]+$ ]] || [[ "$MAX_BYTES" -le 0 ]]; then
  echo "Invalid --max-bytes: $MAX_BYTES" >&2
  exit 2
fi
if ! [[ "$CHUNK_BYTES" =~ ^[0-9]+$ ]] || [[ "$CHUNK_BYTES" -le 0 ]]; then
  echo "Invalid --chunk-bytes: $CHUNK_BYTES" >&2
  exit 2
fi
if ! [[ "$CHUNKS_PER_COMMAND" =~ ^[0-9]+$ ]] || [[ "$CHUNKS_PER_COMMAND" -le 0 ]]; then
  echo "Invalid --chunks-per-command: $CHUNKS_PER_COMMAND" >&2
  exit 2
fi

if [[ ! -f "$SOURCE_PATH" ]]; then
  echo "Source file does not exist: $SOURCE_PATH" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

FILE_BYTES="$(wc -c < "$SOURCE_PATH" | tr -d '[:space:]')"
if [[ "$FILE_BYTES" -gt "$MAX_BYTES" ]]; then
  echo "Refusing upload: $SOURCE_PATH is ${FILE_BYTES} bytes, max is ${MAX_BYTES}" >&2
  exit 1
fi

LOCAL_SHA="$(shasum -a 256 "$SOURCE_PATH" | awk '{print $1}')"
REMOTE_CMDS_JSON_FILE="$(mktemp -t huanxin-upload-cmds.XXXXXX)"
trap 'rm -f "$REMOTE_CMDS_JSON_FILE"' EXIT
python3 - <<'PY' "$REMOTE_PATH" "$SOURCE_PATH" "$LOCAL_SHA" "$FILE_BYTES" "$CHUNK_BYTES" "$CHUNKS_PER_COMMAND" "$REMOTE_CMDS_JSON_FILE"
import base64
import json
import shlex
import sys
from pathlib import PurePosixPath

remote_path = sys.argv[1]
source_path = sys.argv[2]
local_sha = sys.argv[3]
file_bytes = sys.argv[4]
chunk_bytes = int(sys.argv[5])
chunks_per_command = int(sys.argv[6])
output_path = sys.argv[7]
parent = str(PurePosixPath(remote_path).parent)
b64_path = remote_path + ".b64tmp"
encoded = base64.b64encode(open(source_path, "rb").read()).decode("ascii")

setup = []
if parent and parent != ".":
    setup.append("mkdir -p " + shlex.quote(parent))
setup.append("rm -f " + shlex.quote(b64_path) + " " + shlex.quote(remote_path))

commands = [" && ".join(setup)]
chunk_parts = []
for index in range(0, len(encoded), chunk_bytes):
    chunk = encoded[index : index + chunk_bytes]
    chunk_parts.append("printf '%s' " + shlex.quote(chunk) + " >> " + shlex.quote(b64_path))
for index in range(0, len(chunk_parts), chunks_per_command):
    commands.append(" && ".join(chunk_parts[index : index + chunks_per_command]))

verify_parts = [
    "base64 -d " + shlex.quote(b64_path) + " > " + shlex.quote(remote_path),
    "rm -f " + shlex.quote(b64_path),
    "printf '__HX_UPLOAD_LOCAL_SHA__ " + local_sha + "\\n__HX_UPLOAD_REMOTE_SHA__ '",
    "sha256sum " + shlex.quote(remote_path) + " | awk '{print $1}'",
    "printf '__HX_UPLOAD_BYTES__ " + file_bytes + "\\n'",
    "wc -c " + shlex.quote(remote_path),
]
commands.append(" && ".join(verify_parts))
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(commands, handle)
PY

if [[ "$DRY_RUN" -eq 1 ]]; then
  python3 - <<'PY' "$ENV_NAME" "$SOURCE_PATH" "$REMOTE_PATH" "$FILE_BYTES" "$LOCAL_SHA" "$REMOTE_CMDS_JSON_FILE"
import json
import sys

commands = json.load(open(sys.argv[6], encoding="utf-8"))
print(
    json.dumps(
        {
            "env": sys.argv[1],
            "source": sys.argv[2],
            "remote_path": sys.argv[3],
            "bytes": int(sys.argv[4]),
            "sha256": sys.argv[5],
            "chunk_commands": len(commands),
            "remote_command": commands[0] if commands else "",
            "remote_commands": commands,
        },
        indent=2,
    )
)
PY
  exit 0
fi

JSON_LINES="$(
  python3 - <<'PY' "$REMOTE_CMDS_JSON_FILE"
import json
import sys
for command in json.load(open(sys.argv[1], encoding="utf-8")):
    print(json.dumps(command))
PY
)"
JSON_OUT=""
while IFS= read -r command_json; do
  [[ -z "$command_json" ]] && continue
  REMOTE_CMD="$(python3 - <<'PY' "$command_json"
import json
import sys
print(json.loads(sys.argv[1]))
PY
)"
  JSON_OUT="$(
    HUANXIN_WAIT_MS="${HUANXIN_WAIT_MS:-180000}" \
      bash "$ROOT_DIR/scripts/huanxin_env_shell.sh" --env "$ENV_NAME" "$REMOTE_CMD"
  )"
done <<< "$JSON_LINES"

python3 - <<'PY' "$JSON_OUT" "$ENV_NAME" "$REMOTE_PATH" "$FILE_BYTES" "$LOCAL_SHA"
import json
import re
import sys

payload = json.loads(sys.argv[1])
env_name = sys.argv[2]
remote_path = sys.argv[3]
expected_bytes = int(sys.argv[4])
expected_sha = sys.argv[5]

if not payload.get("ok") or not payload.get("commandOk"):
    raise SystemExit(f"Huanxin upload command failed: {payload}")

combined = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
local_match = re.search(r"__HX_UPLOAD_LOCAL_SHA__ ([0-9a-f]{64})", combined)
remote_match = re.search(r"__HX_UPLOAD_REMOTE_SHA__ ([0-9a-f]{64})", combined)
bytes_match = re.search(r"__HX_UPLOAD_BYTES__ (\d+)", combined)
wc_match = re.search(r"^\s*(\d+)\s+" + re.escape(remote_path) + r"\s*$", combined, re.M)

if not local_match or not remote_match or not bytes_match or not wc_match:
    raise SystemExit(f"Did not observe complete upload markers for {remote_path} on {env_name}")

remote_sha = remote_match.group(1)
remote_bytes = int(wc_match.group(1))
if local_match.group(1) != expected_sha or remote_sha != expected_sha:
    raise SystemExit(f"SHA256 mismatch for {remote_path} on {env_name}: remote={remote_sha} expected={expected_sha}")
if int(bytes_match.group(1)) != expected_bytes or remote_bytes != expected_bytes:
    raise SystemExit(
        f"Byte count mismatch for {remote_path} on {env_name}: remote={remote_bytes} expected={expected_bytes}"
    )

print(
    json.dumps(
        {
            "ok": True,
            "env": env_name,
            "remote_path": remote_path,
            "bytes": expected_bytes,
            "sha256": expected_sha,
            "transport": payload.get("transport"),
        },
        indent=2,
    )
)
PY
