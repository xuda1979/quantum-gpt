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
BOOT_ASI1=0; BOOT_ASI2=0; BOOT_ASI3=0
boot_var_for() { echo "BOOT_$1"; }

seed_and_restart() {
  E="$1"
  log "$E: cookie bridge + restart"
  pid=$(pgrep -f "huanxin_browser_daemon.js --env $E" | head -1)
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
  sleep 4
  /usr/bin/python3 "$QG/scripts/sapo_cookie_seed.py" >> "$LOG" 2>&1 || log "$E: cookie seed FAILED (user Chrome login needed?)"
  NODE_BIN="$(command -v node || ls /Users/daxu/.local/share/fnm/node-versions/*/installation/bin/node 2>/dev/null | tail -1)"
  CDP="$(cdp_for "$E")"
  ( cd "$QG" && HUANXIN_PROFILE_COPY_NAME="quantum-rnd-$E" HUANXIN_CDP_PORT="$CDP" \
    HUANXIN_TRAIN_DEV_URL="$(train_dev_url_for "$E")" \
    HUANXIN_HOST_RESOLVER_RULES='MAP aihuanxin.cn 36.212.177.181' HUANXIN_FORGE_KC_CALLBACK=1 \
    HUANXIN_CAPTURE_SCRIPT="$QG/scripts/huanxin_capture_chrome_fixed1.sh" \
    PATH="$(dirname "$NODE_BIN"):$PATH" nohup "$NODE_BIN" browser-automation/huanxin_browser_daemon.js \
    --env "$E" >> /Users/daxu/software/quantum-gpt-new/logs/huanxin_all_keepalive.log 2>&1 & )
  log "$E: relaunched"
}

daemon_state() {
  curl -4 -s -m 8 "http://127.0.0.1:$1/health" 2>/dev/null | /usr/bin/python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    err = str(d.get('startupError') or '')
    st = 'ready' if d.get('ready') else ('error' if d.get('startupState')=='error' else 'booting')
    af = 1 if ('login_required' in err or 'auth expired' in err) else 0
    print(st, af)
except Exception:
    print('down', 0)"
}

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
    set -- $(daemon_state "$port")
    st="$1"; authfail="${2:-0}"
    bootvar="$(boot_var_for "$E")"
    bootval="$(eval "echo \${$bootvar:-0}")"
    needs_restart=0
    case "$st" in
      ready) eval "$bootvar=0" ;;
      booting)
        if [ "$bootval" -eq 0 ]; then
          eval "$bootvar=$(date +%s)"
          bootval="$(eval "echo \${$bootvar:-0}")"
        fi
        if [ $(( $(date +%s) - bootval )) -gt 900 ]; then
          log "$E: booting >15m -> wedged"; needs_restart=1
        fi ;;
      *) needs_restart=1 ;;
    esac
    [ "$authfail" = "1" ] && needs_restart=1
    if [ "$needs_restart" = "1" ]; then
      seed_and_restart "$E"
      eval "$bootvar=0"
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
