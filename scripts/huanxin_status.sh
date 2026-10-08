#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_NAME="${1:-${HUANXIN_ENV_NAME:-AI}}"
ENV_CONFIG="$("$ROOT_DIR/.venv/bin/python" scripts/huanxin_env_config.py --env "$ENV_NAME" --format shell 2>/dev/null || /usr/bin/python3 scripts/huanxin_env_config.py --env "$ENV_NAME" --format shell)"
eval "$ENV_CONFIG"
DEFAULT_DAEMON_PORT="$HUANXIN_ENV_DAEMON_PORT"
TRAIN_DEV_URL="${HUANXIN_TRAIN_DEV_URL:-$HUANXIN_ENV_TRAIN_DEV_URL}"
MANUAL_MODE_LOCK="$ROOT_DIR/.huanxin_manual_mode"
AUTOMATION_ENABLE_FILE="$ROOT_DIR/.huanxin_automation_enabled"
KEEPALIVE_LABEL="com.quantumgpt.huanxin-safari-keepalive"
KEEPALIVE_LOG="/tmp/huanxin-safari-keepalive.launchd.log"
DAEMON_AGENT_LABEL="com.quantumgpt.huanxin-ai2-daemon"
DAEMON_HEALTH_URL="${HUANXIN_DAEMON_HEALTH_URL:-http://127.0.0.1:${DEFAULT_DAEMON_PORT}/health}"
DAEMON_LOG="${HUANXIN_DAEMON_LOG:-/tmp/huanxin-daemon-${ENV_NAME}.log}"
REPAIR_LOG="/tmp/huanxin-browser-profile-repair.log"
REPAIR_RESULT_PATH="${HUANXIN_PROFILE_REPAIR_RESULT_PATH:-/tmp/huanxin-browser-profile-repair.json}"
REPAIR_STATE_PATH="${HUANXIN_PROFILE_REPAIR_STATE_PATH:-/tmp/huanxin-browser-profile-repair-state.json}"
CALLBACK_FILE="${HUANXIN_LATEST_CALLBACK_FILE:-/tmp/huanxin-safari-latest-callback.json}"
PROBE_TIMEOUT_SEC="${HUANXIN_STATUS_PROBE_TIMEOUT_SEC:-45}"
META_DIR="$ROOT_DIR/.huanxin_jobs"

set +e
KEEPALIVE_STATUS="$(bash scripts/install_huanxin_safari_keepalive_agent.sh --status 2>&1)"
KEEPALIVE_STATUS_CODE=$?
DAEMON_AGENT_STATUS="$(bash scripts/install_huanxin_ai2_daemon_agent.sh --status 2>&1)"
DAEMON_AGENT_STATUS_CODE=$?
DAEMON_HEALTH="$(curl -sS --max-time 3 "$DAEMON_HEALTH_URL" 2>/dev/null)"
DAEMON_HEALTH_CODE=$?
if [[ ! -f "$AUTOMATION_ENABLE_FILE" || -f "$MANUAL_MODE_LOCK" ]]; then
  PROBE_JSON="$(
    /usr/bin/python3 - "$MANUAL_MODE_LOCK" "$AUTOMATION_ENABLE_FILE" <<'PY'
import json
import sys

print(
    json.dumps(
        {
            "state": "automation_disabled",
            "error": "huanxin_probe_skipped",
            "manual_lock_present": __import__("pathlib").Path(sys.argv[1]).exists(),
            "automation_enable_present": __import__("pathlib").Path(sys.argv[2]).exists(),
            "lock_path": sys.argv[1],
            "enable_path": sys.argv[2],
        },
        ensure_ascii=False,
    )
)
PY
  )"
  PROBE_STATUS_CODE=125
else
  PROBE_JSON="$(
  /usr/bin/python3 - "$ROOT_DIR" "$PROBE_TIMEOUT_SEC" <<'PY'
import json
import subprocess
import sys

root_dir = sys.argv[1]
timeout_sec = int(sys.argv[2])
try:
    completed = subprocess.run(
        ["node", "browser-automation/huanxin_probe.js"],
        cwd=root_dir,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
except subprocess.TimeoutExpired:
    print(
        json.dumps(
            {
                "state": "probe_timeout",
                "error": "huanxin_probe_timed_out",
                "timeout_seconds": timeout_sec,
            },
            ensure_ascii=False,
        )
    )
    raise SystemExit(124)

payload = completed.stdout.strip() or completed.stderr.strip()
if payload:
    print(payload)
raise SystemExit(completed.returncode)
PY
  )"
  PROBE_STATUS_CODE=$?
