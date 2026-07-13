#!/usr/bin/env bash
# Resumable multi-part shell-stream upload of a local file to a Huanxin env when
# the S3 relay is unreachable from that env. Splits the source into parts, skips
# parts already present remotely (sha256 match), uploads the rest via the proven
# chunked small-file helper, then concatenates + verifies + (optionally) extracts.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_NAME="${1:?env name required}"
SOURCE="${2:?local source file required}"
REMOTE_PATH="${3:?remote path required}"
PART_BYTES="${PART_BYTES:-2000000}"
CHUNK_BYTES="${CHUNK_BYTES:-48000}"
CHUNKS_PER_COMMAND="${CHUNKS_PER_COMMAND:-4}"
EXTRACT_DIR="${EXTRACT_DIR:-}"
MAX_RETRIES="${MAX_RETRIES:-5}"
RETRY_SLEEP_SEC="${RETRY_SLEEP_SEC:-8}"
REMOTE_TIMEOUT_SEC="${REMOTE_TIMEOUT_SEC:-210}"

WORK="$(mktemp -d -t asi1parts.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

LOCAL_SHA="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
TOTAL_BYTES="$(wc -c < "$SOURCE" | tr -d '[:space:]')"
split -b "$PART_BYTES" "$SOURCE" "$WORK/part_"
PARTS=("$WORK"/part_*)
NPARTS="${#PARTS[@]}"
REMOTE_DIR="$(dirname "$REMOTE_PATH")"
echo "[partupload] source=$SOURCE bytes=$TOTAL_BYTES sha=$LOCAL_SHA parts=$NPARTS part_bytes=$PART_BYTES"

remote() {
  perl -e 'alarm shift @ARGV; exec @ARGV' "$REMOTE_TIMEOUT_SEC" \
    env HUANXIN_WAIT_MS=180000 \
    bash scripts/huanxin_env_shell.sh --env "$ENV_NAME" "$1"
}

remote_with_retry() {
  local cmd="$1"
  local attempt=1
  while :; do
    if remote "$cmd"; then
      return 0
    fi
    if [[ "$attempt" -ge "$MAX_RETRIES" ]]; then
      return 1
    fi
    echo "[partupload] remote command failed, retry $attempt/$MAX_RETRIES after ${RETRY_SLEEP_SEC}s" >&2
    sleep "$RETRY_SLEEP_SEC"
    attempt=$((attempt + 1))
  done
}

# Ensure remote staging dir exists. Do not block the whole run if this probe is
# flaky; per-part uploads create parent dirs as needed.
if ! remote_with_retry "mkdir -p '$REMOTE_DIR/.parts'; echo __PARTS_DIR_READY__"; then
  echo "[partupload] warning: initial staging-dir probe failed; continuing with per-part upload attempts" >&2
fi

i=0
for p in "${PARTS[@]}"; do
  i=$((i+1))
  pname="$(basename "$p")"
  psha="$(shasum -a 256 "$p" | awk '{print $1}')"
  remote_part="$REMOTE_DIR/.parts/$pname"
  # Skip if already present with matching sha.
  CHECK="$(remote_with_retry "if [ -f '$remote_part' ]; then sha256sum '$remote_part' | awk '{print \$1}'; else echo MISSING; fi; echo __CHECK_DONE__" 2>/dev/null || echo '')"
  if printf '%s' "$CHECK" | grep -q "$psha"; then
    echo "[partupload] part $i/$NPARTS $pname already present (sha ok), skipping"
    continue
  fi
  echo "[partupload] uploading part $i/$NPARTS $pname ($(wc -c < "$p") bytes)"
  ok=0
  attempt=1
  while [[ "$attempt" -le "$MAX_RETRIES" ]]; do
    if HUANXIN_WAIT_MS=180000 bash scripts/huanxin_upload_small_file.sh \
      --env "$ENV_NAME" --source "$p" --remote-path "$remote_part" \
      --max-bytes "$((PART_BYTES + 1000))" --chunk-bytes "$CHUNK_BYTES" \
      --chunks-per-command "$CHUNKS_PER_COMMAND" > "$WORK/up_${i}.json" 2>&1; then
      ok=1
      break
    fi
    echo "[partupload] upload failed for $pname, retry $attempt/$MAX_RETRIES after ${RETRY_SLEEP_SEC}s" >&2
    sleep "$RETRY_SLEEP_SEC"
    attempt=$((attempt + 1))
  done
  if [[ "$ok" -ne 1 ]]; then
    echo "[partupload] FAILED part $i ($pname); see $WORK/up_${i}.json" >&2
    tail -5 "$WORK/up_${i}.json" >&2
    cp "$WORK/up_${i}.json" "/tmp/asi1_partupload_fail_${i}.json"
    exit 1
  fi
done

echo "[partupload] all parts present; assembling remotely"
ASSEMBLE="set -e
cd '$REMOTE_DIR'
cat .parts/part_* > '$REMOTE_PATH'
got=\$(sha256sum '$REMOTE_PATH' | awk '{print \$1}')
echo __REMOTE_SHA__ \$got
echo __EXPECT_SHA__ $LOCAL_SHA
if [ \"\$got\" != '$LOCAL_SHA' ]; then echo __ASSEMBLE_SHA_MISMATCH__; exit 3; fi
echo __ASSEMBLE_OK__"
if [ -n "$EXTRACT_DIR" ]; then
  ASSEMBLE="$ASSEMBLE
mkdir -p '$EXTRACT_DIR'
tar xzf '$REMOTE_PATH' -C '$EXTRACT_DIR'
echo __EXTRACT_OK__ '$EXTRACT_DIR'
rm -rf '$REMOTE_DIR/.parts'
echo __CLEANUP_OK__"
fi
remote_with_retry "$ASSEMBLE"
