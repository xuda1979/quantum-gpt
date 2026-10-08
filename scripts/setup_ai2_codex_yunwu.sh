#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_MODEL="${MODEL_ALIAS:-omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST}"
AI2_WORKSPACE_ROOT="${AI2_WORKSPACE_ROOT:-/root/work/david/software/quantum-gpt}"
YUNWU_PROXY_BASE_URL="${YUNWU_PROXY_BASE_URL:-http://127.0.0.1:8011/v1}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
STAMP="$(date +%Y%m%dT%H%M%S)"

cd "$ROOT_DIR"

effective_yunwu_api_key="${YUNWU_API_KEY:-${YUNWU_OPENAI_API_KEY:-}}"
if [[ -z "$effective_yunwu_api_key" ]]; then
  echo "missing YUNWU_API_KEY or YUNWU_OPENAI_API_KEY" >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

config_path="$tmp_dir/config.toml"
env_path="$tmp_dir/yunwu_env.sh"
remote_cmd_path="$tmp_dir/remote_command.txt"
result_path="$tmp_dir/install_result.json"

python3 scripts/render_codex_local_config.py \
  --model-name "$LOCAL_MODEL" \
  --base-url "http://127.0.0.1:8000/v1" \
  --env-key LOCAL_CODEX_API_KEY \
  --wire-api responses \
  --supports-websockets false \
  --personality pragmatic \
  --workspace-root "$AI2_WORKSPACE_ROOT" \
  --trust-root "/root/work" \
  --trust-root "/" \
  --include-yunwu \
  --yunwu-base-url "$YUNWU_PROXY_BASE_URL" \
  --yunwu-env-key LOCAL_CODEX_API_KEY \
  --yunwu-claude-env-key LOCAL_CODEX_API_KEY \
  --yunwu-gemini-env-key LOCAL_CODEX_API_KEY \
  --include-huanxin-glm52-claude \
  --huanxin-glm52-env-key HUANXIN_GLM52_API_KEY \
  >"$config_path"

python3 - <<'PY' "$env_path"
import os
import shlex
import sys
from pathlib import Path

path = Path(sys.argv[1])
effective_api_key = os.environ.get("YUNWU_API_KEY") or os.environ.get("YUNWU_OPENAI_API_KEY")
if not effective_api_key:
    raise SystemExit("missing YUNWU_API_KEY or YUNWU_OPENAI_API_KEY")

env_pairs = {
    "YUNWU_API_KEY": effective_api_key,
    "YUNWU_OPENAI_API_KEY": os.environ.get("YUNWU_OPENAI_API_KEY") or effective_api_key,
    "YUNWU_CLAUDE_API_KEY": os.environ.get("YUNWU_CLAUDE_API_KEY", ""),
    "YUNWU_CLAUDE_BASE_URL": os.environ.get("YUNWU_CLAUDE_BASE_URL", ""),
    "YUNWU_CLAUDE_MODEL": os.environ.get("YUNWU_CLAUDE_MODEL", ""),
    "YUNWU_GEMINI_API_KEY": os.environ.get("YUNWU_GEMINI_API_KEY", ""),
    "YUNWU_RELAY_S3_ROOT": os.environ.get("YUNWU_RELAY_S3_ROOT", ""),
    "YUNWU_RELAY_REQUEST_PREFIX": os.environ.get("YUNWU_RELAY_REQUEST_PREFIX", ""),
    "YUNWU_RELAY_RESPONSE_PREFIX": os.environ.get("YUNWU_RELAY_RESPONSE_PREFIX", ""),
    "YUNWU_RELAY_TIMEOUT_SECONDS": os.environ.get("YUNWU_RELAY_TIMEOUT_SECONDS", ""),
    "YUNWU_RELAY_POLL_SECONDS": os.environ.get("YUNWU_RELAY_POLL_SECONDS", ""),
}

lines = ["#!/usr/bin/env bash"]
for key, value in env_pairs.items():
    if value:
        lines.append(f"export {key}={shlex.quote(value)}")
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

python3 - <<'PY' "$config_path" "$env_path" "$remote_cmd_path" "$STAMP"
import base64
import sys
from pathlib import Path

config_b64 = base64.b64encode(Path(sys.argv[1]).read_bytes()).decode("ascii")
env_b64 = base64.b64encode(Path(sys.argv[2]).read_bytes()).decode("ascii")
remote_cmd_path = Path(sys.argv[3])
stamp = sys.argv[4]

py_code = (
    "from pathlib import Path; import base64; "
    f"config_bytes=base64.b64decode({config_b64!r}); "
    f"env_bytes=base64.b64decode({env_b64!r}); "
    "home=Path.home(); codex_dir=home/'.codex'; codex_dir.mkdir(parents=True, exist_ok=True); "
    "config_path=codex_dir/'config.toml'; env_path=codex_dir/'yunwu_env.sh'; "
    f"backup_path=codex_dir/'config.toml.pre-yunwu-{stamp}.bak'; "
    "existing_config=config_path.read_bytes() if config_path.exists() else None; "
    "backup_path.write_bytes(existing_config) if existing_config is not None else None; "
    "config_path.write_bytes(config_bytes); env_path.write_bytes(env_bytes); env_path.chmod(0o600); "
    "bashrc_path=home/'.bashrc'; existing=bashrc_path.read_text(encoding='utf-8') if bashrc_path.exists() else ''; "
    "start='# >>> quantum-gpt codex env >>>'; end='# <<< quantum-gpt codex env <<<'; "
    "block='\\n'.join([start,'export LOCAL_CODEX_API_KEY=dummy','export NO_PROXY=127.0.0.1,localhost','export no_proxy=127.0.0.1,localhost','unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY','export PATH=/root/.local/bin:/usr/local/bin:$PATH','[ -f \\\"$HOME/.codex/yunwu_env.sh\\\" ] && . \\\"$HOME/.codex/yunwu_env.sh\\\"',end,'']); "
    "replacement=(existing.split(start,1)[0].rstrip('\\n')+'\\n'+block+existing.split(start,1)[1].split(end,1)[1].lstrip('\\n')) if (start in existing and end in existing) else ((existing if existing.endswith('\\n') or existing=='' else existing+'\\n')+block); "
    "bashrc_path.write_text(replacement, encoding='utf-8'); "
    "print('INSTALL_OK'); print(f'CONFIG={config_path}'); print(f'ENV={env_path}'); print(f'BACKUP={backup_path if backup_path.exists() else \"none\"}')"
)

remote_cmd_path.write_text(f"python3 -c {py_code!r}", encoding="utf-8")
PY

remote_cmd="$(cat "$remote_cmd_path")"

HUANXIN_ALLOW_STANDALONE_FALLBACK=1 \
HUANXIN_PROFILE_COPY_NAME="${HUANXIN_PROFILE_COPY_NAME:-quantum-rnd-yunwu-setup-$STAMP}" \
node browser-automation/huanxin_shell_exec.js ai2 --skip-daemon --wait-ms "$WAIT_MS" --command "$remote_cmd" \
  >"$result_path"

python3 - <<'PY' "$result_path"
import json
import sys

payload = json.load(open(sys.argv[1], "r", encoding="utf-8"))
if not payload.get("ok"):
    raise SystemExit(json.dumps(payload, ensure_ascii=False, indent=2))
text = "\n".join(str(payload.get(key, "")) for key in ("output", "after", "before"))
if "INSTALL_OK" not in text:
    raise SystemExit(text)
print(json.dumps(payload, ensure_ascii=False, indent=2))
PY
