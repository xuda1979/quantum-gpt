#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_ROOT="${HUANXIN_S3_ROOT:-nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main}"
REMOTE_ROOT="${AI_REMOTE_ROOT:-/root/software/quantum-gpt}"
REMOTE_CODEX_BIN="${REMOTE_CODEX_BIN:-/root/.local/bin/codex}"
MODEL_ALIAS="${MODEL_ALIAS:-local_finetuned_model}"
BASE_MODEL_PATH="${BASE_MODEL_PATH:-models/Qwen2.5-1.5B-Instruct}"
ADAPTER_PATH="${ADAPTER_PATH:-outputs/qwen25-quantum-generalization-holdout-ai1-8npu-true20-e2-20260412T1617CST/adapter}"
PROMPT="${PROMPT:-Reply with exactly OK and nothing else.}"
WAIT_MS="${HUANXIN_WAIT_MS:-900000}"
ALLOW_STANDALONE_FALLBACK="${HUANXIN_ALLOW_STANDALONE_FALLBACK:-1}"
RCLONE_BOOTSTRAP_URL="${RCLONE_BOOTSTRAP_URL:-}"
PRESEEDED_RCLONE_URL="${PRESEEDED_RCLONE_URL:-}"
SERVER_DEVICE="${SERVER_DEVICE:-npu}"
SERVER_MAX_NEW_TOKENS="${SERVER_MAX_NEW_TOKENS:-256}"
SERVER_LOG_PATH="${SERVER_LOG_PATH:-/tmp/quantum_codex_server.log}"
SETUP_LOG_PATH="${SETUP_LOG_PATH:-/tmp/ai_codex_local_exec.log}"
JOB_NAME="${JOB_NAME:-ai-codex-local-finetuned}"
POLL_SECONDS="${POLL_SECONDS:-20}"
PRINT_ONLY=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai_codex_local_exec.sh [options]

Options:
  --model-alias <name>       Codex model alias to expose. Default: local_finetuned_model
  --base-model <path>        Remote relative base-model path under the repo root.
  --adapter <path>           Remote relative adapter path under the repo root.
  --prompt <text>            Smoke-test prompt for `codex exec`.
  --wait-ms <ms>             Huanxin shell wait budget. Default: 900000
  --server-device <device>   Provider device. Default: npu
  --max-new-tokens <n>       Provider max_new_tokens. Default: 256
  --print-only               Print the generated remote command and exit.
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model-alias)
      MODEL_ALIAS="${2:-}"
      shift 2
      ;;
    --base-model)
      BASE_MODEL_PATH="${2:-}"
      shift 2
      ;;
    --adapter)
      ADAPTER_PATH="${2:-}"
      shift 2
      ;;
    --prompt)
      PROMPT="${2:-}"
      shift 2
      ;;
    --wait-ms)
      WAIT_MS="${2:-}"
      shift 2
      ;;
    --server-device)
      SERVER_DEVICE="${2:-}"
      shift 2
      ;;
    --max-new-tokens)
      SERVER_MAX_NEW_TOKENS="${2:-}"
      shift 2
      ;;
    --print-only)
      PRINT_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "unknown option: $1" >&2
      usage
      ;;
  esac
done

choose_rclone_bin() {
  local candidate="${RCLONE_BIN:-$(command -v rclone || true)}"
  if [[ -z "$candidate" && -x /Users/daxu/homebrew/bin/rclone ]]; then
    candidate=/Users/daxu/homebrew/bin/rclone
  fi
  if [[ -z "$candidate" || ! -x "$candidate" ]]; then
    echo 'rclone not found locally. Set RCLONE_BIN or install rclone.' >&2
    exit 1
  fi
  printf '%s\n' "$candidate"
}

extract_url_host() {
  python3 - <<'PY' "$1"
import sys
from urllib.parse import urlparse

print(urlparse(sys.argv[1]).hostname or "")
PY
}

resolve_ipv4() {
  python3 - <<'PY' "$1"
import socket
import sys

host = sys.argv[1]
try:
    infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
except OSError:
    raise SystemExit(1)

seen = set()
for info in infos:
    ip = info[4][0]
    if ':' in ip or ip in seen:
        continue
    print(ip)
    raise SystemExit(0)
raise SystemExit(1)
PY
}

RCLONE_BIN="$(choose_rclone_bin)"

NM_REMOTE_CONFIG="$("$RCLONE_BIN" config show nm-aihuanxin)"
if [[ -z "$NM_REMOTE_CONFIG" ]]; then
  echo "could not read local rclone config for remote 'nm-aihuanxin'" >&2
  exit 1
fi

