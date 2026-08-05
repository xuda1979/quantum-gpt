#!/usr/bin/env bash
# =============================================================================
# Monitor the FV-GSPO ASI2 run through the headless browser daemon's /exec
# transport (no Huanxin page interaction needed after launch).
#
# Usage:
#   bash scripts/monitor_asi2_fv_gspo.sh            # ASI2 daemon, port 19004
#   bash scripts/monitor_asi2_fv_gspo.sh 19004
#
# Prereqs:
#   - The daemon is running: node browser-automation/huanxin_browser_daemon.js ASI2
#   - The repo is synced to the remote root (git pull on the box).
#
# Prints: remote launch status + compact FV-GSPO metrics status.
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DAEMON_PORT="${1:-19004}"
REMOTE_ROOT="${ASI2_GRPO_REMOTE_ROOT:-/root/work/software/quantum-gpt}"
BASE="http://127.0.0.1:${DAEMON_PORT}"

jq_escape() {
  python3 -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1"
}

exec_cmd() {
  local cmd="$1"
  curl -s --max-time 120 -X POST "${BASE}/exec" -H 'Content-Type: application/json' \
    -d "{\"command\": $(jq_escape "$cmd"), \"waitMs\": 90000}"
}

echo "=== remote launch status ==="
exec_cmd "bash ${REMOTE_ROOT}/scripts/asi2_launch_grpo_27b_selfeval.sh status" |
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except json.JSONDecodeError:
    print("daemon unreachable or not running")
    sys.exit(1)
print((d.get("output") or d.get("error") or json.dumps(d))[:3000])
'

echo ""
echo "=== FV-GSPO run metrics ==="
exec_cmd "cd ${REMOTE_ROOT} && python3 scripts/remote_grpo_status.py" |
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except json.JSONDecodeError:
    print("no parseable status; daemon busy?")
    sys.exit(0)
print(json.dumps(d, ensure_ascii=False, indent=1))
'
