#!/usr/bin/env bash
# HUANXIN HEARTBEAT (2026-09-03, user directive: "access and connection alive
# forever" + "make the huanxin script very robust"). One loop, full self-heal:
#   1. auth-broker 19090 down            -> launchd kickstart
#   2. daemon auth-failed (login_required) -> plaintext cookie bridge from the
#      logged-in user Chrome (proven 2026-09-03) + daemon restart
#   3. daemon error/down                 -> cookie bridge + restart
#   4. daemon booting >15m (wedge)       -> cookie bridge + restart
#   5. judge-health watcher dead         -> respawn
# Portable bash 3.2 (NO associative arrays — B-029/B-035 class). Never wipes
# profiles, never opens tabs. State JSON for the standup every 2 min.
set -u
LOG="/Users/daxu/software/quantum-gpt-new/logs/huanxin_heartbeat.log"
STATE="/tmp/huanxin_heartbeat_state.json"
QG="/Users/daxu/software/quantum-gpt"
ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }
port_for() { case "$1" in ASI1) echo 20646;; ASI2) echo 19004;; ASI3) echo 20653;; esac; }
cdp_for() { case "$1" in ASI1) echo 9224;; ASI2) echo 9225;; ASI3) echo 9226;; esac; }
# Per-env `开发环境` detail URL, resolved from the single source of truth
# (scripts/huanxin_env_config.py -> .huanxin_envs.json). WITHOUT this the daemon
# falls back to the hard-coded DEFAULT_TRAIN_DEV_URL in huanxin_shell_exec.js,
# which points at the *AI* environment — so every daemon booted on the wrong
# env's page (redirect_uri ...?name=AI) and then had to hunt for its own row in
# the env list. Setting it lands each daemon directly on its own env.
train_dev_url_for() {
  /usr/bin/python3 "$QG/scripts/huanxin_env_config.py" --env "$1" --field train_dev_url 2>/dev/null
}
# B-047 (2026-09-11): boot-start timestamps used to live in IN-MEMORY BOOT_ASI*
# variables, so every restart of this process reset them to 0. That is half of a
# MUTUAL LIVELOCK with the keeper: session_keeper.sh:158 kickstarts this script
# with `launchctl kickstart -k` whenever the daemons are not ready -> the kick
# resets the boot timers -> the 900s wedge branch below becomes unreachable ->
# the stuck daemons are never restarted and never converge -> the keeper kicks
# again. Observed live: ASI1/2/3 all booting 17:41:37Z -> 18:00Z+ with heartbeat
# restarts every 2-7 min, i.e. always faster than the 900s timeout.
# The timestamps now persist to disk and survive a process restart.
BOOTSTATE="${SAPO_HEARTBEAT_BOOTSTATE:-/tmp/huanxin_boot_timers.txt}"
PLATFORM_ERR_COOLDOWN_S="${SAPO_HEARTBEAT_PLATFORM_ERR_COOLDOWN_S:-1800}"
boot_get() {  # $1 = env name -> epoch seconds, empty when absent
  [ -f "$BOOTSTATE" ] || return 0
  awk -v k="$1" '$1==k {v=$2} END {if (v!="") print v}' "$BOOTSTATE" 2>/dev/null
}
boot_set() {  # $1 = env name, $2 = epoch seconds (0 clears)
  _tmp="$BOOTSTATE.$$"
  if [ -f "$BOOTSTATE" ]; then
    awk -v k="$1" '$1!=k' "$BOOTSTATE" > "$_tmp" 2>/dev/null
  fi
  echo "$1 $2" >> "$_tmp"
  mv "$_tmp" "$BOOTSTATE" 2>/dev/null
}
bootval_for() {  # numeric epoch, or 0 when absent/corrupt (fail closed to first-seen)
  _v="$(boot_get "$1")"
  case "$_v" in ''|*[!0-9]*) echo 0 ;; *) echo "$_v" ;; esac
}

# B-051 (2026-09-11, section 5.4.1 three-state probe): ONLY a positive DEAD
# signal may restart a daemon. The old dispatch was two-state -- anything that
# was not `ready`/`booting` fell through to `*) needs_restart=1` -- and a DEAD
# PIPELINE (python3 fork starved -> curl|python3 prints nothing) was therefore
# indistinguishable from a refused connection. Live consequence: the watchdog
# killed daemons that were merely booting, over and over, so none of the three
# environments could ever converge (the ~105m dark state). UNKNOWN is now its
# own state and it is INERT: it logs and never fires.
ACTION=""
action_for_state() {  # $1 = "state authfail [pterm]", $2 = pterm flag (optional)
  local _st="${1:-unknown}"
  local _pterm="${2:-0}"
  case "$_st" in
    ready)   ACTION=clear ;;
    booting) ACTION=timer ;;
    unknown) ACTION=inert ;;
    down)    ACTION=restart ;;
    error)
      if [ "$_pterm" = "1" ]; then
        ACTION=platform_hold
      else
        ACTION=restart
      fi ;;
    *)       ACTION=inert ;;
  esac
}

