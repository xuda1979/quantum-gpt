#!/usr/bin/env bash
set -euo pipefail

DEFAULT_TRAIN_DEV_URL="https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev"
URL_TO_VISIT="$DEFAULT_TRAIN_DEV_URL"
SAFARI_APP_ID="${HUANXIN_SAFARI_APP_ID:-com.apple.Safari}"
SAFARI_APP_PATH="${HUANXIN_SAFARI_APP_PATH:-/Applications/Safari.app}"
OSASCRIPT_TIMEOUT_SEC="${HUANXIN_KEEPALIVE_OSASCRIPT_TIMEOUT_SEC:-20}"
TRAIN_DEV_PREFIX="${DEFAULT_TRAIN_DEV_URL%%#*}"
URL_TO_VISIT_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$URL_TO_VISIT")"
TRAIN_DEV_PREFIX_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$TRAIN_DEV_PREFIX")"
SAFARI_APP_ID_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$SAFARI_APP_ID")"
SAFARI_APP_PATH_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$SAFARI_APP_PATH")"

usage() {
  echo "Usage: $0 [--url <auth-or-train-dev-url>]" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      URL_TO_VISIT="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

URL_TO_VISIT_JSON="$(/usr/bin/python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$URL_TO_VISIT")"

run_jxa() {
  /usr/bin/python3 - "$OSASCRIPT_TIMEOUT_SEC" "$1" <<'PY'
import subprocess
import sys

timeout_sec = int(sys.argv[1])
script = sys.argv[2]
completed = subprocess.run(
    ["osascript", "-l", "JavaScript"],
    input=script,
    text=True,
    capture_output=True,
    timeout=timeout_sec,
    check=False,
)
if completed.stdout:
    sys.stdout.write(completed.stdout)
if completed.stderr:
    sys.stderr.write(completed.stderr)
raise SystemExit(completed.returncode)
PY
}

safari_jxa_binding() {
  cat <<JXA
let safari = null;
for (const candidate of [$SAFARI_APP_ID_JSON, $SAFARI_APP_PATH_JSON, "Safari"]) {
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

FOUND_JSON="$(
run_jxa "$(cat <<JXA
$(
safari_jxa_binding
)
const prefix = $TRAIN_DEV_PREFIX_JSON;
const wins = safari.windows();
let result = { found: false, prefix };
for (let w = 0; w < wins.length; w++) {
  const tabs = wins[w].tabs();
  for (let t = 0; t < tabs.length; t++) {
    const url = String(tabs[t].url() || '');
    if (url.startsWith(prefix)) {
      result = { found: true, window: w + 1, tab: t + 1, url, title: tabs[t].name() };
      break;
    }
  }
  if (result.found) break;
}
console.log(JSON.stringify(result));
JXA
)" 2>&1
)"

case "$FOUND_JSON" in
  *'"found":true'*)
    ;;
  *)
    printf '%s\n' "$FOUND_JSON"
    exit 2
    ;;
esac

run_jxa "$(cat <<JXA
$(safari_jxa_binding)
const found = $FOUND_JSON;
const visitUrl = $URL_TO_VISIT_JSON;
const win = safari.windows()[found.window - 1];
const tab = win.tabs()[found.tab - 1];
win.currentTab = tab;
tab.url = visitUrl;
delay(0.5);
const samples = [];
let callbackUrl = null;
let authRedirectUrl = null;
for (let i = 0; i < 20; i++) {
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
console.log(JSON.stringify({
  found: true,
  window: found.window,
  tab: found.tab,
  visit_url: visitUrl,
  final_url: String(tab.url() || ''),
  title: String(tab.name() || ''),
  callback_url: callbackUrl,
  auth_redirect_url: authRedirectUrl,
  redirect_samples: samples,
}));
JXA
)" 2>&1