read_nm_remote_field() {
  python3 - <<'PY' "$NM_REMOTE_CONFIG" "$1"
import configparser
import io
import sys

config = configparser.ConfigParser()
config.read_file(io.StringIO(sys.argv[1]))
print(config.get("nm-aihuanxin", sys.argv[2], fallback=""))
PY
}

NM_S3_PROVIDER="$(read_nm_remote_field provider)"
NM_S3_ACCESS_KEY_ID="$(read_nm_remote_field access_key_id)"
NM_S3_SECRET_ACCESS_KEY="$(read_nm_remote_field secret_access_key)"
NM_S3_ENDPOINT="$(read_nm_remote_field endpoint)"
NM_S3_ENDPOINT_HOST="$(extract_url_host "$NM_S3_ENDPOINT")"
NM_S3_ENDPOINT_IP="$(resolve_ipv4 "$NM_S3_ENDPOINT_HOST" || true)"
RCLONE_BOOTSTRAP_HOST=""
RCLONE_BOOTSTRAP_IP=""
if [[ -z "$RCLONE_BOOTSTRAP_URL" ]]; then
  RCLONE_BOOTSTRAP_HOST="downloads.rclone.org"
  RCLONE_BOOTSTRAP_IP="$(resolve_ipv4 "$RCLONE_BOOTSTRAP_HOST" || true)"
fi

if [[ -z "$NM_S3_PROVIDER" ]]; then
  NM_S3_PROVIDER="Minio"
fi

if [[ -z "$NM_S3_ACCESS_KEY_ID" || -z "$NM_S3_SECRET_ACCESS_KEY" || -z "$NM_S3_ENDPOINT" ]]; then
  echo "could not parse nm-aihuanxin credentials from local rclone config" >&2
  exit 1
fi

stage_paths=(
  scripts/ai_codex_local_bootstrap_remote.sh
  scripts/install_codex_standalone.sh
  scripts/render_codex_local_config.py
  scripts/serve_openai_chat_adapter.py
  training/model_backend.py
  training/model_family_preflight.py
  training/qwen_sft_peft.py
  training/runtime_overlay.py
  training/text_preprocessor_backend.py
  evals/runner/candidate_sanitize.py
)

cd "$ROOT_DIR"

if [[ "$PRINT_ONLY" != "1" ]]; then
  bash "$ROOT_DIR/scripts/push_to_s3.sh" "${stage_paths[@]}"
fi

BOOTSTRAP_SCRIPT_S3_PATH="${S3_ROOT}/scripts/ai_codex_local_bootstrap_remote.sh"
BOOTSTRAP_SCRIPT_URL="$("$RCLONE_BIN" link "$BOOTSTRAP_SCRIPT_S3_PATH" --expire 24h)"

REMOTE_CMD="$(
  python3 - <<'PY' \
    "$BOOTSTRAP_SCRIPT_URL" \
    "$NM_S3_PROVIDER" \
    "$NM_S3_ACCESS_KEY_ID" \
    "$NM_S3_SECRET_ACCESS_KEY" \
    "$NM_S3_ENDPOINT" \
    "$NM_S3_ENDPOINT_HOST" \
    "$NM_S3_ENDPOINT_IP" \
    "$RCLONE_BOOTSTRAP_URL" \
    "$RCLONE_BOOTSTRAP_HOST" \
    "$RCLONE_BOOTSTRAP_IP" \
    "$PRESEEDED_RCLONE_URL"
import shlex
import sys

(
    bootstrap_script_url,
    nm_s3_provider,
    nm_s3_access_key_id,
    nm_s3_secret_access_key,
    nm_s3_endpoint,
    nm_s3_endpoint_host,
    nm_s3_endpoint_ip,
    rclone_bootstrap_url,
    rclone_bootstrap_host,
    rclone_bootstrap_ip,
    preseeded_rclone_url,
) = sys.argv[1:]


def q(value: str) -> str:
    return shlex.quote(value)


remote_root = "/root/software/quantum-gpt"
remote_root_q = q(remote_root)
bootstrap_script = q(remote_root + '/scripts/ai_codex_local_bootstrap_remote.sh')
bootstrap_script_url_q = q(bootstrap_script_url)

curl_parts = ["curl", "-fsSL"]
if nm_s3_endpoint_host and nm_s3_endpoint_ip:
    curl_parts.extend(["--resolve", q(f"{nm_s3_endpoint_host}:443:{nm_s3_endpoint_ip}")])
curl_parts.extend([bootstrap_script_url_q, "-o", bootstrap_script])

