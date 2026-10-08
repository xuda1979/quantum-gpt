#!/usr/bin/env bash
set -euo pipefail

TRAIN_DEV_URL="${HUANXIN_TRAIN_DEV_URL:-https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI}"
SAFARI_APP_ID="${HUANXIN_SAFARI_APP_ID:-com.apple.Safari}"
SAFARI_APP_PATH="${HUANXIN_SAFARI_APP_PATH:-/Applications/Safari.app}"
OSASCRIPT_TIMEOUT_SEC="${HUANXIN_KEEPALIVE_OSASCRIPT_TIMEOUT_SEC:-60}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANUAL_MODE_LOCK="$ROOT_DIR/.huanxin_manual_mode"
AUTOMATION_ENABLE_FILE="$ROOT_DIR/.huanxin_automation_enabled"
if [[ ! -f "$AUTOMATION_ENABLE_FILE" || -f "$MANUAL_MODE_LOCK" ]]; then
  echo "{\"ok\":false,\"error\":\"huanxin_automation_disabled\",\"lock_path\":\"$MANUAL_MODE_LOCK\",\"enable_path\":\"$AUTOMATION_ENABLE_FILE\"}"
  exit 125
fi
CALLBACK_FILE="${HUANXIN_LATEST_CALLBACK_FILE:-/tmp/huanxin-safari-latest-callback.json}"
REPAIR_SCRIPT="${HUANXIN_PROFILE_REPAIR_SCRIPT:-$ROOT_DIR/scripts/repair_huanxin_browser_profile.sh}"
REPAIR_LOG_FILE="${HUANXIN_PROFILE_REPAIR_LOG_FILE:-/tmp/huanxin-browser-profile-repair.log}"
REPAIR_LOCK_FILE="${HUANXIN_PROFILE_REPAIR_LOCK_FILE:-/tmp/huanxin-browser-profile-repair.lock}"
LAST_RELAYED_CALLBACK_FILE="${HUANXIN_LAST_RELAYED_CALLBACK_FILE:-/tmp/huanxin-browser-profile-last-callback.txt}"
BACKGROUND_PROFILE_REPAIR="${HUANXIN_BACKGROUND_PROFILE_REPAIR:-0}"
REPAIR_MIN_INTERVAL_SEC="${HUANXIN_PROFILE_REPAIR_MIN_INTERVAL_SEC:-45}"
REPAIR_LOCK_STALE_SEC="${HUANXIN_PROFILE_REPAIR_LOCK_STALE_SEC:-900}"
LAST_REPAIR_STARTED_FILE="${HUANXIN_PROFILE_REPAIR_LAST_STARTED_FILE:-/tmp/huanxin-browser-profile-repair.last_started}"
DAEMON_HEALTH_URL="${HUANXIN_DAEMON_HEALTH_URL:-http://127.0.0.1:19006/health}"
FORCE_REPAIR_ON_DAEMON_DRIFT="${HUANXIN_FORCE_REPAIR_ON_DAEMON_DRIFT:-0}"
REFRESH=0
ACTIVATE=0
TRAIN_DEV_URL_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$TRAIN_DEV_URL")"
SAFARI_APP_ID_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$SAFARI_APP_ID")"
SAFARI_APP_PATH_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$SAFARI_APP_PATH")"

safari_jxa_binding() {
  cat <<JXA
let safari = null;
for (const candidate of [$SAFARI_APP_ID_JSON, "Safari"]) {
  try {
    safari = Application(candidate);
    const _ = safari.name();
    break;
  } catch (error) {}
}
if (!safari) {
  throw new Error("Safari application could not be resolved via bundle id, path, or app name.");
}
JXA
}

huanxin_app_surface_helpers_jxa() {
  cat <<'JXA'
function normalizeHuanxinAppSurface(rawUrl) {
  const value = String(rawUrl || '');
  if (!value) {
    return '';
  }

  const hashIndex = value.indexOf('#');
  if (hashIndex === -1) {
    return value;
  }

  const beforeHash = value.slice(0, hashIndex);
  const hash = value.slice(hashIndex + 1);
  const queryIndex = hash.indexOf('?');
  const hashPath = queryIndex === -1 ? hash : hash.slice(0, queryIndex);
  const hashQuery = queryIndex === -1 ? '' : hash.slice(queryIndex + 1);
  const transientKeys = new Set(['state', 'session_state', 'code']);
  const stableParts = hashQuery
    .split('&')
    .filter(Boolean)
    .filter((part) => {
      const key = part.split('=', 1)[0] || '';
      return !transientKeys.has(key);
    })
    .sort();
  return stableParts.length
    ? `${beforeHash}#${hashPath}?${stableParts.join('&')}`
    : `${beforeHash}#${hashPath}`;
}

function isExpectedHuanxinAppSurface(candidateUrl, targetUrl) {
  const stableCandidate = normalizeHuanxinAppSurface(candidateUrl);
  const stableTarget = normalizeHuanxinAppSurface(targetUrl);
  return Boolean(stableCandidate) && stableCandidate === stableTarget;
}
JXA
}

