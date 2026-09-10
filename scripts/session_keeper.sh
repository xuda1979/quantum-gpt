#!/bin/bash
# session_keeper.sh — dedicated agent: keeps the Claude session + this Mac alive 24/7.
# Fixes the 2026-09-05/06 crash class: (a) headless claude CLI "Not logged in"
# (self-heals by refreshing /Users/daxu/.claude-mcp-cron/claude_headless.env from a live
# router-backed claude process), (b) Huanxin daemons down (restarts via existing scripts),
# (c) Mac sleep/logoff (asserts caffeinate; verifies user console session).
# Loop every 120s. Logs to logs/session_keeper.log with heartbeats. Never opens browser tabs.
set -u
# launchd context safety: minimal but complete env for nested claude calls
export HOME="${HOME:-/Users/daxu}"
export USER="${USER:-daxu}"
export PATH="${PATH:-/usr/bin:/bin:/usr/sbin:/sbin:/Users/daxu/homebrew/bin:/Users/daxu/.local/bin}"
ROOT="/Users/daxu/software/quantum-gpt"
LOG="$ROOT/logs/session_keeper.log"
ENVF="/Users/daxu/.claude-mcp-cron/claude_headless.env"
CLAUDE="/Users/daxu/homebrew/bin/claude"
HEARTBEAT="/tmp/session_keeper_state.json"
mkdir -p "$ROOT/logs"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

stamp_state() {  # durable JSON heartbeat every cycle
  # B-035(a): takes the keeper shell pid as $4 so the heartbeat pid field is the
  # long-lived keeper process, NOT the transient python3 heredoc (phantom-restart
  # alarm class). Falls back to the heredoc pid only when $4 is empty.
  python3 - "$1" "$2" "$3" "$4" <<'EOF'
import json, sys, datetime, os
status, headless, daemons, keeper_pid = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
     "status": status, "headless_auth": headless, "daemons": daemons,
     "pid": int(keeper_pid) if keeper_pid else os.getpid(), "uptime_s": None}
try:
    with open("/proc/uptime") as f: d["uptime_s"] = float(f.read().split()[0])
except Exception: pass
json.dump(d, open(os.environ.get("SK_HEARTBEAT", "/tmp/session_keeper_state.json"), "w"))
EOF
}

headless_ok() {
  bash -c "source '$ENVF' 2>/dev/null; '$CLAUDE' --print 'reply AUTH-OK only' < /dev/null" 2>/dev/null | grep -q "AUTH-OK"
}

refresh_env_from_live_process() {
  # find a live router-backed claude process with a valid AUTH_TOKEN env
  # ps-based scan (pgrep -f missed processes in some visibility contexts)
  for pid in $(ps aux | grep -E "bin/claude" | grep -v grep | awk '{print $2}'); do
    tok=$(ps eww "$pid" 2>/dev/null | tr ' ' '\n' | grep -oE "^ANTHROPIC_AUTH_TOKEN=.+" | head -1 | cut -d= -f2-)
    [ -z "$tok" ] && continue
    base=$(ps eww "$pid" 2>/dev/null | tr ' ' '\n' | grep -oE "^ANTHROPIC_BASE_URL=.+" | head -1 | cut -d= -f2-)
    [ -z "$base" ] && continue
    # write candidate env atomically
    TMP="$ENVF.candidate.$$"
    {
      echo "# refreshed by session_keeper $(date '+%F %T') from pid $pid"
      echo "export ANTHROPIC_BASE_URL=\"$base\""
      echo "export ANTHROPIC_AUTH_TOKEN=\"$tok\""
      PE=$(ps eww "$pid" 2>/dev/null | tr ' ' '\n')
      for MV in ANTHROPIC_MODEL ANTHROPIC_SMALL_FAST_MODEL ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_OPUS_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL; do
        V=$(echo "$PE" | grep -oE "^$MV=.+" | head -1)
        [ -n "$V" ] && echo "export $V"
      done
    } > "$TMP" && chmod 600 "$TMP"
    # verify the candidate actually works before adopting
    if mv "$TMP" "$ENVF.new" 2>/dev/null; then
      OLD="$ENVF.old.$$"; [ -f "$ENVF" ] && cp "$ENVF" "$OLD"
      mv "$ENVF.new" "$ENVF"
      if headless_ok; then
        [ -n "${OLD:-}" ] && rm -f "$OLD"
        return 0
      else
        [ -n "${OLD:-}" ] && mv "$OLD" "$ENVF"  # rollback
      fi
    fi
    rm -f "$TMP" "$ENVF.new" 2>/dev/null
  done
  return 1
}

