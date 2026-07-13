#!/usr/bin/env bash
set -euo pipefail

# Generic Huanxin shell wrapper. The environment name is always an input.
#
# Usage:
#   scripts/huanxin_env_shell.sh --env <env-name> "<remote command>"
#   HUANXIN_TRAINING_ENV=<env-name> scripts/huanxin_env_shell.sh "<remote command>"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_NAME="${HUANXIN_TRAINING_ENV:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --help|-h)
      sed -n '1,12p' "$0"
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

if [[ -z "$ENV_NAME" || $# -lt 1 ]]; then
  echo 'Usage: scripts/huanxin_env_shell.sh --env <env-name> "<remote command>"' >&2
  exit 2
fi

export HUANXIN_DAEMON_STARTUP_MAX_POLLS="${HUANXIN_DAEMON_STARTUP_MAX_POLLS:-180}"
export HUANXIN_DAEMON_STARTUP_POLL_INTERVAL_SECONDS="${HUANXIN_DAEMON_STARTUP_POLL_INTERVAL_SECONDS:-2}"

exec bash scripts/huanxin_shell.sh "$ENV_NAME" "$*"
