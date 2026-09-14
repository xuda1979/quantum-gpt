#!/usr/bin/env bash
# Quick ASI3 auth fix - verifies connection (headless-only; browser tabs are banned).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# BANNED: Safari SSO bridge opens real browser tabs. Permanently disabled.
export HUANXIN_ALLOW_SAFARI_SSO_BRIDGE=0
export HUANXIN_ALLOW_STANDALONE_FALLBACK=1
export HUANXIN_WAIT_MS=120000

echo "Fixing ASI3 auth (headless only, no browser tabs)..."
echo ""

bash "$ROOT_DIR/scripts/huanxin_shell.sh" ASI3 \
  "echo AUTH_OK && echo REMOTE=\$(hostname) && echo NPUS=\$(nproc) && ls /root/work/filestorage/Qwen3.8-27B/ | head -3"

echo ""
echo "Auth check complete. If AUTH_OK was printed, ASI3 is ready."
