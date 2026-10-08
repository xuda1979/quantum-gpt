#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${HUANXIN_TRAINING_ENV:-ASI1}"
REMOTE_ROOT="${ASI1_REMOTE_ROOT:-/workspace/quantum-gpt}"
REMOTE_OUTPUT_DIR=""
LOCAL_OUTPUT_DIR=""
MAX_BYTES="${FETCH_MAX_BYTES:-1048576}"
LOG_PATH=""
TAIL_LINES="${FETCH_TAIL_LINES:-500}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  scripts/fetch_asi1_agentic_run_artifacts.sh --remote-output-dir <dir> [--local-output-dir <dir>] [--log-path <remote-log>]

Fetch small ASI1 agentic GRPO run artifacts needed by the local dashboard.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote-output-dir)
      REMOTE_OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --local-output-dir)
      LOCAL_OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
      shift 2
      ;;
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --max-bytes)
      MAX_BYTES="${2:-}"
      shift 2
      ;;
    --log-path)
      LOG_PATH="${2:-}"
      shift 2
      ;;
    --tail-lines)
      TAIL_LINES="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
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

if [[ -z "$REMOTE_OUTPUT_DIR" ]]; then
  echo "Missing --remote-output-dir." >&2
  usage >&2
  exit 2
fi

if [[ "$REMOTE_OUTPUT_DIR" = /* ]]; then
  REMOTE_DIR="$REMOTE_OUTPUT_DIR"
  RUN_NAME="$(basename "$REMOTE_OUTPUT_DIR")"
else
  REMOTE_DIR="${REMOTE_ROOT%/}/${REMOTE_OUTPUT_DIR}"
  RUN_NAME="$(basename "$REMOTE_OUTPUT_DIR")"
fi

if [[ -z "$LOCAL_OUTPUT_DIR" ]]; then
  LOCAL_OUTPUT_DIR="$ROOT_DIR/outputs/$RUN_NAME"
fi

mkdir -p "$LOCAL_OUTPUT_DIR"

if ! [[ "$MAX_BYTES" =~ ^[1-9][0-9]*$ ]]; then
  echo "--max-bytes must be a positive integer." >&2
  exit 2
fi

if ! [[ "$TAIL_LINES" =~ ^[1-9][0-9]*$ ]]; then
  echo "--tail-lines must be a positive integer." >&2
  exit 2
fi

if (( TAIL_LINES > 2000 )); then
  echo "--tail-lines must be <= 2000 for bounded dashboard log tails." >&2
  exit 2
fi

REMOTE_CMD="$(python3 - <<'PY' "$REMOTE_DIR" "$LOG_PATH" "$MAX_BYTES" "$TAIL_LINES"
import shlex
import sys
import json

remote_dir, log_path, max_bytes, tail_lines = sys.argv[1:5]
artifact_names = [
    "live_status.json",
    "grpo_step_metrics.jsonl",
    "online_eval_latest.json",
    "online_eval_history.jsonl",
    "grpo_metrics.json",
    "run_config.json",
    "latest_checkpoint.json",
    "checkpoint_history.jsonl",
    "job_health.json",
    "failure_report.json",
    "safety_report.json",
    "agentic_traces.jsonl",
]
code = r'''
import base64
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

remote_dir = pathlib.Path(sys.argv[1])
log_path = sys.argv[2]
max_bytes = int(sys.argv[3])
tail_lines = int(sys.argv[4])
artifact_names = json.loads(sys.argv[5])

payload = {
    "schema_version": 1,
    "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
    "remote_dir": str(remote_dir),
    "log_path": log_path or None,
    "max_bytes": max_bytes,
    "tail_lines": tail_lines,
    "files": {},
}

def add_file_record(name, path):
    record = {"remote_path": str(path), "exists": path.exists()}
    if path.exists():
        data = path.read_bytes()
        record.update(
            {
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "too_large": len(data) > max_bytes,
            }
        )
        if len(data) <= max_bytes:
            record["base64"] = base64.b64encode(data).decode("ascii")
    payload["files"][name] = record
    return record

for name in artifact_names:
    add_file_record(name, remote_dir / name)

latest_record = payload["files"].get("latest_checkpoint.json") or {}
if latest_record.get("base64"):
    try:
        latest_payload = json.loads(base64.b64decode(latest_record["base64"]).decode("utf-8"))
    except Exception as error:
        payload["checkpoint_probe_error"] = str(error)
    else:
        checkpoint_path_raw = str(latest_payload.get("checkpoint_dir") or latest_payload.get("checkpoint_path") or "")
        if checkpoint_path_raw:
            checkpoint_path = pathlib.Path(checkpoint_path_raw)
            if not checkpoint_path.is_absolute():
                checkpoint_path = remote_dir / checkpoint_path
            if checkpoint_path.is_dir():
                for child_name in ["checkpoint_state.json", "runtime_state.pt"]:
                    add_file_record(f"latest_checkpoint/{child_name}", checkpoint_path / child_name)
            else:
                add_file_record("latest_checkpoint_artifact", checkpoint_path)

if log_path:
    path = pathlib.Path(log_path)
    record = {"remote_path": str(path), "exists": path.exists(), "tail_lines": tail_lines}
    if path.exists():
        completed = subprocess.run(
            ["tail", "-n", str(tail_lines), "--", str(path)],
            text=False,
            capture_output=True,
            check=False,
        )
        data = completed.stdout
        record.update(
            {
                "returncode": completed.returncode,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "too_large": len(data) > max_bytes,
            }
        )
        if len(data) <= max_bytes:
            record["base64"] = base64.b64encode(data).decode("ascii")
    payload["files"]["train_log_tail.txt"] = record

print("__HX_ARTIFACT_BUNDLE_BEGIN__")
print(json.dumps(payload, sort_keys=True))
print("__HX_ARTIFACT_BUNDLE_END__")
'''

print(
    "python3 -c "
    + shlex.quote(code)
    + " "
    + shlex.quote(remote_dir)
    + " "
    + shlex.quote(log_path)
    + " "
    + shlex.quote(max_bytes)
    + " "
    + shlex.quote(tail_lines)
    + " "
    + shlex.quote(json.dumps(artifact_names))
)
PY
)"

if [[ "$DRY_RUN" == "1" ]]; then
  python3 - <<'PY' "$ENV_NAME" "$REMOTE_ROOT" "$REMOTE_DIR" "$LOCAL_OUTPUT_DIR" "$LOG_PATH" "$MAX_BYTES" "$TAIL_LINES" "$REMOTE_CMD"
import json
import sys

env_name, remote_root, remote_dir, local_output_dir, log_path, max_bytes, tail_lines, remote_cmd = sys.argv[1:9]
print(
    json.dumps(
        {
            "ok": True,
            "env": env_name,
            "remote_root": remote_root,
            "remote_dir": remote_dir,
            "local_output_dir": local_output_dir,
            "log_path": log_path or None,
            "max_bytes": int(max_bytes),
            "tail_lines": int(tail_lines),
            "shell_command": [
                "bash",
                "scripts/huanxin_env_shell.sh",
                "--env",
                env_name,
                remote_cmd,
            ],
            "remote_command": remote_cmd,
        },
        indent=2,
    )
)
PY
  exit 0
fi

JSON_OUT="$(
  HUANXIN_WAIT_MS="${HUANXIN_WAIT_MS:-180000}" \
    bash "$ROOT_DIR/scripts/huanxin_env_shell.sh" --env "$ENV_NAME" "$REMOTE_CMD"
)"

python3 - <<'PY' "$JSON_OUT" "$LOCAL_OUTPUT_DIR" "$ENV_NAME" "$REMOTE_DIR" "$LOG_PATH"
import base64
import json
import pathlib
import re
import sys

shell_payload = json.loads(sys.argv[1])
local_dir = pathlib.Path(sys.argv[2])
env_name = sys.argv[3]
remote_dir = sys.argv[4]
log_path = sys.argv[5] or None

if not shell_payload.get("ok"):
    raise SystemExit(f"Huanxin shell command failed: {shell_payload}")

combined = "\n".join(str(shell_payload.get(key, "")) for key in ("output", "after", "before"))
match = re.search(r"__HX_ARTIFACT_BUNDLE_BEGIN__\n(.*?)\n__HX_ARTIFACT_BUNDLE_END__", combined, re.S)
if match is None:
    raise SystemExit("Did not observe complete ASI1 artifact bundle markers.")

bundle = json.loads(match.group(1))
local_dir.mkdir(parents=True, exist_ok=True)
manifest = {
    "schema_version": 1,
    "env": env_name,
    "remote_dir": remote_dir,
    "log_path": log_path,
    "transport": shell_payload.get("transport"),
    "duration_ms": shell_payload.get("durationMs"),
    "fetched_at_utc": bundle.get("fetched_at_utc"),
    "max_bytes": bundle.get("max_bytes"),
    "tail_lines": bundle.get("tail_lines"),
    "files": {},
}

for name, record in sorted(dict(bundle.get("files") or {}).items()):
    record = dict(record)
    b64 = record.pop("base64", None)
    local_path = local_dir / name
    if b64 is not None:
        data = base64.b64decode(b64)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
        record["local_path"] = str(local_path)
        record["fetched"] = True
    else:
        record["fetched"] = False
    manifest["files"][name] = record

manifest_path = local_dir / "asi1_fetch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(
    json.dumps(
        {
            "ok": True,
            "local_output_dir": str(local_dir),
            "manifest": str(manifest_path),
            "files": sorted(p.name for p in local_dir.iterdir()),
        },
        indent=2,
    )
)
PY
