#!/usr/bin/env bash
# One-shot status snapshot for the R&D loop. Safe to run locally.
# Prints: training jobs, recent eval JSONs, recent outputs, and any new
# files in coord/ or docs/ written by other sessions.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== R&D status @ $(date '+%Y-%m-%dT%H:%M:%S%z') ==="
echo

echo "--- Other sessions' recent files (last 2h) ---"
find . -maxdepth 4 -newermt "$(date -v-2H '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -d '2 hours ago' '+%Y-%m-%d %H:%M:%S')" -type f \
  -not -path "./.git/*" -not -path "*/__pycache__/*" -not -path "./tmp/*" \
  -not -path "*/.pytest_cache/*" -not -name ".DS_Store" \
  2>/dev/null | head -30
echo

echo "--- coord/SESSION_CLAIMS.md (last 20 lines) ---"
tail -20 coord/SESSION_CLAIMS.md 2>/dev/null || echo "(none)"
echo

echo "--- Recent outputs/ (last 5 dirs by mtime) ---"
ls -dt outputs/*/ 2>/dev/null | head -5
echo

echo "--- Recent eval JSONs (last 5 by mtime) ---"
find outputs reports -name "eval-*.json" -o -name "*base_vs_adapter*.json" 2>/dev/null \
  | head -5 | while read f; do ls -la "$f"; done
echo

echo "--- Local task queue (background jobs) ---"
jobs -l 2>/dev/null || echo "(none in this shell)"
echo

echo "--- ASI1/2/3 quick probe (skip if offline) ---"
for env in ASI1 ASI2 ASI3; do
  if [ -f ".huanxin_shell_connections/${env}.json" ]; then
    echo "  ${env}: connection file present"
  else
    echo "  ${env}: no connection file"
  fi
done
echo "=== end status ==="
