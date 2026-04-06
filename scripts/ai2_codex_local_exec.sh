#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S3_SCRIPTS_ROOT="nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-qwen25-coder-main/scripts"
REMOTE_ROOT="/root/root/work/quantum-gpt"
REMOTE_CODEX_BIN="/root/.local/bin/codex"
MODEL_ALIAS="${MODEL_ALIAS:-quantum-gpt-omnicoder9b.1}"
BASE_MODEL_PATH="${BASE_MODEL_PATH:-models/OmniCoder-9B}"
ADAPTER_PATH="${ADAPTER_PATH:-outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter}"
PROMPT="Reply with exactly OK and nothing else."
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
TRANSPORT="${AI2_CODEX_TRANSPORT:-direct}"
PRINT_ONLY=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai2_codex_local_exec.sh [--model-alias <name>] [--base-model <path>] [--adapter <path>] [--prompt <text>] [--wait-ms <ms>] [--transport <direct|wrapper>] [--print-only]

Stages the Codex helper scripts, syncs them to ai2, starts the local model
adapter server if needed, and runs:
  codex exec ... -p local -m <model-alias>
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
    --transport)
      TRANSPORT="${2:-}"
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
      usage
      ;;
  esac
done

case "$TRANSPORT" in
  direct|wrapper)
    ;;
  *)
    echo "invalid transport: $TRANSPORT (expected direct or wrapper)" >&2
    exit 1
    ;;
esac

shell_quote() {
  local value="${1//\'/\'\"\'\"\'}"
  printf "'%s'" "$value"
}

stage_paths=(
  scripts/install_codex_standalone.sh
  scripts/render_codex_local_config.py
  scripts/serve_openai_chat_adapter.py
)

cd "$ROOT_DIR"
if [[ "$PRINT_ONLY" != "1" ]]; then
  bash "$ROOT_DIR/scripts/push_to_s3.sh" "${stage_paths[@]}"
fi

REMOTE_CMD="cd $(shell_quote "$REMOTE_ROOT"); "
REMOTE_CMD+="grep -qxF 'export LOCAL_CODEX_API_KEY=dummy' /root/.bashrc || printf '\\nexport LOCAL_CODEX_API_KEY=dummy\\n' >> /root/.bashrc; "
REMOTE_CMD+="grep -qxF 'export NO_PROXY=127.0.0.1,localhost' /root/.bashrc || printf 'export NO_PROXY=127.0.0.1,localhost\\n' >> /root/.bashrc; "
REMOTE_CMD+="grep -qxF 'export no_proxy=127.0.0.1,localhost' /root/.bashrc || printf 'export no_proxy=127.0.0.1,localhost\\n' >> /root/.bashrc; "
REMOTE_CMD+="grep -qxF 'unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY' /root/.bashrc || printf 'unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY\\n' >> /root/.bashrc; "
REMOTE_CMD+="if [[ ! -f /root/.bash_profile ]]; then printf 'source /root/.bashrc\\n' > /root/.bash_profile; elif ! grep -qxF 'source /root/.bashrc' /root/.bash_profile; then printf '\\nsource /root/.bashrc\\n' >> /root/.bash_profile; fi; "
REMOTE_CMD+="export NO_PROXY=127.0.0.1,localhost; export no_proxy=127.0.0.1,localhost; "
REMOTE_CMD+="unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY; "
REMOTE_CMD+="rclone copy $(shell_quote "$S3_SCRIPTS_ROOT") $(shell_quote "$REMOTE_ROOT/scripts") --include 'install_codex_standalone.sh' --include 'render_codex_local_config.py' --include 'serve_openai_chat_adapter.py' --fast-list --transfers 4 --checkers 8; "
REMOTE_CMD+="if [[ ! -x $(shell_quote "$REMOTE_CODEX_BIN") ]]; then bash scripts/install_codex_standalone.sh --shim-path /usr/local/bin/codex; fi; "
REMOTE_CMD+="export PATH=/root/.local/bin:/usr/local/bin:\$PATH; "
REMOTE_CMD+="CODEX_CMD=\$(command -v codex || true); "
REMOTE_CMD+="if [[ -z \"\$CODEX_CMD\" && -x $(shell_quote "$REMOTE_CODEX_BIN") ]]; then CODEX_CMD=$(shell_quote "$REMOTE_CODEX_BIN"); fi; "
REMOTE_CMD+="if [[ -z \"\$CODEX_CMD\" ]]; then echo 'Codex binary missing after setup. Expected codex on PATH or /root/.local/bin/codex.' >&2; exit 1; fi; "
REMOTE_CMD+="mkdir -p /root/.codex; "
REMOTE_CMD+="python3 scripts/render_codex_local_config.py --model-name $(shell_quote "$MODEL_ALIAS") --base-url http://127.0.0.1:8000/v1 --env-key LOCAL_CODEX_API_KEY --wire-api responses --supports-websockets false > /root/.codex/config.toml; "
REMOTE_CMD+="if ! curl --noproxy '*' -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then nohup env PYTHONUNBUFFERED=1 PYTHONPYCACHEPREFIX=/tmp/pycache ASCEND_RT_VISIBLE_DEVICES=\"\${ASCEND_RT_VISIBLE_DEVICES:-6}\" python3 scripts/serve_openai_chat_adapter.py --base-model $(shell_quote "$BASE_MODEL_PATH") --adapter $(shell_quote "$ADAPTER_PATH") --model-name $(shell_quote "$MODEL_ALIAS") --device npu --host 127.0.0.1 --port 8000 > /tmp/quantum_codex_server.log 2>&1 & sleep 12; fi; "
REMOTE_CMD+="curl --noproxy '*' -fsS http://127.0.0.1:8000/health >/dev/null; "
REMOTE_CMD+="export LOCAL_CODEX_API_KEY=dummy; "
REMOTE_CMD+="echo __CODEX_CMD__ \$CODEX_CMD; "
REMOTE_CMD+="echo __AI2_RUN_CMD__ \"\$CODEX_CMD -p local -m $(shell_quote "$MODEL_ALIAS")\"; "
REMOTE_CMD+="rm -f /tmp/codex_last.txt; "
REMOTE_CMD+="\"\$CODEX_CMD\" exec --skip-git-repo-check --color never -C $(shell_quote "$REMOTE_ROOT") -p local -m $(shell_quote "$MODEL_ALIAS") -o /tmp/codex_last.txt $(shell_quote "$PROMPT"); "
REMOTE_CMD+="echo __CODEX_OUTPUT__; cat /tmp/codex_last.txt"

if [[ "$PRINT_ONLY" == "1" ]]; then
  printf '%s\n' "$REMOTE_CMD"
  exit 0
fi

if [[ "$TRANSPORT" == "wrapper" ]]; then
  HUANXIN_WAIT_MS="$WAIT_MS" bash "$ROOT_DIR/scripts/ai2_shell.sh" "$REMOTE_CMD"
else
  node "$ROOT_DIR/browser-automation/huanxin_shell_exec.js" ai2 --skip-daemon --wait-ms "$WAIT_MS" --command "$REMOTE_CMD"
fi
