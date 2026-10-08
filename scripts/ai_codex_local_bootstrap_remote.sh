#!/usr/bin/env bash
set -euo pipefail

S3_ROOT="${S3_ROOT:-nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main}"
REMOTE_ROOT="${REMOTE_ROOT:-/root/software/quantum-gpt}"
MODEL_ALIAS="${MODEL_ALIAS:-local_finetuned_model}"
BASE_MODEL_PATH="${BASE_MODEL_PATH:-models/Qwen2.5-1.5B-Instruct}"
ADAPTER_PATH="${ADAPTER_PATH:-outputs/qwen25-quantum-generalization-holdout-ai1-8npu-true20-e2-20260412T1617CST/adapter}"
PROMPT="${PROMPT:-Reply with exactly OK and nothing else.}"
SERVER_DEVICE="${SERVER_DEVICE:-npu}"
SERVER_MAX_NEW_TOKENS="${SERVER_MAX_NEW_TOKENS:-256}"
SERVER_LOG_PATH="${SERVER_LOG_PATH:-/tmp/quantum_codex_server.log}"
PRESEEDED_CODEX_ARCHIVE_S3_PATH="${PRESEEDED_CODEX_ARCHIVE_S3_PATH:-${S3_ROOT}/tools/codex-aarch64-unknown-linux-musl.tar.gz}"

required_vars=(
  NM_S3_ACCESS_KEY_ID
  NM_S3_SECRET_ACCESS_KEY
  NM_S3_ENDPOINT
)

for name in "${required_vars[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "missing required env: $name" >&2
    exit 1
  fi
done

NM_S3_PROVIDER="${NM_S3_PROVIDER:-Minio}"
NM_S3_ENDPOINT_HOST="${NM_S3_ENDPOINT_HOST:-}"
NM_S3_ENDPOINT_IP="${NM_S3_ENDPOINT_IP:-}"
RCLONE_BOOTSTRAP_URL="${RCLONE_BOOTSTRAP_URL:-}"
RCLONE_BOOTSTRAP_HOST="${RCLONE_BOOTSTRAP_HOST:-}"
RCLONE_BOOTSTRAP_IP="${RCLONE_BOOTSTRAP_IP:-}"
PRESEEDED_RCLONE_URL="${PRESEEDED_RCLONE_URL:-}"
CODEX_OUTPUT_PATH="/tmp/codex_local_finetuned_model.txt"
RCLONE_CONFIG_PATH="/tmp/nm-aihuanxin-rclone.conf"
WHEELHOUSE_DIR="/tmp/ai_codex_wheels"

base_model_abs="${REMOTE_ROOT}/${BASE_MODEL_PATH}"
adapter_abs="${REMOTE_ROOT}/${ADAPTER_PATH}"

export PATH="/root/.local/bin:/usr/local/bin:${PATH}"
export LOCAL_CODEX_API_KEY="${LOCAL_CODEX_API_KEY:-dummy}"
export NO_PROXY="${NO_PROXY:+${NO_PROXY},}127.0.0.1,localhost"
export no_proxy="${no_proxy:+${no_proxy},}127.0.0.1,localhost"

if [[ -z "$NM_S3_ENDPOINT_HOST" ]]; then
  NM_S3_ENDPOINT_HOST="$(
    python3 - <<'PY' "$NM_S3_ENDPOINT"
import sys
from urllib.parse import urlparse

print(urlparse(sys.argv[1]).hostname or "")
PY
  )"
fi

if [[ -z "$RCLONE_BOOTSTRAP_HOST" && -n "$RCLONE_BOOTSTRAP_URL" ]]; then
  RCLONE_BOOTSTRAP_HOST="$(
    python3 - <<'PY' "$RCLONE_BOOTSTRAP_URL"
import sys
from urllib.parse import urlparse

print(urlparse(sys.argv[1]).hostname or "")
PY
  )"
fi

ensure_endpoint_host_mapping() {
  if [[ -z "$NM_S3_ENDPOINT_HOST" || -z "$NM_S3_ENDPOINT_IP" ]]; then
    return 0
  fi
  if grep -Eq "(^|[[:space:]])${NM_S3_ENDPOINT_HOST}([[:space:]]|$)" /etc/hosts; then
    return 0
  fi
  printf '%s %s\n' "$NM_S3_ENDPOINT_IP" "$NM_S3_ENDPOINT_HOST" >> /etc/hosts
}

