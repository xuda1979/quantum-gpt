#!/usr/bin/env bash
# =============================================================================
# sapo_cleanup_stale.sh — GUARDED stale-proc cleanup for pre-launch GO prep.
#
# Class-extinction fix (executor defect, 2026-08-27): the earlier box-prep
# cleanup SIGKILLed ANY process matching fv_gspo_repair_sidecar as "stale" —
# including the NEW run's live sidecar (untrappable kill -> frozen log ->
# silent starvation -> breaker stopping a healthy trainer; killed runs 11/12).
#
# Guards (repair-lane notes /tmp/sapo_run12_bootverify_NOTES.txt + coordinator):
#   G0: NEVER run the kill loop after a sidecar is up — if any LIVE
#       repair_sidecar.pid exists under the outputs root, skip everything.
#   G1: NEVER run the kill loop while a trainer process is alive (daemon-retry
#       safety — a retried GO script must not touch a launched run).
#   G2: target the SPECIFIC stale run dir, never pgrep-wide — a candidate is
#       killed only if its cmdline does NOT reference the protected run dir
#       (and, when --stale-run is given, only if it DOES reference it).
#
# Usage: bash scripts/sapo_cleanup_stale.sh \
#          [--outputs-root DIR] [--protect-run RUN_DIR] [--stale-run RUN_DIR]
#   --outputs-root  dir containing sapo-27b-ai-*/ run dirs (default: $PWD/outputs)
#   --protect-run   run dir whose sidecar/sync daemon must NEVER be killed
#   --stale-run     optional exact run dir to target (kills ONLY that dir's procs)
# Exit: 0 always (operational script; guards make it a no-op when unsafe).
# =============================================================================
set -uo pipefail

OUTPUTS_ROOT="${OUTPUTS_ROOT:-$PWD/outputs}"
# Resolve to an absolute path: run dirs in candidate cmdlines are absolute, so
# the G3 scope match below needs the root in absolute form too.
OUTPUTS_ROOT="$(cd "$OUTPUTS_ROOT" 2>/dev/null && pwd || printf '%s' "$OUTPUTS_ROOT")"
PROTECT_RUN=""
STALE_RUN=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --outputs-root) OUTPUTS_ROOT="${2:-$OUTPUTS_ROOT}"; shift 2 ;;
    --protect-run) PROTECT_RUN="${2:-}"; shift 2 ;;
    --stale-run) STALE_RUN="${2:-}"; shift 2 ;;
    *) echo "usage: $0 [--outputs-root DIR] [--protect-run RUN_DIR] [--stale-run RUN_DIR]" >&2; exit 2 ;;
  esac
done

log() { printf '[%s] %s\n' "$(date -u +%H:%M:%SZ)" "$*"; }

# --- G0: sidecar already up (live pidfile) -> never kill after that ----------
for pf in "$OUTPUTS_ROOT"/sapo-27b-ai-*/repair_sidecar.pid; do
  [[ -f "$pf" ]] || continue
  pid="$(cat "$pf" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    log "G0 skip: live repair_sidecar.pid $pf -> pid $pid (sidecar is up; kill loop never runs after that)"
    exit 0
  fi
done

# --- G1: trainer alive -> skip everything (retry/post-launch safety) ----------
if pgrep -f 'training/[g]rpo_trainer.py' >/dev/null 2>&1; then
  log "G1 skip: trainer process alive (kill loop never runs while training is live)"
  exit 0
fi

# --- Collect candidates once (snapshot; no re-reads) --------------------------
candidates=""
for pid in $(pgrep -f 'checkpoint_sync_[d]aemon.sh|fv_gspo_repair_[s]idecar.sh' 2>/dev/null || true); do
  [[ "$pid" =~ ^[0-9]+$ ]] || continue
  cmd="$(ps -p "$pid" -o args= 2>/dev/null || true)"
  # G3 (repairq 2026-09-01): the kill loop is scoped to THIS outputs root.
  # The pgrep match is global — without the scope, cleanup SIGKILLs ANY
  # sidecar/sync-daemon matching the pattern on the box, including a
  # CONCURRENT run's live sidecar whose run dir is under a different root
  # (the runs-11/12 killer this file documents, reproduced locally when the
  # liveness-guard and cleanup-stale suites run in one session).
  if [[ "$cmd" != *"$OUTPUTS_ROOT"* ]]; then
    log "G3 skip (not this outputs root): pid=$pid ($cmd)"
    continue
  fi
  # G2: protected run dir is never a target.
  if [[ -n "$PROTECT_RUN" && "$cmd" == *"$PROTECT_RUN"* ]]; then
    log "G2 protect: pid=$pid ($cmd)"
    continue
  fi
  # G2: when targeting a specific stale run, kill ONLY that dir's procs.
  if [[ -n "$STALE_RUN" ]]; then
    if [[ "$cmd" != *"$STALE_RUN"* ]]; then
      log "G2 skip (not target): pid=$pid ($cmd)"
      continue
    fi
  fi
  candidates="$candidates $pid"
done

if [[ -z "${candidates// /}" ]]; then
  log "no stale procs found"
  exit 0
fi

for pid in $candidates; do
  log "TERM stale pid=$pid"
  kill -TERM "$pid" 2>/dev/null || true
done
sleep 3
for pid in $candidates; do
  if kill -0 "$pid" 2>/dev/null; then
    log "KILL stale pid=$pid"
    kill -KILL "$pid" 2>/dev/null || true
  fi
done
log "cleanup done"
