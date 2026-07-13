#!/usr/bin/env bash
# Backup important artifacts to INER S3 and push pending code changes to git.
#
# This is the idempotent "save everything" entry point. Safe to run from cron.
# It does two things:
#   1. Sync code/ + outputs/ + evals/runs/ + training/ to INER S3
#      (adapters, evaluation results, run configs, scorecards, manifests).
#   2. Stage and commit any pending code changes, then push to origin.
#
# NAS note: the persistent NAS lives on the remote ASI training hosts at
# /root/work/software/quantum-gpt (see NAS_ROOT in asi1_launch_*.sh). When
# a training env is running, watch_huanxin_checkpoints_to_s3.sh relays
# checkpoints from that NAS to S3. This script covers the local side: it
# ensures anything that has landed on this Mac also reaches S3 + git.
#
# Usage:
#   scripts/backup_to_s3_and_git.sh             # do everything
#   scripts/backup_to_s3_and_git.sh --s3-only   # skip git commit/push
#   scripts/backup_to_s3_and_git.sh --git-only  # skip S3 sync
#   scripts/backup_to_s3_and_git.sh --dry-run   # pass --dry-run to rclone
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

S3_ONLY=0
GIT_ONLY=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --s3-only)  S3_ONLY=1 ;;
    --git-only) GIT_ONLY=1 ;;
    --dry-run)  DRY_RUN=1 ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

# ── S3 backup ─────────────────────────────────────────────────────────────
if [[ $GIT_ONLY -eq 0 ]]; then
  echo "=== [$(date -u +%FT%TZ)] S3 backup starting ==="
  source "$ROOT_DIR/scripts/iner_s3_env.sh"
  CONFIG_PATH="$(mktemp /tmp/iner-rclone-backup.XXXXXX)"
  trap 'rm -f "$CONFIG_PATH"' EXIT
  iner_write_rclone_config "$CONFIG_PATH"

  RCLONE_ARGS=(--config "$CONFIG_PATH" --s3-no-check-bucket --fast-list
               --transfers 8 --checkers 16
               --exclude ".DS_Store" --exclude "__pycache__/**")
  if [[ $DRY_RUN -eq 1 ]]; then
    RCLONE_ARGS+=(--dry-run)
  fi

  # 1a. Code + small docs/coord (the bulk upload script already excludes
  # outputs/, models/, logs/, data/generated/, runtime-bundles).
  echo "--- code/ ---"
  rclone copy "$ROOT_DIR" "${INER_S3_ROOT}" "${RCLONE_ARGS[@]}" \
    --exclude "outputs/**" --exclude "models/**" --exclude "logs/**" \
    --exclude "data/generated/**" --exclude "artifacts/runtime-bundles/**" \
    --exclude "browser-automation/profile*/**" --exclude ".venv*/**" \
    --exclude ".git/**" 2>&1 | tail -5 || true

  # 1b. Adapters + run configs + metrics (the "important files").
  echo "--- outputs/ ---"
  rclone copy "$ROOT_DIR/outputs/" "${INER_S3_ROOT}/outputs/" "${RCLONE_ARGS[@]}" 2>&1 | tail -5 || true

  # 1c. Evaluation results: scorecards, manifests, candidate maps, generation logs.
  echo "--- evals/runs/ ---"
  rclone copy "$ROOT_DIR/evals/runs/" "${INER_S3_ROOT}/evals/runs/" "${RCLONE_ARGS[@]}" 2>&1 | tail -5 || true

  # 1d. Training configs / plans (small, but valuable).
  echo "--- training/ ---"
  rclone copy "$ROOT_DIR/training/" "${INER_S3_ROOT}/training/" "${RCLONE_ARGS[@]}" 2>&1 | tail -5 || true

  echo "=== S3 backup done ==="
fi

# ── Git commit + push ─────────────────────────────────────────────────────
if [[ $S3_ONLY -eq 0 ]]; then
  echo "=== [$(date -u +%FT%TZ)] git sync starting ==="
  BRANCH="$(git rev-parse --abbrev-ref HEAD)"

  # Stage tracked modifications + deletions. Do NOT mass-add untracked files
  # (large generated dirs are gitignored on purpose).
  git add -u

  # Stage a curated set of new code files if present (safe, small).
  for f in MEMORY.md docs/STATE.md scripts/iter3_reference_solutions.py; do
    [[ -f "$f" ]] && git add "$f"
  done

  if git diff --cached --quiet; then
    echo "no staged changes; skipping commit"
  else
    SUMMARY="$(git diff --cached --stat | tail -1)"
    git commit -m "chore(backup): periodic sync $(date -u +%FT%TZ)

$SUMMARY

Co-Authored-By: Claude Code <noreply@anthropic.com>"
  fi

  # Push (best-effort; never force).
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    git push origin "$BRANCH" 2>&1 | tail -5 || echo "push failed (offline?)"
  else
    echo "no upstream set for $BRANCH; skipping push"
  fi
  echo "=== git sync done ==="
fi

echo "=== [$(date -u +%FT%TZ)] backup_to_s3_and_git complete ==="
