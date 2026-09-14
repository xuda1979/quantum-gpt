#!/usr/bin/env bash
# BANNED: Safari SSO bridge opens real browser tabs. Permanently disabled.
export HUANXIN_ALLOW_SAFARI_SSO_BRIDGE=0
export HUANXIN_ALLOW_STANDALONE_FALLBACK=1
export HUANXIN_WAIT_MS=180000
bash scripts/huanxin_shell.sh ASI3 "echo AUTH_OK && hostname && nproc && ls /root/work/filestorage/Qwen3.8-27B/ 2>/dev/null | head -3"