fi
set -e

if [[ -f "$KEEPALIVE_LOG" ]]; then
  KEEPALIVE_LOG_TAIL="$(tail -n 5 "$KEEPALIVE_LOG")"
else
  KEEPALIVE_LOG_TAIL=""
fi

if [[ -f "$DAEMON_LOG" ]]; then
  DAEMON_LOG_TAIL="$(tail -n 20 "$DAEMON_LOG")"
else
  DAEMON_LOG_TAIL=""
fi

if [[ -f "$REPAIR_LOG" ]]; then
  REPAIR_LOG_TAIL="$(tail -n 20 "$REPAIR_LOG")"
else
  REPAIR_LOG_TAIL=""
fi

if [[ -f "$REPAIR_STATE_PATH" ]]; then
  REPAIR_STATE_JSON="$(cat "$REPAIR_STATE_PATH")"
  REPAIR_STATE_MTIME="$(stat -f '%m' "$REPAIR_STATE_PATH" 2>/dev/null || true)"
else
  REPAIR_STATE_JSON=""
  REPAIR_STATE_MTIME=""
fi

if [[ -f "$REPAIR_RESULT_PATH" ]]; then
  REPAIR_RESULT_JSON="$(cat "$REPAIR_RESULT_PATH")"
  REPAIR_RESULT_MTIME="$(stat -f '%m' "$REPAIR_RESULT_PATH" 2>/dev/null || true)"
else
  REPAIR_RESULT_JSON=""
  REPAIR_RESULT_MTIME=""
fi

if [[ -f "$CALLBACK_FILE" ]]; then
  CALLBACK_JSON="$(cat "$CALLBACK_FILE")"
else
  CALLBACK_JSON=""
fi

JOB_SUMMARY_JSON="$(
/usr/bin/python3 - "$META_DIR" <<'PY'
import glob
import json
import os
import sys

meta_dir = sys.argv[1]
items = []
for path in sorted(glob.glob(os.path.join(meta_dir, "*.json"))):
    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        continue
    payload["_meta_path"] = path
    items.append(payload)

items.sort(key=lambda item: str(item.get("created_at") or item.get("job_id") or ""))
recent = items[-5:]
fastiter = [
    item for item in items
    if "fast" in str(item.get("name") or "") or "fastiter" in str(item.get("command") or "")
]
summary = {
    "meta_dir": meta_dir,
    "job_count": len(items),
    "recent_job_ids": [str(item.get("job_id")) for item in recent],
    "latest_job": recent[-1] if recent else None,
    "latest_fast_iteration_job": fastiter[-1] if fastiter else None,
}
print(json.dumps(summary, ensure_ascii=False))
PY
)"

COMMAND_CONNECTION_PATH="$ROOT_DIR/.huanxin_shell_connections/${ENV_NAME}.json"
if [[ -f "$COMMAND_CONNECTION_PATH" ]]; then
  COMMAND_CONNECTION_JSON="$(cat "$COMMAND_CONNECTION_PATH")"
else
  COMMAND_CONNECTION_JSON=""
fi

/usr/bin/python3 - "$ENV_NAME" "$TRAIN_DEV_URL" "$KEEPALIVE_LABEL" "$KEEPALIVE_STATUS_CODE" "$KEEPALIVE_STATUS" "$KEEPALIVE_LOG" "$KEEPALIVE_LOG_TAIL" "$DAEMON_AGENT_LABEL" "$DAEMON_AGENT_STATUS_CODE" "$DAEMON_AGENT_STATUS" "$DAEMON_HEALTH_URL" "$DAEMON_HEALTH_CODE" "$DAEMON_HEALTH" "$PROBE_STATUS_CODE" "$PROBE_JSON" "$DAEMON_LOG" "$DAEMON_LOG_TAIL" "$REPAIR_LOG" "$REPAIR_LOG_TAIL" "$REPAIR_STATE_PATH" "$REPAIR_STATE_JSON" "$REPAIR_STATE_MTIME" "$REPAIR_RESULT_PATH" "$REPAIR_RESULT_JSON" "$REPAIR_RESULT_MTIME" "$CALLBACK_FILE" "$CALLBACK_JSON" "$JOB_SUMMARY_JSON" "$COMMAND_CONNECTION_PATH" "$COMMAND_CONNECTION_JSON" <<'PY'
import json
import re
import sys
from datetime import datetime, timezone