env_parts = [
    f"NM_S3_PROVIDER={q(nm_s3_provider)}",
    f"NM_S3_ACCESS_KEY_ID={q(nm_s3_access_key_id)}",
    f"NM_S3_SECRET_ACCESS_KEY={q(nm_s3_secret_access_key)}",
    f"NM_S3_ENDPOINT={q(nm_s3_endpoint)}",
]
if nm_s3_endpoint_host:
    env_parts.append(f"NM_S3_ENDPOINT_HOST={q(nm_s3_endpoint_host)}")
if nm_s3_endpoint_ip:
    env_parts.append(f"NM_S3_ENDPOINT_IP={q(nm_s3_endpoint_ip)}")
if rclone_bootstrap_url:
    env_parts.append(f"RCLONE_BOOTSTRAP_URL={q(rclone_bootstrap_url)}")
if rclone_bootstrap_host:
    env_parts.append(f"RCLONE_BOOTSTRAP_HOST={q(rclone_bootstrap_host)}")
if rclone_bootstrap_ip:
    env_parts.append(f"RCLONE_BOOTSTRAP_IP={q(rclone_bootstrap_ip)}")
if preseeded_rclone_url:
    env_parts.append(f"PRESEEDED_RCLONE_URL={q(preseeded_rclone_url)}")

parts = [
    "set -euo pipefail",
    f"mkdir -p {remote_root_q}/scripts",
    " ".join(curl_parts),
    f"chmod 0755 {bootstrap_script}",
    "env " + " ".join(env_parts) + f" bash {bootstrap_script}",
]

print(" && ".join(parts))
PY
)"

if [[ "$PRINT_ONLY" == "1" ]]; then
  python3 - <<'PY' "$REMOTE_CMD"
import re
import sys

text = sys.argv[1]
text = re.sub(r"^(access_key_id\s*=\s*).*$", r"\1[redacted]", text, flags=re.MULTILINE)
text = re.sub(r"^(secret_access_key\s*=\s*).*$", r"\1[redacted]", text, flags=re.MULTILINE)
text = re.sub(r"(NM_S3_ACCESS_KEY_ID=)(\S+)", r"\1[redacted]", text)
text = re.sub(r"(NM_S3_SECRET_ACCESS_KEY=)(\S+)", r"\1[redacted]", text)
print(text)
PY
  exit 0
fi

JOB_JSON="$(
  AI_JOB_REMOTE_ROOT="$REMOTE_ROOT" \
  AI2_JOB_SHELL_WRAPPER="$ROOT_DIR/scripts/ai_shell.sh" \
  AI2_JOB_META_DIR="$ROOT_DIR/.huanxin_ai_jobs" \
  HUANXIN_WAIT_MS="$WAIT_MS" \
  HUANXIN_ALLOW_STANDALONE_FALLBACK="$ALLOW_STANDALONE_FALLBACK" \
    bash "$ROOT_DIR/scripts/ai_job.sh" start "$JOB_NAME" "$SETUP_LOG_PATH" "$REMOTE_CMD"
)"

JOB_ID="$(
  python3 - <<'PY' "$JOB_JSON"
import json
import sys
print(json.loads(sys.argv[1])["job_id"])
PY
)"

printf '%s\n' "$JOB_JSON"

while true; do
  STATUS_JSON="$(
    AI_JOB_REMOTE_ROOT="$REMOTE_ROOT" \
    AI2_JOB_SHELL_WRAPPER="$ROOT_DIR/scripts/ai_shell.sh" \
    AI2_JOB_META_DIR="$ROOT_DIR/.huanxin_ai_jobs" \
    HUANXIN_WAIT_MS="$WAIT_MS" \
    HUANXIN_ALLOW_STANDALONE_FALLBACK="$ALLOW_STANDALONE_FALLBACK" \
      bash "$ROOT_DIR/scripts/ai_job.sh" status "$JOB_ID" 200
  )"

  STATUS="$(python3 - <<'PY' "$STATUS_JSON"
import json
import sys
print(json.loads(sys.argv[1]).get("status", "unknown"))
PY
)"

  if [[ "$STATUS" == "running" ]]; then
    sleep "$POLL_SECONDS"
    continue
  fi

  python3 - <<'PY' "$STATUS_JSON"
import json
import sys

payload = json.loads(sys.argv[1])
log_tail = str(payload.get("log_tail") or "")

if payload.get("status") != "exited":
    raise SystemExit(json.dumps(payload, indent=2))

required_markers = ("__AI_CODEX_READY__", "__AI_CODEX_RESULT__")
missing = [marker for marker in required_markers if marker not in log_tail]
if missing:
    raise SystemExit(json.dumps(payload, indent=2))

if "\nOK\n" not in "\n" + log_tail + "\n":
    raise SystemExit(json.dumps(payload, indent=2))

print(json.dumps(payload, indent=2))
PY
  break
done