print_error_json() {
  /usr/bin/python3 - "$1" "$2" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "ok": False,
            "error": sys.argv[1],
            "detail": sys.argv[2],
        },
        ensure_ascii=False,
    )
)
PY
}

record_callback_event() {
  local json_payload="$1"
  /usr/bin/python3 - "$CALLBACK_FILE" "$json_payload" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(sys.argv[2])
event = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "url": payload.get("callback_url") or payload.get("url"),
    "observed_url": payload.get("url"),
    "callback_url": payload.get("callback_url"),
    "auth_redirect_url": payload.get("auth_redirect_url"),
    "target_url": payload.get("target_url"),
    "window": payload.get("window"),
    "tab": payload.get("tab"),
    "title": payload.get("title"),
    "on_expected_surface": payload.get("on_expected_surface"),
}
path.write_text(json.dumps(event, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY
}

relay_callback_to_profile_if_needed() {
  local json_payload="$1"
  /usr/bin/python3 - "$json_payload" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
url = str(payload.get("callback_url") or payload.get("url") or "")
print("1" if ("session_state=" in url and "code=" in url) else "0")
PY
}

scan_for_train_dev_tab_json() {
  run_jxa "$(cat <<JXA
$(safari_jxa_binding)
$(huanxin_app_surface_helpers_jxa)
const target = $TRAIN_DEV_URL_JSON;
const wins = safari.windows();
let result = { found: false, target };
for (let w = 0; w < wins.length; w += 1) {
  const tabs = wins[w].tabs();
  for (let t = 0; t < tabs.length; t += 1) {
    const url = tabs[t].url();
    if (isExpectedHuanxinAppSurface(url, target)) {
      result = { found: true, window: w + 1, tab: t + 1, url, title: tabs[t].name() };
      break;
    }
  }
  if (result.found) {
    break;
  }
}
console.log(JSON.stringify(result));
JXA
)" 2>&1
}

open_train_dev_tab() {
  /usr/bin/osascript <<APPLESCRIPT
set targetUrl to ${TRAIN_DEV_URL_JSON}
try
  tell application id "${SAFARI_APP_ID}"
    activate
    open location targetUrl
  end tell
on error
  try
    tell application "Safari"
      activate
      open location targetUrl
    end tell
  end try
end try
APPLESCRIPT
  sleep 3
}

scan_and_validate_tab() {
  local json status
  json="$(scan_for_train_dev_tab_json 2>&1)"
  status=$?
  FOUND_JSON="$json"
  FOUND_STATUS=$status
  if [[ "$status" -ne 0 ]]; then
    print_error_json "apple_events_unavailable" "$json"
    return 2
  fi
  if [[ "$json" != *'"found":true'* ]]; then
    return 1
  fi
  return 0
}

maybe_trigger_profile_repair() {
  local json_payload="$1"
  local callback_url should_relay last_callback now_epoch last_started existing_pid trigger_reason
  should_relay="$(relay_callback_to_profile_if_needed "$json_payload")"
  trigger_reason="none"
  if [[ "$should_relay" == "1" ]]; then
    trigger_reason="callback"
  elif [[ "$FORCE_REPAIR_ON_DAEMON_DRIFT" == "1" ]]; then
    local daemon_needs_repair
    daemon_needs_repair="$(
      /usr/bin/python3 - "$DAEMON_HEALTH_URL" <<'PY'
import json
import subprocess
import sys
from urllib.parse import urlparse

health_url = sys.argv[1]
parsed = urlparse(health_url)
hostname = parsed.hostname or "127.0.0.1"
port = str(parsed.port or 19002)
path = parsed.path or "/health"

try:
    completed = subprocess.run(
        ["curl", "--max-time", "2", "-sS", f"http://{hostname}:{port}{path}"],
        text=True,
        capture_output=True,
        check=False,
    )
except Exception:
    print("0")
    raise SystemExit(0)

payload_raw = (completed.stdout or "").strip()
if completed.returncode != 0 or not payload_raw:
    print("0")
    raise SystemExit(0)

try:
    payload = json.loads(payload_raw)
except json.JSONDecodeError:
    print("0")
    raise SystemExit(0)

current_url = str(payload.get("currentUrl") or "").lower()
startup_state = str(payload.get("startupState") or "").lower()
ready = bool(payload.get("ready"))
auth_like = ("/auth/realms/" in current_url) or ("openid-connect/auth" in current_url)
needs_repair = auth_like or (not ready) or (startup_state in {"error", "booting"})
print("1" if needs_repair else "0")
PY
    )"
    if [[ "$daemon_needs_repair" == "1" ]]; then
      trigger_reason="daemon_drift"
    fi
  fi
  if [[ "$trigger_reason" == "none" ]]; then
    return 0
  fi
  if [[ "$trigger_reason" == "callback" ]]; then
    record_callback_event "$json_payload"
  fi
  if [[ "$BACKGROUND_PROFILE_REPAIR" != "1" ]]; then
    return 0
  fi
  if [[ "$trigger_reason" == "callback" ]]; then
    callback_url="$(
      /usr/bin/python3 - "$json_payload" <<'PY'