(
    env_name,
    train_dev_url,
    keepalive_label,
    keepalive_status_code,
    keepalive_status,
    keepalive_log,
    keepalive_log_tail,
    daemon_agent_label,
    daemon_agent_status_code,
    daemon_agent_status,
    daemon_health_url,
    daemon_health_code,
    daemon_health,
    probe_status_code,
    probe_json,
    daemon_log,
    daemon_log_tail,
    repair_log,
    repair_log_tail,
    repair_state_path,
    repair_state_json,
    repair_state_mtime,
    repair_result_path,
    repair_result_json,
    repair_result_mtime,
    callback_file,
    callback_json,
    job_summary_json,
    command_connection_path,
    command_connection_json,
) = sys.argv[1:]

def parse_json_maybe(text):
    stripped = text.strip()
    if not stripped:
        return None
    candidates = [stripped]
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    candidates.extend(reversed(lines))
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and start < end:
        candidates.append(stripped[start:end + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None

def parse_timestamp_maybe(value):
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None

def age_seconds(value):
    ts = parse_timestamp_maybe(value)
    if ts is None:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - ts.astimezone(timezone.utc)).total_seconds())

def parse_epoch_maybe(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None

def timestamp_epoch(value):
    ts = parse_timestamp_maybe(value)
    if ts is None:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).timestamp()

def age_seconds_from_epoch(epoch):
    if epoch is None:
        return None
    return max(0.0, datetime.now(timezone.utc).timestamp() - float(epoch))

keepalive_loaded = "launchd_state=loaded" in keepalive_status and "path =" in keepalive_status
last_exit_match = re.search(r"last exit code = (\d+)", keepalive_status)
keepalive_last_exit_code = int(last_exit_match.group(1)) if last_exit_match else None
keepalive_recent_error = (
    "refresh_failed" in keepalive_log_tail
    or "unexpected_post_refresh_url" in keepalive_log_tail
    or "apple_events_unavailable" in keepalive_log_tail
    or "IndentationError" in keepalive_log_tail
    or "Traceback" in keepalive_log_tail
)
keepalive_operational = keepalive_loaded and keepalive_last_exit_code in (None, 0) and not keepalive_recent_error

daemon_agent_loaded = "launchd_state=loaded" in daemon_agent_status and "path =" in daemon_agent_status
if not daemon_agent_loaded:
    daemon_agent_loaded = "launchd_state=loaded" in daemon_agent_status and "state = not running" in daemon_agent_status

probe_payload = parse_json_maybe(probe_json)
probe_state = "probe_unavailable"
if probe_payload is not None:
    probe_state = str(probe_payload.get("state") or "unknown")
elif probe_json.strip():
    try:
        probe_payload = json.loads(probe_json)
        probe_state = str(probe_payload.get("state") or "unknown")
    except json.JSONDecodeError:
        probe_state = "probe_parse_error"

daemon_payload = parse_json_maybe(daemon_health)
daemon_state = "not_running"
if daemon_payload is not None:
    if bool(daemon_payload.get("ok")) or daemon_health_code == "0":
        daemon_state = "healthy"
    else:
        daemon_state = "unhealthy"
elif daemon_health.strip():
    try:
        daemon_payload = json.loads(daemon_health)
        daemon_state = "healthy" if bool(daemon_payload.get("ok")) or daemon_health_code == "0" else "unhealthy"
    except json.JSONDecodeError:
        daemon_state = "health_parse_error"