curl_endpoint_args=()
if [[ -n "$NM_S3_ENDPOINT_HOST" && -n "$NM_S3_ENDPOINT_IP" ]]; then
  curl_endpoint_args+=(--resolve "${NM_S3_ENDPOINT_HOST}:443:${NM_S3_ENDPOINT_IP}")
fi

rclone_curl_args=()
if [[ -n "$RCLONE_BOOTSTRAP_HOST" && -n "$RCLONE_BOOTSTRAP_IP" ]]; then
  rclone_curl_args+=(--resolve "${RCLONE_BOOTSTRAP_HOST}:443:${RCLONE_BOOTSTRAP_IP}")
fi

ensure_endpoint_host_mapping

grep -qxF 'export LOCAL_CODEX_API_KEY=dummy' /root/.bashrc || printf '\nexport LOCAL_CODEX_API_KEY=dummy\n' >> /root/.bashrc
grep -qxF 'export PATH=/root/.local/bin:/usr/local/bin:$PATH' /root/.bashrc || printf 'export PATH=/root/.local/bin:/usr/local/bin:$PATH\n' >> /root/.bashrc
if [[ ! -f /root/.bash_profile ]]; then
  printf 'source /root/.bashrc\n' > /root/.bash_profile
elif ! grep -qxF 'source /root/.bashrc' /root/.bash_profile; then
  printf '\nsource /root/.bashrc\n' >> /root/.bash_profile
fi

mkdir -p /root/.local/bin /usr/local/bin /root/.codex
mkdir -p "${REMOTE_ROOT}/scripts" "${REMOTE_ROOT}/training" "${REMOTE_ROOT}/evals/runner"
mkdir -p "${REMOTE_ROOT}/models" "${REMOTE_ROOT}/outputs"

if ! command -v rclone >/dev/null 2>&1; then
  tmp_dir="$(mktemp -d)"
  if [[ -n "$PRESEEDED_RCLONE_URL" ]]; then
    if curl -fsSL "${curl_endpoint_args[@]}" "$PRESEEDED_RCLONE_URL" -o "$tmp_dir/rclone"; then
      install -m 0755 "$tmp_dir/rclone" /usr/local/bin/rclone
    fi
  fi
  if ! command -v rclone >/dev/null 2>&1; then
    bootstrap_url="$RCLONE_BOOTSTRAP_URL"
    if [[ -z "$bootstrap_url" ]]; then
      bootstrap_url='https://downloads.rclone.org/rclone-current-linux-arm64.zip'
    fi
    curl -fsSL "${rclone_curl_args[@]}" "$bootstrap_url" -o "$tmp_dir/rclone.zip"
    python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$tmp_dir/rclone.zip" "$tmp_dir"
    rclone_bin="$(find "$tmp_dir" -type f -name rclone | head -n 1)"
    install -m 0755 "$rclone_bin" /usr/local/bin/rclone
  fi
  rm -rf "$tmp_dir"
fi

cat > "$RCLONE_CONFIG_PATH" <<EOF
[nm-aihuanxin]
type = s3
provider = ${NM_S3_PROVIDER}
access_key_id = ${NM_S3_ACCESS_KEY_ID}
secret_access_key = ${NM_S3_SECRET_ACCESS_KEY}
endpoint = ${NM_S3_ENDPOINT}
EOF

rclone_base=(rclone --config "$RCLONE_CONFIG_PATH" --s3-no-check-bucket --fast-list)

"${rclone_base[@]}" copy "${S3_ROOT}/scripts" "${REMOTE_ROOT}/scripts" \
  --include 'ai_codex_local_bootstrap_remote.sh' \
  --include 'install_codex_standalone.sh' \
  --include 'render_codex_local_config.py' \
  --include 'serve_openai_chat_adapter.py' \
  --transfers 4 --checkers 8

"${rclone_base[@]}" copy "${S3_ROOT}/training" "${REMOTE_ROOT}/training" \
  --include 'model_backend.py' \
  --include 'model_family_preflight.py' \
  --include 'qwen_sft_peft.py' \
  --include 'runtime_overlay.py' \
  --include 'text_preprocessor_backend.py' \
  --transfers 4 --checkers 8

"${rclone_base[@]}" copy "${S3_ROOT}/evals/runner" "${REMOTE_ROOT}/evals/runner" \
  --include 'candidate_sanitize.py' \
  --transfers 2 --checkers 4

"${rclone_base[@]}" copy "${S3_ROOT}/${BASE_MODEL_PATH}" "$base_model_abs" \
  --transfers 8 --checkers 16

