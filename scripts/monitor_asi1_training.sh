#!/usr/bin/env bash
# Monitor the running Qwen3.6-27B training process on ASI1 once an hour,
# logging progress/throughput/losses locally and sending updates if needed.
# This script is intended to run as a local background daemon on the Mac.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MON_LOG="/tmp/asi1_qwen27b_hourly_monitor.log"
STATE_FILE="/tmp/asi1_qwen27b_last_state.json"

echo "=== ASI1 27B SFT Monitor Daemon Started at $(date) ===" | tee -a "$MON_LOG"

while :; do
  echo "Checking training progress at $(date)..." >> "$MON_LOG"

  # Run remote query and extract payload securely
  scripts/huanxin_env_shell.sh --env ASI1 "L=/workspace/logs/asi1_qwen36_27b_verified10k_20260616.log; { echo PROC=\$(ps -p \$(cat /tmp/asi1_qwen36_27b_sft.pid) -o stat= 2>/dev/null || echo DEAD); echo NLINES=\$(wc -l < \$L 2>/dev/null || echo 0); echo TB=\$(grep -c Traceback \$L 2>/dev/null || echo 0); echo '--KEY--'; grep -nE 'trainable params|loss|\"step\"' \$L 2>/dev/null | tail -15; } > /tmp/diag_hourly.txt 2>&1; cut -c1-220 /tmp/diag_hourly.txt" > /tmp/mon_hourly.json 2>&1 || true

  if [ -s /tmp/mon_hourly.json ]; then
    python3 - <<'PY' >> "$MON_LOG" 2>&1
import json
import os
import re

try:
    with open('/tmp/mon_hourly.json') as f:
        raw = f.read()
    s = raw.find('{')
    if s == -1:
        print("[Error] No JSON block in command output")
        sys.exit(0)
    data = json.loads(raw[s:])
    output = data.get('output', '')

    # Store or parse
    with open('/tmp/asi1_qwen27b_last_raw.txt', 'w') as f:
        f.write(output)

    lines = output.splitlines()
    proc = "DEAD"
    nlines = "0"
    tb = "0"
    last_step_line = ""

    for line in lines:
        if line.startswith("PROC="):
            proc = line.split("=", 1)[1].strip()
        elif line.startswith("NLINES="):
            nlines = line.split("=", 1)[1].strip()
        elif line.startswith("TB="):
            tb = line.split("=", 1)[1].strip()
        elif '"step"' in line:
            last_step_line = line

    print(f"[{os.popen('date').read().strip()}] PROC={proc} | NLINES={nlines} | TB={tb}")
    if last_step_line:
        print(f"  Last step metric: {last_step_line}")

    # Write current parsed state
    state = {
        "proc": proc,
        "nlines": nlines,
        "tb": tb,
        "last_step": last_step_line,
        "updated_at": os.popen('date').read().strip()
    }
    with open('/tmp/asi1_qwen27b_last_state.json', 'w') as f:
        json.dump(state, f, indent=2)
except Exception as e:
    print(f"[Error] Failed to parse monitor output: {e}")
PY
  else:
    echo "[$(date)] [Warning] Zero-byte or missing JSON monitor output" | tee -a "$MON_LOG"
  fi

  echo "Sleeping for 3600 seconds until the next check..." >> "$MON_LOG"
  sleep 3600
done