daemon_startup_state = "unknown"
daemon_ready = False
daemon_current_url = ""
daemon_startup_failure = {}
daemon_startup_failure_kind = None
daemon_shell_endpoint_failure = False
daemon_health_summary = ""
if isinstance(daemon_payload, dict):
    daemon_startup_state = str(daemon_payload.get("startupState") or "unknown")
    daemon_ready = bool(daemon_payload.get("ready"))
    daemon_current_url = str(daemon_payload.get("currentUrl") or "")
    daemon_startup_failure = daemon_payload.get("startupFailure") or {}
    daemon_startup_failure_kind = daemon_payload.get("startupFailureKind")
    daemon_shell_endpoint_failure = bool(daemon_payload.get("shellEndpointFailure"))
    daemon_health_summary = str(daemon_payload.get("healthSummary") or "")

daemon_on_train_surface = "/train-dev" in daemon_current_url
daemon_on_env_surface = "/train-dev/environment/" in daemon_current_url
daemon_operational = (
    daemon_state == "healthy"
    and daemon_ready
    and daemon_startup_state == "ready"
    and (daemon_on_train_surface or daemon_on_env_surface)
)

daemon_auth_state = "unknown"
if daemon_operational:
    daemon_auth_state = "authenticated"
elif "/auth/realms/" in daemon_current_url or "openid-connect/auth" in daemon_current_url:
    daemon_auth_state = "login_required"
elif "login_required" in daemon_log_tail or "短信登录" in daemon_log_tail or "密码登录" in daemon_log_tail:
    daemon_auth_state = "login_required"
elif daemon_state == "healthy":
    daemon_auth_state = "authenticated"

shell_endpoint_summary = ""
shell_endpoint_request = None
shell_endpoint_response = None
if isinstance(daemon_startup_failure, dict):
    shell_endpoint_summary = str(daemon_startup_failure.get("summary") or "")
    shell_endpoint_request = daemon_startup_failure.get("request")
    shell_endpoint_response = daemon_startup_failure.get("response")
if not shell_endpoint_summary and daemon_shell_endpoint_failure:
    shell_endpoint_summary = daemon_health_summary or str((daemon_payload or {}).get("startupError") or "")

cold_probe_login_required = probe_state == "login_required" and daemon_operational
repair_state_payload = parse_json_maybe(repair_state_json) or {}
repair_result_payload = parse_json_maybe(repair_result_json) or {}
callback_payload = parse_json_maybe(callback_json) or {}
repair_status = str(repair_state_payload.get("status") or "unknown")
repair_stage = str(repair_state_payload.get("stage") or "unknown")
repair_ok = repair_result_payload.get("ok")
if repair_status == "unknown" and isinstance(repair_result_payload, dict) and "ok" in repair_result_payload:
    repair_status = "succeeded" if bool(repair_result_payload.get("ok")) else "failed"
    repair_stage = "legacy_result_only"

repair_status_raw = repair_status
repair_stage_raw = repair_stage

repair_state_updated_epoch = timestamp_epoch(repair_state_payload.get("updated_at"))
if repair_state_updated_epoch is None:
    repair_state_updated_epoch = parse_epoch_maybe(repair_state_mtime)
repair_result_updated_epoch = timestamp_epoch(repair_result_payload.get("updated_at"))
if repair_result_updated_epoch is None:
    repair_result_updated_epoch = timestamp_epoch(repair_result_payload.get("timestamp_utc"))
if repair_result_updated_epoch is None:
    repair_result_updated_epoch = parse_epoch_maybe(repair_result_mtime)

repair_result_profile_synced = (
    bool(repair_result_payload.get("profileSyncedToBase"))
    if isinstance(repair_result_payload, dict) and "profileSyncedToBase" in repair_result_payload
    else None
)
repair_result_effective_success = bool(repair_ok) and repair_result_profile_synced is not False
repair_result_effective_failure = repair_ok is False
repair_result_stale_vs_state = (
    repair_state_updated_epoch is not None
    and repair_result_updated_epoch is not None
    and repair_result_updated_epoch + 2 < repair_state_updated_epoch
)

repair_state_source = "state"
if (
    repair_status in ("unknown", "failed")
    and repair_result_effective_success
    and repair_result_updated_epoch is not None
    and (
        repair_state_updated_epoch is None
        or repair_result_updated_epoch + 2 >= repair_state_updated_epoch
    )
):
    repair_status = "succeeded"
    repair_stage = "result_supersedes_state"
    repair_state_source = "result_supersedes_state"