"${rclone_base[@]}" copy "${S3_ROOT}/${ADAPTER_PATH}" "$adapter_abs" \
  --transfers 4 --checkers 8

if ! python3 -c "import importlib.util, sys; mods=['accelerate','peft']; missing=[m for m in mods if not importlib.util.find_spec(m)]; sys.exit(0 if not missing else 1)"; then
  rm -rf "$WHEELHOUSE_DIR"
  mkdir -p "$WHEELHOUSE_DIR"
  "${rclone_base[@]}" copy "${S3_ROOT}/tools/wheels" "$WHEELHOUSE_DIR" \
    --include '*.whl' \
    --transfers 2 --checkers 4 >/dev/null 2>&1 || true
  if compgen -G "$WHEELHOUSE_DIR/*.whl" >/dev/null; then
    python3 -m pip install --no-input "$WHEELHOUSE_DIR"/*.whl || true
  fi
  python3 -c "import importlib.util, sys; mods=['accelerate','peft']; missing=[m for m in mods if not importlib.util.find_spec(m)]; sys.exit(0 if not missing else 1)" \
    || python3 -m pip install --no-input accelerate peft
fi

if ! command -v codex >/dev/null 2>&1; then
  tmp_dir="$(mktemp -d)"
  preseeded_codex_ok=0
  if "${rclone_base[@]}" copyto "$PRESEEDED_CODEX_ARCHIVE_S3_PATH" "$tmp_dir/codex.tar.gz" >/dev/null 2>&1; then
    tar -xzf "$tmp_dir/codex.tar.gz" -C "$tmp_dir"
    codex_bin="$(find "$tmp_dir" -maxdepth 2 -type f \( -name 'codex' -o -name 'codex-*unknown-linux-musl' \) | head -n 1)"
    if [[ -n "$codex_bin" && -f "$codex_bin" ]]; then
      install -m 0755 "$codex_bin" /root/.local/bin/codex
      ln -sf /root/.local/bin/codex /usr/local/bin/codex
      preseeded_codex_ok=1
    fi
  fi
  rm -rf "$tmp_dir"
  if [[ "$preseeded_codex_ok" != "1" ]]; then
    bash "${REMOTE_ROOT}/scripts/install_codex_standalone.sh" --shim-path /usr/local/bin/codex
  fi
fi

codex --version

python3 "${REMOTE_ROOT}/scripts/render_codex_local_config.py" \
  --model-name "$MODEL_ALIAS" \
  --base-url http://127.0.0.1:8000/v1 \
  --env-key LOCAL_CODEX_API_KEY \
  --wire-api responses \
  --supports-websockets false \
  --personality pragmatic \
  --workspace-root "$REMOTE_ROOT" \
  --trust-root "$REMOTE_ROOT" > /root/.codex/config.toml

pkill -f 'serve_openai_chat_adapter.py' >/dev/null 2>&1 || true
rm -f "$SERVER_LOG_PATH"

nohup env \
  PYTHONUNBUFFERED=1 \
  PYTHONPYCACHEPREFIX=/tmp/pycache \
  ASCEND_RT_VISIBLE_DEVICES="${ASCEND_RT_VISIBLE_DEVICES:-6}" \
  LOCAL_CODEX_API_KEY="$LOCAL_CODEX_API_KEY" \
  python3 "${REMOTE_ROOT}/scripts/serve_openai_chat_adapter.py" \
    --base-model "$base_model_abs" \
    --adapter "$adapter_abs" \
    --model-name "$MODEL_ALIAS" \
    --device "$SERVER_DEVICE" \
    --max-new-tokens "$SERVER_MAX_NEW_TOKENS" \
    --host 127.0.0.1 \
    --port 8000 > "$SERVER_LOG_PATH" 2>&1 < /dev/null &

sleep 20
curl --noproxy '*' -fsS http://127.0.0.1:8000/health

rm -f "$CODEX_OUTPUT_PATH"
printf '' | codex exec \
  --skip-git-repo-check \
  --color never \
  -C "$REMOTE_ROOT" \
  -p local \
  -m "$MODEL_ALIAS" \
  -o "$CODEX_OUTPUT_PATH" \
  "$PROMPT"

echo "__AI_CODEX_READY__:codex -p local -m ${MODEL_ALIAS}"
echo "__AI_CODEX_RESULT__"
cat "$CODEX_OUTPUT_PATH"
