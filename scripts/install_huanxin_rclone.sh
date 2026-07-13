#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${1:-AI}"
REMOTE_DIR="${HUANXIN_RCLONE_REMOTE_DIR:-/tmp}"
WAIT_MS="${HUANXIN_RCLONE_WAIT_MS:-120000}"

cd "$ROOT_DIR"

tmp_dir="$(mktemp -d)"
timestamp="$(date +%s)"
remote_script_name="install-rclone-${timestamp}.sh"
local_script_path="$tmp_dir/$remote_script_name"

cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

cat > "$local_script_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail

mkdir -p /usr/local/bin
if ! command -v rclone >/dev/null 2>&1; then
  candidate_version="\$(apt-cache policy rclone | sed -n 's/^  Candidate: //p' | head -n 1)"
  if [[ -z "\$candidate_version" || "\$candidate_version" == "(none)" ]]; then
    candidate_version='1.53.3-4ubuntu1.22.04.3'
  fi
  arch="\$(dpkg --print-architecture)"
  deb_url="https://ports.ubuntu.com/ubuntu-ports/pool/universe/r/rclone/rclone_\${candidate_version}_\${arch}.deb"
  tmp_deb="\$(mktemp /tmp/rclone.XXXXXX.deb)"
  cleanup() {
    rm -f "\$tmp_deb"
  }
  trap cleanup EXIT
  curl -fsSL "\$deb_url" -o "\$tmp_deb"
  dpkg -i "\$tmp_deb"
fi

echo __RCLONE_PATH__
command -v rclone
echo __RCLONE_VERSION__
rclone version | sed -n '1,3p'
EOF

chmod 0755 "$local_script_path"

node browser-automation/huanxin_shell_sync.js "$ENV_NAME" --remote-dir "$REMOTE_DIR" --source "$local_script_path"

printf -v remote_command 'script_path=$(find %q -type f -name %q | head -n 1); test -n "$script_path"; bash "$script_path"; rm -f "$script_path"' "$REMOTE_DIR" "$remote_script_name"
json_out="$(node browser-automation/huanxin_shell_exec.js "$ENV_NAME" --skip-daemon --wait-ms "$WAIT_MS" --command "$remote_command")"

python3 - <<'PY' "$json_out" "$ENV_NAME"
import json
import sys

payload = json.loads(sys.argv[1])
env_name = sys.argv[2]
output = payload.get("output", "")

if not payload.get("ok") or payload.get("commandStatus") != 0:
    raise SystemExit(f"rclone install failed on {env_name}: {json.dumps(payload, ensure_ascii=False)}")

if "__RCLONE_PATH__" not in output or "__RCLONE_VERSION__" not in output:
    raise SystemExit(f"rclone verification markers missing on {env_name}: {json.dumps(payload, ensure_ascii=False)}")

print(json.dumps(payload, indent=2, ensure_ascii=False))
PY