daemon_check() {
  for p in $SK_DAEMON_PORTS; do
    H=$(curl -s -m 4 "http://127.0.0.1:$p/health" 2>/dev/null)
    echo "$H" | grep -q '"ok":true' || return 1
    # 2026-09-08 blind-keeper fix: the daemon reports ok:true even in
    # startupState=error (auth-bridge failure), which stamped daemons=OK while
    # /exec was down. OK requires the daemon to actually be ready.
    echo "$H" | grep -q '"ready":true' || return 1
  done
  return 0
}

# FIX #2 (2026-09-07): detect daemon BUSY/congestion (single-exec mutex backlogged)
# — the "ok:true but output stops round-tripping" class. A daemon stuck busy for
# N consecutive keeper cycles (each ~120s) makes every exec queue behind one long
# holder; we fail-closed by restarting the daemon via the heartbeat.
# B-036 (2026-09-09): backlog-wedge bar. pendingRequestCount > 3 = wedged
# (same bar as sapo_wedge_watch.py), overridable for drills.
SK_PENDING_MAX=4
# §9.1 "keep ALL compute resources connected forever": every provisioned env's
# daemon must be watched, not just the two that happened to be listed. ASI1
# (:20646) was absent from this default, so a dead ASI1 daemon was invisible to
# the keeper — a resource nobody watches is a resource allowed to go dark.
SK_DAEMON_PORTS="${SK_DAEMON_PORTS:-20653 19004 20646}"

daemon_congested_check() {
  for p in $SK_DAEMON_PORTS; do
    # 2026-09-09 fix: the old probe called json.load(sys.stdin) TWICE - the 2nd
    # read hit EOF, the traceback was suppressed, and $busy was always empty, so
    # this check could NEVER fire (vacuous detector, shadowed-helper class).
    # B-036: also reads pendingRequestCount (-1 when absent -> never fires on
    # missing measurement, fail-safe for older daemon builds).
    state=$(curl -s -m 4 "http://127.0.0.1:$p/health" 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);pend=d.get('pendingRequestCount');pend=-1 if pend is None else pend;print(d.get('busy'), d.get('ready'), pend)" 2>/dev/null)
    # busy True + ready True = congested (busy but alive); busy True + ready False = mid-restart (not congestion)
    # B-036: ready True + pending >= SK_PENDING_MAX with busy False = backlog
    # wedge (the live 16:41Z-18:02Z ASI3 class: ready:true busy:false pending
    # 14-15 for 85+ min, invisible to every auto-heal layer until now).
    case "$state" in
      "True True"*) return 0 ;;  # congested
      "False True"*)
        pending="${state##* }"
        if [ "$pending" -ge "$SK_PENDING_MAX" ] 2>/dev/null; then
          return 0  # backlog wedge
        fi
        ;;
      *) ;;
    esac
  done
  return 1  # not congested
}

daemons_recover() {
  # B-039 (2026-09-09): the heartbeat restarts daemons ONLY on error/authfail/
  # booting>15m - a ready:true+backlogged wedge (pendingRequestCount>=bar, no
  # completions) matches NONE of those, so the heartbeat kick could never heal
  # the live 16:41Z/20:23Z ASI3 class. Restart the wedged daemon DIRECTLY:
  # POST /stop and its supervisor relaunches it. Heartbeat kick stays as the
  # fallback for the not-ready classes.
  local port wedged=0
  for port in $SK_DAEMON_PORTS; do
    local state pending
    state=$(curl -s -m 4 "http://127.0.0.1:$port/health" 2>/dev/null | python3 -c "import sys,json;d=json.load(sys.stdin);pend=d.get('pendingRequestCount');pend=-1 if pend is None else pend;print(d.get('busy'), d.get('ready'), pend)" 2>/dev/null)
    case "$state" in
      "True True"*)
        log "ACTION daemon :$port busy-congested — direct /stop restart"
        curl -s -m 5 -X POST "http://127.0.0.1:$port/stop" >/dev/null 2>&1 || true
        wedged=1 ;;
      "False True"*)
        pending="${state##* }"
        if [ "$pending" -ge "$SK_PENDING_MAX" ] 2>/dev/null; then
          log "ACTION daemon :$port backlog wedge (pending=$pending) — direct /stop restart"
          curl -s -m 5 -X POST "http://127.0.0.1:$port/stop" >/dev/null 2>&1 || true
          wedged=1
        fi ;;
    esac
  done
  if [ "$wedged" = "0" ]; then
    log "ACTION daemons not ready — running huanxin heartbeat kick"
    # the launchd heartbeat owns daemon restart; nudge it and wait one cycle
    launchctl kickstart -k "gui/$(id -u)/com.quantumgpt.huanxin-heartbeat" 2>/dev/null || true
  fi
}

# FIX #2 (2026-09-08): fail-closed on daemon OUTPUT degradation.
# The live exec round-trip probe is intentionally NOT used here: a healthy-but-
# briefly-busy daemon can exceed a 30s /exec probe and would FALSE-trigger a
# restart (worse than the bug). The reliable, low-risk detector is the
# congestion check (busy:true backlog -> the class that causes output drops);
# it restarts only after 3 consecutive busy cycles so a single long holder
# doesn't spur a restart. This keeps monitoring fail-closed without
# false-positive daemon churn.

