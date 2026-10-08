#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ENV="${SOURCE_ENV:-ai2}"
TARGET_ENV="${TARGET_ENV:-AI}"
SOURCE_ROOT="${SOURCE_ROOT:-/root/root/work/quantum-gpt}"
ALT_SOURCE_ROOT="${ALT_SOURCE_ROOT:-/root/work/quantum-gpt}"
TARGET_ROOT="${TARGET_ROOT:-/root/software/quantum-gpt}"
RELAY_ROOT="${RELAY_ROOT:-nm-aihuanxin:jtdlp-3ed7854b946a47b1a49ad754baa76cd3/quantum-gpt-ai-migration}"
WAIT_MS="${HUANXIN_WAIT_MS:-180000}"
DRY_RUN=0
SKIP_SOURCE_PUSH=0
SKIP_TARGET_PULL=0

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/migrate_ai2_quantum_gpt_to_ai.sh [--dry-run] [--skip-source-push] [--skip-target-pull]

Copies the whole remote quantum-gpt project, including models and outputs, from
the historical ai2 environment to the AI environment under ~/software/quantum-gpt.

Defaults:
  SOURCE_ENV=ai2
  SOURCE_ROOT=/root/root/work/quantum-gpt
  ALT_SOURCE_ROOT=/root/work/quantum-gpt
  TARGET_ENV=AI
  TARGET_ROOT=/root/software/quantum-gpt
  RELAY_ROOT=nm-aihuanxin:.../quantum-gpt-ai-migration
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --skip-source-push) SKIP_SOURCE_PUSH=1; shift ;;
    --skip-target-pull) SKIP_TARGET_PULL=1; shift ;;
    --help|-h) usage ;;
    *) echo "unknown option: $1" >&2; usage ;;
  esac
done

cd "$ROOT_DIR"

remote_quote() {
  printf '%q' "$1"
}

source_probe_cmd=$(cat <<EOF
set -euo pipefail
if [ -d $(remote_quote "$SOURCE_ROOT") ]; then src=$(remote_quote "$SOURCE_ROOT"); elif [ -d $(remote_quote "$ALT_SOURCE_ROOT") ]; then src=$(remote_quote "$ALT_SOURCE_ROOT"); else echo "SOURCE_ROOT_MISSING $(remote_quote "$SOURCE_ROOT") $(remote_quote "$ALT_SOURCE_ROOT")"; exit 4; fi
echo "__MIGRATE_SOURCE_ROOT__:\$src"
du -sh "\$src" 2>/dev/null || true
find "\$src/models" -maxdepth 2 -type f \\( -name "config.json" -o -name "*.safetensors" \\) 2>/dev/null | head -80 || true
command -v rclone
rclone version | head -5
EOF
)

target_probe_cmd=$(cat <<EOF
set -euo pipefail
mkdir -p $(remote_quote "$TARGET_ROOT")
cd $(remote_quote "$TARGET_ROOT")
echo "__MIGRATE_TARGET_ROOT__:\$(pwd)"
command -v rclone
rclone version | head -5
EOF
)

echo "== Probe source $SOURCE_ENV =="
HUANXIN_WAIT_MS="$WAIT_MS" HUANXIN_ALLOW_STANDALONE_FALLBACK=1 \
  bash scripts/huanxin_shell.sh "$SOURCE_ENV" "$source_probe_cmd"

echo "== Probe target $TARGET_ENV =="
HUANXIN_WAIT_MS="$WAIT_MS" \
  bash scripts/huanxin_shell.sh "$TARGET_ENV" "$target_probe_cmd"

dry_flag=""
if [[ $DRY_RUN -eq 1 ]]; then
  dry_flag=" --dry-run"
fi

if [[ $SKIP_SOURCE_PUSH -eq 0 ]]; then
  source_push_cmd=$(cat <<EOF
set -euo pipefail
if [ -d $(remote_quote "$SOURCE_ROOT") ]; then src=$(remote_quote "$SOURCE_ROOT"); else src=$(remote_quote "$ALT_SOURCE_ROOT"); fi
test -d "\$src"
log=/tmp/quantum_gpt_ai2_to_ai_source_push.log
cd "\$(dirname "\$src")"
rclone sync "\$(basename "\$src")" $(remote_quote "$RELAY_ROOT") --s3-no-check-bucket --fast-list --transfers 8 --checkers 16 --progress$dry_flag >"\$log" 2>&1
rc=\$?
echo "__MIGRATE_SOURCE_PUSH_RC__:\$rc"
tail -n 80 "\$log"
exit \$rc
EOF
)
  echo "== Push source $SOURCE_ENV -> relay =="
  HUANXIN_WAIT_MS="$WAIT_MS" HUANXIN_ALLOW_STANDALONE_FALLBACK=1 \
    bash scripts/huanxin_shell.sh "$SOURCE_ENV" "$source_push_cmd"
fi

if [[ $SKIP_TARGET_PULL -eq 0 ]]; then
  target_pull_cmd=$(cat <<EOF
set -euo pipefail
mkdir -p $(remote_quote "$TARGET_ROOT")
log=/tmp/quantum_gpt_ai2_to_ai_target_pull.log
rclone sync $(remote_quote "$RELAY_ROOT") $(remote_quote "$TARGET_ROOT") --s3-no-check-bucket --fast-list --transfers 8 --checkers 16 --progress$dry_flag >"\$log" 2>&1
rc=\$?
echo "__MIGRATE_TARGET_PULL_RC__:\$rc"
tail -n 80 "\$log"
echo "__MIGRATE_TARGET_VERIFY__"
du -sh $(remote_quote "$TARGET_ROOT") 2>/dev/null || true
find $(remote_quote "$TARGET_ROOT")/models -maxdepth 2 -type f \\( -name "config.json" -o -name "*.safetensors" \\) 2>/dev/null | head -80 || true
exit \$rc
EOF
)
  echo "== Pull relay -> target $TARGET_ENV =="
  HUANXIN_WAIT_MS="$WAIT_MS" \
    bash scripts/huanxin_shell.sh "$TARGET_ENV" "$target_pull_cmd"
fi