elif (
    repair_status in ("unknown", "succeeded")
    and repair_result_effective_failure
    and repair_result_updated_epoch is not None
    and (
        repair_state_updated_epoch is None
        or repair_result_updated_epoch + 2 >= repair_state_updated_epoch
    )
):
    repair_status = "failed"
    repair_stage = "result_supersedes_state"
    repair_state_source = "result_supersedes_state"

repair_effective_updated_epoch = repair_state_updated_epoch
if repair_state_source == "result_supersedes_state":
    repair_effective_updated_epoch = repair_result_updated_epoch

repair_updated_age_sec = age_seconds_from_epoch(repair_effective_updated_epoch)
repair_result_age_sec = age_seconds_from_epoch(repair_result_updated_epoch)
callback_age_sec = age_seconds(callback_payload.get("timestamp_utc"))
command_connection_payload = parse_json_maybe(command_connection_json) or {}
command_connection_age_sec = age_seconds(command_connection_payload.get("recorded_at_utc"))
command_channel_recent_success = (
    bool(command_connection_payload.get("ok"))
    and bool(command_connection_payload.get("command_ok"))
    and (command_connection_age_sec is None or command_connection_age_sec <= 1800)
)
repair_recent_failure = repair_status == "failed" and (repair_updated_age_sec is None or repair_updated_age_sec <= 900)
repair_in_progress = repair_status == "running" and (repair_updated_age_sec is None or repair_updated_age_sec <= 600)
repair_recent_success = (
    repair_status == "succeeded"
    and repair_result_effective_success
    and (repair_updated_age_sec is None or repair_updated_age_sec <= 1800)
)

keepalive_transient_repair_noise = (
    "Terminated" in repair_log_tail
    or "Terminated" in keepalive_log_tail
)

if (daemon_shell_endpoint_failure or daemon_startup_failure_kind == "shell_endpoint_unavailable") and command_channel_recent_success:
    summary = "command_channel_connected_daemon_shell_endpoint_failed"
elif daemon_shell_endpoint_failure or daemon_startup_failure_kind == "shell_endpoint_unavailable":
    summary = "browser_daemon_shell_endpoint_failed"
elif keepalive_operational and daemon_state == "healthy" and daemon_auth_state == "authenticated" and daemon_agent_loaded:
    summary = "safari_keepalive_and_supervised_browser_daemon_healthy"
elif keepalive_operational and daemon_state == "healthy" and daemon_auth_state == "authenticated":
    summary = "safari_keepalive_and_browser_daemon_healthy"
elif keepalive_loaded and repair_in_progress and not daemon_operational:
    summary = "safari_keepalive_repair_in_progress"
elif keepalive_operational and not daemon_operational and (
    probe_state == "login_required" or daemon_auth_state == "login_required"
):
    summary = "safari_session_warm_but_browser_profile_expired"
elif keepalive_loaded and repair_recent_failure and not daemon_operational:
    summary = "safari_keepalive_loaded_profile_repair_failed"
elif keepalive_loaded and keepalive_recent_error:
    summary = "safari_keepalive_loaded_but_refresh_failing"
elif keepalive_loaded:
    summary = "safari_keepalive_healthy_browser_daemon_not_running"
else:
    summary = "keepalive_not_loaded"

job_summary = parse_json_maybe(job_summary_json) or {}