# B-055 (2026-09-11): the daemon launch below MUST go through
# scripts/sapo_detach_exec.sh. `nohup ... &` does NOT change the process
# group and macOS has no portable `setsid`, so the daemons inherited THIS
# script`s launchd-job process group. session_keeper.sh fires a launchctl
# kickstart -k on this heartbeat job whenever ANY ONE daemon is not ready --
# including a daemon merely mid-booting, which is a NORMAL boot state.
# That kickstart tears down the job`s whole process group, so the keeper`s
# remedy killed all three daemons, including siblings already ready; they
# rebooted, the keeper kicked again mid-boot, and the three resources could
# never converge. Measured 2026-09-10 17:41Z -> 18:2xZ: 6 heartbeat
# restarts in 36 min, each with a keeper kick in the same minute, all three
# daemons dark throughout. os.setsid() in a pre-exec (what the helper does)
# makes each daemon a session leader, immune to that teardown.
daemon_is_midboot() {
  local env="$1"
  local st st0
  st="$(daemon_state "$env" 2>/dev/null || echo unknown)"
  st0="${st%% *}"
  # booting, down (listener not bound yet), and error (state flips during boot)
  # are all valid mid-boot states when a fresh boot timer exists (B-183).
  case "$st0" in
    booting|down|error) ;;
    *) return 1 ;;
  esac
  local boot_epoch boot_age
  boot_epoch="$(boot_get "$env")"
  [ -n "$boot_epoch" ] && [ "$boot_epoch" -gt 0 ] 2>/dev/null || return 1
  boot_age=$(( $(date +%s) - boot_epoch ))
  if [ "$boot_age" -lt 300 ] 2>/dev/null; then
    return 0
  fi
  return 1
}

seed_and_restart() {
  E="$1"
  log "$E: cookie bridge + restart"
  pid=$(pgrep -f "huanxin_browser_daemon.js --env $E" | head -1)
  if [ -n "$pid" ] && daemon_is_midboot "$E"; then
    log "$E: daemon is mid-boot (booting, <300s) -- skipping kill"
  elif [ -n "$pid" ]; then
    kill "$pid" 2>/dev/null
  fi
  sleep 4
  /usr/bin/python3 "$QG/scripts/sapo_cookie_seed.py" >> "$LOG" 2>&1 || log "$E: cookie seed FAILED (user Chrome login needed?)"
  NODE_BIN="$(command -v node || ls /Users/daxu/.local/share/fnm/node-versions/*/installation/bin/node 2>/dev/null | tail -1)"
  CDP="$(cdp_for "$E")"
  ( cd "$QG" && HUANXIN_PROFILE_COPY_NAME="quantum-rnd-$E" HUANXIN_CDP_PORT="$CDP" \
    HUANXIN_TRAIN_DEV_URL="$(train_dev_url_for "$E")" \
    HUANXIN_HOST_RESOLVER_RULES='MAP aihuanxin.cn 36.212.177.181' HUANXIN_FORGE_KC_CALLBACK=1 \
    HUANXIN_CAPTURE_SCRIPT="$QG/scripts/huanxin_capture_chrome_fixed1.sh" \
    PATH="$(dirname "$NODE_BIN"):$PATH" nohup bash "$QG/scripts/sapo_detach_exec.sh" \
    "$NODE_BIN" browser-automation/huanxin_browser_daemon.js \
    --env "$E" >> /Users/daxu/software/quantum-gpt-new/logs/huanxin_all_keepalive.log 2>&1 & )
  log "$E: relaunched"
}

daemon_state() {
  _body=$(curl -4 -s -m 8 "http://127.0.0.1:$1/health" 2>/dev/null)
  _rc=$?
  if [ -z "$_body" ]; then
    if [ "$_rc" -eq 7 ]; then
      echo "down 0"
    else
      echo "unknown 0"
    fi
    return 0
  fi
  printf "%s" "$_body" | /usr/bin/python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    err = str(d.get('startupError') or '')
    st = 'ready' if d.get('ready') else ('error' if d.get('startupState')=='error' else 'booting')
    af = 1 if ('login_required' in err or 'auth expired' in err) else 0
    pterm = 1 if ('shell endpoint' in err and 'no terminal' in err) else 0
    print(st, af, pterm)
except Exception:
    print('unknown', 0)"
}

# Test hook: expose the helper DEFINITIONS without entering the polling loop.
# B-074 (2026-09-11): this guard used to sit above seed_and_restart/
# daemon_state and returned before either was defined, so a test could not
# exercise the SHIPPED probe -- only action_for_state. The B-074 RED test
# stubs curl and calls daemon_state directly to prove the three-state fix,
# so the guard now sits below every helper and above the lock/loop.
if [ "${SAPO_HEARTBEAT_SOURCE_ONLY:-0}" = "1" ]; then
  return 0 2>/dev/null || exit 0
fi

