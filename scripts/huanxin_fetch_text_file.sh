#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/huanxin_fetch_text_file.sh <ai1|ai2> <remote-path> <local-path> [chunk-lines]

Fetch a UTF-8 text file from Huanxin by reading it in line chunks and stitching it
back together locally. This is intended for JSON / logs when direct small-file fetch
through base64 markers is unreliable in xterm transcripts.
EOF
  exit 1
}

if [[ $# -lt 3 || $# -gt 4 ]]; then
  usage
fi

ENV_NAME="$1"
REMOTE_PATH="$2"
LOCAL_PATH="$3"
CHUNK_LINES="${4:-60}"
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

LOCAL_TMP="$(mktemp "${TMPDIR:-/tmp}/huanxin-text-fetch.XXXXXX")"
cleanup() {
  rm -f "$LOCAL_TMP"
}
trap cleanup EXIT

json_is_valid() {
  python3 - <<'PY' "$1"
import json
import sys

raw = sys.argv[1]
try:
    json.loads(raw)
except Exception:
    raise SystemExit(1)
raise SystemExit(0)
PY
}

run_shell_json() {
  local remote_cmd="$1"
  local json_out
  json_out="$(
    HUANXIN_USE_DAEMON=1 HUANXIN_WAIT_MS="$WAIT_MS" \
      bash "$ROOT_DIR/scripts/huanxin_shell.sh" "$ENV_NAME" "$remote_cmd"
  )"
  if json_is_valid "$json_out"; then
    printf '%s' "$json_out"
    return 0
  fi
  HUANXIN_USE_DAEMON=0 HUANXIN_WAIT_MS="$WAIT_MS" \
    bash "$ROOT_DIR/scripts/huanxin_shell.sh" "$ENV_NAME" "$remote_cmd"
}

read_meta() {
  local json_out
  json_out="$(run_shell_json "cd /root/work/quantum-gpt && if [ -f \"$REMOTE_PATH\" ]; then echo __HX_TEXT_EXISTS__ && wc -l \"$REMOTE_PATH\"; else echo __HX_TEXT_MISSING__; fi")"

  python3 - <<'PY' "$json_out"
import json
import re
import sys

raw = sys.argv[1].replace("\r", "")
raw = "".join(ch for ch in raw if ch == "\n" or ch == "\t" or ord(ch) >= 32)
payload = json.loads(raw)
combined = "\n".join(str(payload.get(k, "")) for k in ("output", "after", "before"))
lines = [line.strip() for line in combined.splitlines()]
if "__HX_TEXT_MISSING__" in lines:
    raise SystemExit("MISSING")
match = re.search(r"^\s*(\d+)\s+.+$", combined, re.M)
if not match:
    raise SystemExit("NO_WC")
print(match.group(1))
PY
}

LINE_COUNT="$(read_meta)"
if [[ "$LINE_COUNT" == "MISSING" ]]; then
  echo "Remote file does not exist on $ENV_NAME: $REMOTE_PATH" >&2
  exit 1
fi

if ! [[ "$LINE_COUNT" =~ ^[0-9]+$ ]]; then
  echo "Failed to determine remote line count for $REMOTE_PATH on $ENV_NAME: $LINE_COUNT" >&2
  exit 1
fi

if [[ "$LINE_COUNT" -eq 0 ]]; then
  : > "$LOCAL_TMP"
else
  start=1
  while [[ "$start" -le "$LINE_COUNT" ]]; do
    end=$((start + CHUNK_LINES - 1))
    if [[ "$end" -gt "$LINE_COUNT" ]]; then
      end="$LINE_COUNT"
    fi

    marker_begin="__HX_TEXT_BEGIN_${start}_${end}__"
    marker_end="__HX_TEXT_END_${start}_${end}__"

    json_out="$(run_shell_json "cd /root/work/quantum-gpt && echo $marker_begin && sed -n '${start},${end}p' \"$REMOTE_PATH\" && echo $marker_end")"

    python3 - <<'PY' "$json_out" "$marker_begin" "$marker_end" "$LOCAL_TMP"
import json
import sys
from pathlib import Path

raw = sys.argv[1].replace("\r", "")
raw = "".join(ch for ch in raw if ch == "\n" or ch == "\t" or ord(ch) >= 32)
payload = json.loads(raw)
marker_begin = sys.argv[2]
marker_end = sys.argv[3]
out_path = Path(sys.argv[4])

combined = "\n".join(str(payload.get(k, "")) for k in ("output", "after", "before"))
lines = combined.splitlines()
start = None
end = None
for i, line in enumerate(lines):
    if line.strip() == marker_begin:
        start = i + 1
        continue
    if line.strip() == marker_end and start is not None:
        end = i
        break

if start is None or end is None or end < start:
    raise SystemExit(f"Did not observe complete chunk markers: {marker_begin} .. {marker_end}")

chunk = "\n".join(lines[start:end])
with out_path.open("a", encoding="utf-8") as fh:
    fh.write(chunk)
    fh.write("\n")
PY

    start=$((end + 1))
  done
fi

mkdir -p "$(dirname "$LOCAL_PATH")"
mv "$LOCAL_TMP" "$LOCAL_PATH"
trap - EXIT

python3 - <<'PY' "$LOCAL_PATH" "$LINE_COUNT"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
expected_lines = int(sys.argv[2])
text = path.read_text(encoding="utf-8")
json.loads(text)
print(
    json.dumps(
        {
            "local_path": str(path),
            "bytes": len(text.encode("utf-8")),
            "lines_expected": expected_lines,
            "lines_local": len(text.splitlines()),
            "json_valid": True,
        },
        indent=2,
    )
)
PY