payload = {
    "env_name": env_name,
    "train_dev_url": train_dev_url,
    "summary": summary,
    "keepalive": {
        "label": keepalive_label,
        "loaded": keepalive_loaded,
        "operational": keepalive_operational,
        "last_exit_code": keepalive_last_exit_code,
        "recent_error": keepalive_recent_error,
        "status_command_ok": keepalive_status_code == "0",
        "status_output": keepalive_status,
        "log_path": keepalive_log,
        "recent_log_tail": keepalive_log_tail,
        "transient_repair_noise": keepalive_transient_repair_noise,
    },
    "browser_daemon": {
        "env_name": env_name,
        "health_url": daemon_health_url,
        "health_ok": daemon_health_code == "0",
        "state": daemon_state,
        "payload": daemon_payload,
        "auth_state": daemon_auth_state,
        "operational": daemon_operational,
        "startup_state": daemon_startup_state,
        "startup_failure": daemon_startup_failure,
        "startup_failure_kind": daemon_startup_failure_kind,
        "shell_endpoint_failure": daemon_shell_endpoint_failure,
        "health_summary": daemon_health_summary,
        "current_url": daemon_current_url,
        "log_path": daemon_log,
        "recent_log_tail": daemon_log_tail,
    },
    "command_channel": {
        "status_path": command_connection_path,
        "recent_success": command_channel_recent_success,
        "age_seconds": command_connection_age_sec,
        "payload": command_connection_payload,
        "transport": command_connection_payload.get("transport"),
        "browser_mode": command_connection_payload.get("browser_mode"),
        "url": command_connection_payload.get("url"),
        "duration_ms": command_connection_payload.get("duration_ms"),
    },
    "browser_daemon_ai2": {
        "health_url": daemon_health_url,
        "health_ok": daemon_health_code == "0",
        "state": daemon_state,
        "payload": daemon_payload,
        "auth_state": daemon_auth_state,
        "operational": daemon_operational,
        "startup_state": daemon_startup_state,
        "current_url": daemon_current_url,
        "log_path": daemon_log,
        "recent_log_tail": daemon_log_tail,
    },
    "browser_daemon_agent_ai2": {
        "label": daemon_agent_label,
        "loaded": daemon_agent_loaded,
        "status_command_ok": daemon_agent_status_code == "0",
        "status_output": daemon_agent_status,
    },
    "browser_profile_probe": {
        "command_ok": probe_status_code == "0",
        "state": probe_state,
        "payload": probe_payload,
        "raw_output": probe_json,
    },
    "browser_profile_repair": {
        "state_path": repair_state_path,
        "result_path": repair_result_path,
        "log_path": repair_log,
        "state_raw": repair_status_raw,
        "stage_raw": repair_stage_raw,
        "state": repair_status,
        "stage": repair_stage,
        "result_ok": repair_ok,
        "result_profile_synced_to_base": repair_result_profile_synced,
        "result_effective_success": repair_result_effective_success,
        "result_stale_vs_state": repair_result_stale_vs_state,
        "effective_state_source": repair_state_source,
        "state_updated_epoch": repair_state_updated_epoch,
        "result_updated_epoch": repair_result_updated_epoch,
        "result_age_seconds": repair_result_age_sec,
        "state_payload": repair_state_payload,
        "result_payload": repair_result_payload,
        "recent_log_tail": repair_log_tail,
        "running": repair_in_progress,
        "recent_success": repair_recent_success,
        "recent_failure": repair_recent_failure,
    },
    "safari_callback_bridge": {
        "path": callback_file,
        "payload": callback_payload,
        "age_seconds": callback_age_sec,
    },
    "local_ai2_jobs": job_summary,
    "diagnostics": {
        "env_name": env_name,
        "canonical_train_dev_url": train_dev_url,
        "cold_probe_login_required": cold_probe_login_required,
        "probe_should_block_shell_ops": not daemon_operational and probe_state == "login_required" and not repair_in_progress,
        "effective_shell_authority": "daemon" if daemon_operational else "probe_or_repair",
        "daemon_agent_health_mismatch": daemon_agent_loaded and daemon_health_code != "0",
        "shell_endpoint_summary": shell_endpoint_summary,
        "shell_endpoint_request": shell_endpoint_request,
        "shell_endpoint_response": shell_endpoint_response,
        "command_channel_recent_success": command_channel_recent_success,
        "command_channel_age_seconds": command_connection_age_sec,
        "repair_state_age_seconds": repair_updated_age_sec,
        "repair_result_age_seconds": repair_result_age_sec,
        "repair_result_stale_vs_state": repair_result_stale_vs_state,
        "callback_age_seconds": callback_age_sec,
    },
    "guidance": {
        "normal_path": "Keep the Safari keepalive LaunchAgent installed, use on-demand daemon-backed shell wrappers by default, and only opt into the ai2 daemon LaunchAgent with HUANXIN_USE_DAEMON_AGENT=1 after explicit validation.",
        "diagnosis_rule": "Distinguish three states: train-dev opened/authenticated, daemon terminal endpoint ready, and command channel verified. If the daemon terminal endpoint fails with getShellVisitUrl but a wrapper records a recent command_channel success, report the daemon endpoint failure as a degraded control-plane condition rather than claiming Codex cannot connect.",
    },
}
print(json.dumps(payload, indent=2, ensure_ascii=False))
PY