import json
import sys
payload = json.loads(sys.argv[1])
print(str(payload.get("callback_url") or payload.get("url") or ""))
PY
    )"
  else
    callback_url=""
  fi

  if [[ -n "$callback_url" && -f "$LAST_RELAYED_CALLBACK_FILE" ]]; then
    last_callback="$(cat "$LAST_RELAYED_CALLBACK_FILE" 2>/dev/null || true)"
    if [[ "$last_callback" == "$callback_url" ]]; then
      return 0
    fi
  fi

  now_epoch="$(date +%s)"

  if [[ -f "$REPAIR_LOCK_FILE" ]]; then
    existing_pid="$(cat "$REPAIR_LOCK_FILE" 2>/dev/null || true)"
    if [[ -n "${existing_pid:-}" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      return 0
    fi
    if [[ -n "${existing_pid:-}" ]]; then
      rm -f "$REPAIR_LOCK_FILE"
    fi
  fi

  if [[ -f "$LAST_REPAIR_STARTED_FILE" ]]; then
    last_started="$(cat "$LAST_REPAIR_STARTED_FILE" 2>/dev/null || true)"
    if [[ "$last_started" =~ ^[0-9]+$ ]] && (( now_epoch - last_started < REPAIR_MIN_INTERVAL_SEC )); then
      return 0
    fi
  fi

  if [[ -f "$REPAIR_LOCK_FILE" ]]; then
    existing_pid="$(cat "$REPAIR_LOCK_FILE" 2>/dev/null || true)"
    if [[ -n "${existing_pid:-}" ]]; then
      local started_at
      started_at="$(stat -f '%m' "$REPAIR_LOCK_FILE" 2>/dev/null || echo 0)"
      if [[ "$started_at" =~ ^[0-9]+$ ]] && (( now_epoch - started_at > REPAIR_LOCK_STALE_SEC )); then
        rm -f "$REPAIR_LOCK_FILE"
      fi
    fi
  fi

  printf '%s\n' "$now_epoch" > "$LAST_REPAIR_STARTED_FILE"
  nohup bash -lc '
set -euo pipefail
repair_script="$1"
repair_log_file="$2"
repair_lock_file="$3"
repair_trigger_reason="$4"
printf "%s" "$$" > "$repair_lock_file"
trap '"'"'rm -f "$repair_lock_file"'"'"' EXIT
echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"event\":\"repair_start\",\"trigger\":\"${repair_trigger_reason}\"}" >> "$repair_log_file"
bash "$repair_script" >> "$repair_log_file" 2>&1
' _ "$REPAIR_SCRIPT" "$REPAIR_LOG_FILE" "$REPAIR_LOCK_FILE" "$trigger_reason" >/dev/null 2>&1 &
  disown "$!" 2>/dev/null || true
  if [[ -n "$callback_url" ]]; then
    printf '%s\n' "$callback_url" > "$LAST_RELAYED_CALLBACK_FILE"
  fi
}

run_jxa() {
  /usr/bin/python3 - "$OSASCRIPT_TIMEOUT_SEC" "$1" <<'PY'
import subprocess
import sys

timeout_sec = int(sys.argv[1])
script = sys.argv[2]

try:
    completed = subprocess.run(
        ["osascript", "-l", "JavaScript"],
        input=script,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
except subprocess.TimeoutExpired as exc:
    if exc.stdout:
        sys.stdout.write(exc.stdout)
    if exc.stderr:
        sys.stderr.write(exc.stderr)
    sys.stderr.write(f"osascript timed out after {timeout_sec}s\n")
    raise SystemExit(124)

if completed.stdout:
    sys.stdout.write(completed.stdout)
if completed.stderr:
    sys.stderr.write(completed.stderr)
raise SystemExit(completed.returncode)
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --refresh)
      REFRESH=1
      shift
      ;;
    --activate)
      ACTIVATE=1
      shift
      ;;
    *)
      echo "Usage: $0 [--refresh] [--activate]" >&2
      exit 1
      ;;
  esac
