#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_S3_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main"
AI3_NM_S3_ROOT="${AI3_NM_S3_ROOT:-${HUANXIN_S3_ROOT:-$DEFAULT_S3_ROOT}}"
AI3_PRESEEDED_RCLONE_S3_PATH="${AI3_PRESEEDED_RCLONE_S3_PATH:-${AI3_NM_S3_ROOT}/tools/preseed/rclone-linux-arm64}"

choose_rclone_bin() {
  local candidate="${RCLONE_BIN:-$(command -v rclone || true)}"
  if [[ -z "$candidate" && -x /Users/daxu/homebrew/bin/rclone ]]; then
    candidate=/Users/daxu/homebrew/bin/rclone
  fi
  if [[ -z "$candidate" || ! -x "$candidate" ]]; then
    echo "rclone not found locally. Set RCLONE_BIN or install rclone." >&2
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
    if ":" in ip or ip in seen:
        continue
    print(ip)
    raise SystemExit(0)
raise SystemExit(1)
PY
}

load_ai3_nm_s3_env() {
  local rclone_bin remote_name remote_config provider endpoint
  rclone_bin="$(choose_rclone_bin)"
  remote_name="${AI3_NM_S3_ROOT%%:*}"
  remote_config="$("$rclone_bin" config show "$remote_name")"
  if [[ -z "$remote_config" ]]; then
    echo "could not read local rclone config for remote '$remote_name'" >&2
    exit 1
  fi

  read_remote_field() {
    python3 - <<'PY' "$remote_config" "$1" "$2"
import configparser
import io
import sys

config = configparser.ConfigParser()
config.read_file(io.StringIO(sys.argv[1]))
print(config.get(sys.argv[2], sys.argv[3], fallback=""))
PY
  }

  provider="$(read_remote_field "$remote_name" provider)"
  endpoint="$(read_remote_field "$remote_name" endpoint)"

  export AI3_LOCAL_RCLONE_BIN="$rclone_bin"
  export AI3_NM_REMOTE_NAME="$remote_name"
  export AI3_NM_S3_PROVIDER="${provider:-Minio}"
  export AI3_NM_S3_ACCESS_KEY_ID="$(read_remote_field "$remote_name" access_key_id)"
  export AI3_NM_S3_SECRET_ACCESS_KEY="$(read_remote_field "$remote_name" secret_access_key)"
  export AI3_NM_S3_ENDPOINT="$endpoint"
  export AI3_NM_S3_ENDPOINT_HOST="$(extract_url_host "$endpoint")"
  export AI3_NM_S3_ENDPOINT_IP="$(resolve_ipv4 "$AI3_NM_S3_ENDPOINT_HOST" || true)"
  export AI3_PRESEEDED_RCLONE_URL="${AI3_PRESEEDED_RCLONE_URL:-$("$rclone_bin" link "$AI3_PRESEEDED_RCLONE_S3_PATH" --expire 24h 2>/dev/null)}"
  export AI3_PRESEEDED_RCLONE_HOST="$(extract_url_host "$AI3_PRESEEDED_RCLONE_URL")"
  export AI3_PRESEEDED_RCLONE_IP="$(resolve_ipv4 "$AI3_PRESEEDED_RCLONE_HOST" || true)"

  if [[ -z "$AI3_NM_S3_ACCESS_KEY_ID" || -z "$AI3_NM_S3_SECRET_ACCESS_KEY" || -z "$AI3_NM_S3_ENDPOINT" ]]; then
    echo "could not parse S3 credentials for remote '$remote_name'" >&2
    exit 1
  fi
  if [[ -z "$AI3_PRESEEDED_RCLONE_URL" ]]; then
    echo "could not create a signed URL for $AI3_PRESEEDED_RCLONE_S3_PATH" >&2
    exit 1
  fi
}

ai3_remote_nm_rclone_setup_script() {
  local config_path="${1:-/tmp/nm-aihuanxin-rclone.conf}"
  load_ai3_nm_s3_env
  python3 - <<'PY' \
    "$config_path" \
    "$AI3_NM_REMOTE_NAME" \
    "$AI3_NM_S3_PROVIDER" \
    "$AI3_NM_S3_ACCESS_KEY_ID" \
    "$AI3_NM_S3_SECRET_ACCESS_KEY" \
    "$AI3_NM_S3_ENDPOINT" \
    "$AI3_NM_S3_ENDPOINT_HOST" \
    "$AI3_NM_S3_ENDPOINT_IP" \
    "$AI3_PRESEEDED_RCLONE_URL" \
    "$AI3_PRESEEDED_RCLONE_HOST" \
    "$AI3_PRESEEDED_RCLONE_IP"
import shlex
import sys

(
    config_path,
    remote_name,
    provider,
    access_key_id,
    secret_access_key,
    endpoint,
    endpoint_host,
    endpoint_ip,
    preseeded_rclone_url,
    preseeded_rclone_host,
    preseeded_rclone_ip,
) = sys.argv[1:]


def q(value: str) -> str:
    return shlex.quote(value)


config_text = (
    f"[{remote_name}]\n"
    "type = s3\n"
    f"provider = {provider}\n"
    f"access_key_id = {access_key_id}\n"
    f"secret_access_key = {secret_access_key}\n"
    f"endpoint = {endpoint}\n"
)

curl_parts = ["curl", "-fsSL"]
if preseeded_rclone_host and preseeded_rclone_ip:
    curl_parts.extend(["--resolve", f"{preseeded_rclone_host}:443:{preseeded_rclone_ip}"])
curl_parts.extend([preseeded_rclone_url, "-o", "$tmp_dir/rclone"])

lines = [
    "export PATH=/root/.local/bin:/usr/local/bin:$PATH",
]
if endpoint_host and endpoint_ip:
    lines.append(
        f"if ! grep -Eq '(^|[[:space:]]){endpoint_host}([[:space:]]|$)' /etc/hosts; "
        f"then printf '%s %s\\n' {q(endpoint_ip)} {q(endpoint_host)} >> /etc/hosts; fi"
    )
lines.extend(
    [
        "if ! command -v rclone >/dev/null 2>&1; then",
        "  tmp_dir=$(mktemp -d)",
        "  trap 'rm -rf \"$tmp_dir\"' EXIT",
        "  " + " ".join(q(part) if part != "$tmp_dir/rclone" else part for part in curl_parts),
        "  install -m 0755 \"$tmp_dir/rclone\" /usr/local/bin/rclone",
        "  rm -rf \"$tmp_dir\"",
        "  trap - EXIT",
        "fi",
        "umask 077",
        f"cat > {q(config_path)} <<'__AI3_NM_RCLONE_CONF__'\n{config_text}__AI3_NM_RCLONE_CONF__",
    ]
)
print("\n".join(lines) + "\n")
PY
}
