#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="ASI1"
REMOTE_ROOT="${ASI1_REMOTE_ROOT:-/workspace/quantum-gpt}"
OUTPUT_DIR="${ASI1_AGENTIC_OUTPUT_DIR:-}"
LOG_PATH="${ASI1_AGENTIC_LOG_PATH:-}"
TAIL_LINES="${ASI1_AGENTIC_STATUS_TAIL_LINES:-80}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  scripts/asi1_agentic_grpo_quick_status.sh --output-dir <remote-output-dir> [--log-path <remote-log>] [options]
  scripts/asi1_agentic_grpo_quick_status.sh --log-path <remote-log> [options]

Read-only ASI1 helper for summarizing an agentic GRPO run directory and/or log.

Options:
  --output-dir <path>    Remote agentic GRPO output directory, absolute or relative to /workspace/quantum-gpt.
  --log-path <path>      Remote log path to tail, absolute or relative to /workspace/quantum-gpt.
  --remote-root <path>   Remote repo root. Default: /workspace/quantum-gpt.
  --tail-lines <n>       Number of log lines to print. Default: 80.
  --dry-run              Print the wrapper commands without contacting ASI1.
EOF
}

json_payload() {
  python3 - <<'PY' "$ENV_NAME" "$REMOTE_ROOT" "$OUTPUT_DIR" "$LOG_PATH" "$TAIL_LINES" "$ROOT_DIR"
import json
import shlex
import sys

env_name, remote_root, output_dir, log_path, tail_lines, root_dir = sys.argv[1:7]
commands = []
if output_dir:
    commands.append(
        [
            "bash",
            f"{root_dir}/scripts/show_huanxin_agentic_grpo_status.sh",
            "--env",
            env_name,
            "--remote-root",
            remote_root,
            output_dir,
        ]
    )
if log_path:
    if log_path.startswith("/"):
        remote_log = log_path
    else:
        remote_log = f"{remote_root.rstrip('/')}/{log_path}"
    remote_command = " && ".join(
        [
            f"cd {shlex.quote(remote_root)}",
            f"printf '\\n== log tail: {remote_log} ==\\n'",
            f"test -f {shlex.quote(remote_log)}",
            f"tail -n {shlex.quote(tail_lines)} -- {shlex.quote(remote_log)}",
        ]
    )
    commands.append(
        [
            "bash",
            f"{root_dir}/scripts/huanxin_env_shell.sh",
            "--env",
            env_name,
            remote_command,
        ]
    )
print(
    json.dumps(
        {
            "environment": env_name,
            "remote_root": remote_root,
            "output_dir": output_dir,
            "log_path": log_path,
            "tail_lines": int(tail_lines),
            "commands": commands,
        },
        indent=2,
    )
)
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --log-path)
      LOG_PATH="${2:-}"
      shift 2
      ;;
    --remote-root)
      REMOTE_ROOT="${2:-}"
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
      if [[ -z "$OUTPUT_DIR" ]]; then
        OUTPUT_DIR="$1"
        shift
      else
        echo "Unknown arg: $1" >&2
        usage >&2
        exit 2
      fi
      ;;
  esac
done

if [[ -z "$OUTPUT_DIR" && -z "$LOG_PATH" ]]; then
  echo "Missing --output-dir or --log-path." >&2
  usage >&2
  exit 2
fi

if ! [[ "$TAIL_LINES" =~ ^[1-9][0-9]*$ ]]; then
  echo "--tail-lines must be a positive integer." >&2
  exit 2
fi

if (( TAIL_LINES > 500 )); then
  echo "--tail-lines must be <= 500 for bounded status output." >&2
  exit 2
fi

cd "$ROOT_DIR"

if [[ "$DRY_RUN" == "1" ]]; then
  json_payload
  exit 0
fi

if [[ -n "$OUTPUT_DIR" ]]; then
  bash "$ROOT_DIR/scripts/show_huanxin_agentic_grpo_status.sh" \
    --env "$ENV_NAME" \
    --remote-root "$REMOTE_ROOT" \
    "$OUTPUT_DIR"
fi

if [[ -n "$LOG_PATH" ]]; then
  if [[ -n "$OUTPUT_DIR" ]]; then
    printf '\n'
  fi

  REMOTE_CMD="$(python3 - <<'PY' "$REMOTE_ROOT" "$LOG_PATH" "$TAIL_LINES"
import shlex
import sys

remote_root, log_path, tail_lines = sys.argv[1:4]
if log_path.startswith("/"):
    remote_log = log_path
else:
    remote_log = f"{remote_root.rstrip('/')}/{log_path}"
parts = [
    f"cd {shlex.quote(remote_root)}",
    f"printf '\\n== log tail: {remote_log} ==\\n'",
    f"test -f {shlex.quote(remote_log)}",
    f"tail -n {shlex.quote(tail_lines)} -- {shlex.quote(remote_log)}",
]
print(" && ".join(parts))
PY
)"
  bash "$ROOT_DIR/scripts/huanxin_env_shell.sh" --env "$ENV_NAME" "$REMOTE_CMD"
fi