done

set +e
scan_and_validate_tab
SCAN_RESULT=$?
if [[ "$SCAN_RESULT" -eq 2 ]]; then
  exit 3
fi
if [[ "$SCAN_RESULT" -eq 1 ]]; then
  open_train_dev_tab
  scan_and_validate_tab
  SCAN_RESULT=$?
  if [[ "$SCAN_RESULT" -ne 0 ]]; then
    printf '%s\n' "$FOUND_JSON"
    exit 2
  fi
fi
set -e

if [[ "$REFRESH" -eq 1 || "$ACTIVATE" -eq 1 ]]; then
  set +e
  REFRESHED_JSON="$(
  run_jxa "$(cat <<JXA
const safari = Application($SAFARI_APP_ID_JSON);
$(huanxin_app_surface_helpers_jxa)
const target = $TRAIN_DEV_URL_JSON;
const found = $FOUND_JSON;
const win = safari.windows()[found.window - 1];
const tab = win.tabs()[found.tab - 1];
win.currentTab = tab;
if (${ACTIVATE}) safari.activate();
let refreshed = false;
const currentUrl = String(found.url || '');
const onExpectedSurface = isExpectedHuanxinAppSurface(currentUrl, target);
const refreshUrl =
  currentUrl &&
  onExpectedSurface &&
  !currentUrl.includes('/auth/realms/') &&
  !currentUrl.includes('openid-connect/auth')
    ? currentUrl
    : target;
if (${REFRESH}) {
  tab.url = refreshUrl;
  refreshed = true;
  delay(0.5);
}
const samples = [];
let callbackUrl = null;
let authRedirectUrl = null;
for (let i = 0; i < 16; i++) {
  const sampleUrl = String(tab.url() || '');
  const sampleTitle = String(tab.name() || '');
  samples.push({ t: i * 0.5, url: sampleUrl, title: sampleTitle });
  if (!callbackUrl && sampleUrl.includes('session_state=') && sampleUrl.includes('code=')) {
    callbackUrl = sampleUrl;
  }
  if (!authRedirectUrl && sampleUrl.includes('/auth/realms/') && sampleUrl.includes('openid-connect/auth')) {
    authRedirectUrl = sampleUrl;
  }
  delay(0.5);
}
const finalUrl = String(tab.url() || '');
console.log(JSON.stringify({
  found: true,
  refreshed,
  activated: ${ACTIVATE} ? true : false,
  window: found.window,
  tab: found.tab,
  url: finalUrl,
  callback_url: callbackUrl,
  auth_redirect_url: authRedirectUrl,
  title: tab.name(),
  target_url: refreshUrl,
  refresh_url: refreshUrl,
  on_expected_surface: isExpectedHuanxinAppSurface(finalUrl, target),
  redirect_samples: samples
}));
JXA
  )" 2>&1
  )"
  REFRESH_STATUS=$?
  set -e
  if [[ "$REFRESH_STATUS" -ne 0 ]]; then
    print_error_json "refresh_failed" "$REFRESHED_JSON"
    exit 4
  fi
  case "$REFRESHED_JSON" in
    *'"on_expected_surface":true'*)
      maybe_trigger_profile_repair "$REFRESHED_JSON"
      ;;
    *)
      set +e
      DETAIL_JSON="$(
      /usr/bin/python3 - "$REFRESHED_JSON" <<'PY'
import json
import sys
payload = json.loads(sys.argv[1])
print(json.dumps(payload, ensure_ascii=False))
PY
      )"
      set -e
      maybe_trigger_profile_repair "$DETAIL_JSON"
      print_error_json "unexpected_post_refresh_url" "$REFRESHED_JSON"
      exit 5
      ;;
  esac
  printf '%s\n' "$REFRESHED_JSON"
  exit 0
fi

set +e
RESULT_JSON="$(
run_jxa "$(cat <<JXA
const found = $FOUND_JSON;
found.refreshed = false;
found.target_url = found.url || $TRAIN_DEV_URL_JSON;
console.log(JSON.stringify(found));
JXA
)" 2>&1
)"
RESULT_STATUS=$?
set -e

if [[ "$RESULT_STATUS" -ne 0 ]]; then
  print_error_json "apple_events_unavailable" "$RESULT_JSON"
  exit 3
fi

printf '%s\n' "$RESULT_JSON"