# SINGLE-INSTANCE GUARD (2026-09-08: 3 orphan duplicates formed; triple-polls the
# serialized transport). If another live instance holds the lock, this one exits.
LOCK_SCRIPT="$QG/scripts/sapo_single_instance_lock.sh"
if [ -f "$LOCK_SCRIPT" ]; then
  if ! bash "$LOCK_SCRIPT" acquire sapo_heartbeat --holder-pid "$$" --steal-stale; then
    log "another heartbeat instance holds the lock -> exiting"
    exit 0
  fi
fi
log "heartbeat start"
while true; do
  if ! curl -4 -s -m 5 http://127.0.0.1:19090/health 2>/dev/null | grep -q '"ok":true'; then
    log "broker down -> launchd kickstart"
    launchctl kickstart -k "gui/$(id -u)/com.quantumgpt.huanxin-auth-broker" 2>/dev/null || true
  fi
  report="{"
  first=1
  for E in ASI1 ASI2 ASI3; do
    port="$(port_for "$E")"
    # B-049 (2026-09-11): `set -- $(empty)` CLEARS the positional parameters, so a
    # bare `st="$1"` here aborts the WHOLE heartbeat under `set -u`. Empty output is
    # what a fork-starved pipeline yields -- "fork: Resource temporarily unavailable"
    # in this script's own stderr left curl|python3 printing nothing, and the next
    # line died with "line 73: $1: unbound variable" (43 times in the last 400 stderr
    # lines, against 58 fork-EAGAIN). Fail CLOSED, and per B-051 fail to UNKNOWN --
    # not to `down`, which would restart a daemon that is only booting.
    ds="$(daemon_state "$port")"
    set -- ${ds:-unknown 0}
    st="${1:-unknown}"; authfail="${2:-0}"; pterm="${3:-0}"
    bootval="$(bootval_for "$E")"
    needs_restart=0
    action_for_state "$st" "$pterm"
    # action_for_state sets the GLOBAL $ACTION (declared at the top of this file).
    # This read was lowercase "$action", which never exists — so under `set -u`
    # the heartbeat aborted on EVERY tick ("line 173: action: unbound variable")
    # before it could restart a single daemon. That is a crash-on-tick, not a
    # heal-on-tick: all three envs went dark and stayed dark, and the log shows
    # only "heartbeat start" repeats with no "relaunched" line between them.
    case "$ACTION" in
      clear) boot_set "$E" 0 ;;
      timer)
        if [ "$bootval" -eq 0 ]; then
          boot_set "$E" "$(date +%s)"
          bootval="$(bootval_for "$E")"
        fi
        if [ $(( $(date +%s) - bootval )) -gt 900 ]; then
          log "$E: booting >15m -> wedged"; needs_restart=1
        fi ;;
      restart) needs_restart=1 ;;
      platform_hold)
        _pboot="$(bootval_for "$E")"
        if [ "$_pboot" -gt 0 ] && [ $(( $(date +%s) - _pboot )) -gt "$PLATFORM_ERR_COOLDOWN_S" ] 2>/dev/null; then
          log "$E: platform_hold cooldown expired (${PLATFORM_ERR_COOLDOWN_S}s) -> restart"
          needs_restart=1
        else
          log "$E: platform_hold (shell endpoint failure, cooldown ${PLATFORM_ERR_COOLDOWN_S}s)"
        fi ;;
      inert) log "$E: probe UNKNOWN (fork/transport) - no action taken" ;;
    esac
    [ "$authfail" = "1" ] && needs_restart=1
    if [ "$needs_restart" = "1" ]; then
      seed_and_restart "$E"
      boot_set "$E" 0
      st="restarting"
    fi
    sep=""; [ $first -eq 0 ] && sep=", "
    report="$report$sep\"$E\":\"$st\""
    first=0
  done
  report="$report}"
  if ! pgrep -f sapo_judge_health_agent >/dev/null; then
    log "judge-health dead -> respawn"
    ( source /Users/daxu/.codex/secrets/huanxin.env 2>/dev/null; nohup python3 "$QG/scripts/sapo_judge_health_agent.py" >> /tmp/sapo_judge_health_agent.out 2>&1 & )
  fi
  # POLICE LAYER (user directive 2026-09-03): scope + context hygiene + meta-liveness
  WW=$(/usr/bin/python3 "$QG/scripts/sapo_watchdog_watcher.py" 2>&1 | tail -3 | head -2 | tr '\n' ' ')
  case "$WW" in
    *"GREEN"*) : ;;
    *) log "POLICE meta-liveness: $WW" ;;
  esac
  HYGIENE=$(/usr/bin/python3 "$QG/scripts/sapo_context_hygiene.py" 2>&1 | tail -1)
  case "$HYGIENE" in
    *"CLEAN"*) : ;;
    *) log "POLICE: $HYGIENE" ;;
  esac
  echo "{\"ts\":\"$(ts)\",\"daemons\":$report,\"hygiene\":\"$HYGIENE\"}" > "$STATE"
  log "tick daemons=$report hygiene=$HYGIENE"
  sleep 120
done