consolesess_ok() {
  # console user session alive (guards against logoff)
  [ "$(stat -f %u /dev/console 2>/dev/null)" = "$(id -u)" ]
}

awake_ok() {
  pgrep -f "caffeinate -dimsu" >/dev/null 2>&1
}

# ── cron doctor: future cron jobs get durable auth automatically ──
cron_doctor() {
  for f in /Users/daxu/.claude-mcp-cron/jobs/*/run.sh; do
    [ -f "$f" ] || continue
    grep -q "claude_headless.env" "$f" || \
      sed -i '' 's|^done$|done\n\nif [ -f /Users/daxu/.claude-mcp-cron/claude_headless.env ]; then\n  source /Users/daxu/.claude-mcp-cron/claude_headless.env\nfi|' "$f" 2>/dev/null && \
      echo "[$(date '+%F %T')] cron_doctor patched $f" >> "$LOG"
  done
}

# ── main loop ─────────────────────────────────────────────
# B-035(e): test harness sources this script to unit-test stamp_state; the
# --source-only argument must keep the main loop from running in that mode.
if [ "${1:-}" = "--source-only" ]; then
  return 0 2>/dev/null || exit 0
fi
log "session_keeper started pid $$"
CYCLE=0
while true; do
  CYCLE=$((CYCLE+1))
  PROBES=""
  STATUS="OK"

  # 1. keep-awake guard (never let the Mac sleep)
  if ! awake_ok; then
    STATUS="HEALING"
    nohup /usr/bin/caffeinate -dimsu >/dev/null 2>&1 &
    log "ACTION caffeinate was missing — respawned"
  fi

  # 2. console session guard (logoff detector)
  if ! consolesess_ok; then
    STATUS="DEGRADED"
    log "ALERT console user session is NOT owned by $(id -u) (logoff?) — cannot self-heal, user must log in"
  fi

  # 3. headless claude auth (the crash class)
  HEADLESS_STAMP="failed"  # B-035(b): default failed; success branch flips to ok
  if headless_ok; then
    HEADLESS_STAMP="ok"
    PROBES="$PROBES headless=OK"
  else
    {
      echo "--- debug headless_ok raw output at $(date):"
      bash -c "source '$ENVF' 2>/dev/null; '$CLAUDE' --print 'reply AUTH-OK only' < /dev/null" 2>&1 | tail -3
      echo "--- ENVF head:"; head -c 120 "$ENVF" | sed "s/AUTH_TOKEN=.*/AUTH_TOKEN=<len $(grep -c . "$ENVF")>/"
      echo "--- PATH=$PATH HOME=$HOME"
    } >> "$LOG"
    STATUS="HEALING"
    log "ALERT headless claude auth FAILED — attempting env refresh from live process"
    if refresh_env_from_live_process; then
      log "FIX headless env refreshed from live process — auth verified"
    else
      log "ERROR no live process with valid auth found; keep retrying every cycle"
    fi
  fi

  # 4. Huanxin daemon transport
  if daemon_check; then
    PROBES="$PROBES daemons=OK"
    # 4a. congestion detection (FIX #2): busy-but-alive daemon = degraded output path
    if daemon_congested_check; then
      CONGESTED_CYCLES=$((CONGESTED_CYCLES + 1))
      if [ "$CONGESTED_CYCLES" -ge 3 ]; then
        STATUS="${STATUS}-CONGESTED"
        log "ALERT daemon congested (busy) ${CONGESTED_CYCLES} cycles — output non-round-trip; restarting via heartbeat"
        daemons_recover
        CONGESTED_CYCLES=0
      fi
    else
      CONGESTED_CYCLES=0
    fi
    # 4b. (FIX #2 note) empty-output path is covered by the congestion detector
    # above (busy-backlog -> 3-cycle fail-closed). No separate exec probe: it
    # would false-trigger on a slow-but-healthy daemon.
  else
    STATUS="${STATUS}-DAEMONS"
    log "ALERT daemons not ready (20653/19004)"
    daemons_recover
  fi
  CONGESTED_CYCLES="${CONGESTED_CYCLES:-0}"

  [ $((CYCLE % 30)) -eq 1 ] && cron_doctor
  DAEMONS_STAMP="healing"; daemon_check && DAEMONS_STAMP="ok"
  SK_HEARTBEAT="$HEARTBEAT" stamp_state "$STATUS" "$HEADLESS_STAMP" "$DAEMONS_STAMP" "$$"
  [ $((CYCLE % 30)) -eq 1 ] && log "HEARTBEAT cycle=$CYCLE status=$STATUS$PROBES"  # every ~1h keep log lean
  sleep 120
done

