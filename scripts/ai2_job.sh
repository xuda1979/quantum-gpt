#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_ROOT="${AI2_JOB_REMOTE_ROOT:-/root/root/work/quantum-gpt}"
SHELL_WRAPPER="${AI2_JOB_SHELL_WRAPPER:-$ROOT_DIR/scripts/ai2_shell.sh}"
META_DIR="${AI2_JOB_META_DIR:-$ROOT_DIR/.huanxin_jobs}"
TAIL_LINES_DEFAULT="${HUANXIN_JOB_TAIL_LINES:-40}"

usage() {
  cat >&2 <<'EOF'
Usage:
  scripts/ai2_job.sh start <job-name> <log-path> "<remote command>"
  scripts/ai2_job.sh show <job-id>
  scripts/ai2_job.sh latest [name-substring]
  scripts/ai2_job.sh status <job-id> [tail-lines]
  scripts/ai2_job.sh logs <job-id> [tail-lines]
  scripts/ai2_job.sh ps [egrep-pattern]
  scripts/ai2_job.sh stop <job-id> [signal]
  scripts/ai2_job.sh list
EOF
  exit 1
}

read_json_field() {
  python3 - <<'PY' "$1" "$2"
import json
import sys

payload = json.loads(sys.argv[1])
field = sys.argv[2]
print(payload.get(field, ""))
PY
}

combine_transcript() {
  python3 - <<'PY' "$1"
import json
import sys

payload = json.loads(sys.argv[1])
parts = [payload.get("output", ""), payload.get("after", ""), payload.get("before", "")]
print("\n".join(part for part in parts if part))
PY
}

extract_primary_output() {
  python3 - <<'PY' "$1"
import json
import re
import sys

payload = json.loads(sys.argv[1])
after = str(payload.get("after") or "").replace("\r\n", "\n").replace("\r", "\n")
after_lines = after.split("\n")
start_pattern = re.compile(r"^(__OC_[A-Za-z0-9_]+_START__)\s*$")

start_index = None
end_marker = None
for index, raw_line in enumerate(after_lines):
    match = start_pattern.match(raw_line.strip())
    if not match:
        continue
    start_index = index
    end_marker = match.group(1).replace("_START__", "_END__")

if start_index is not None and end_marker is not None:
    captured = []
    for raw_line in after_lines[start_index + 1:]:
        if raw_line.strip() == end_marker:
            break
        captured.append(raw_line)
    extracted = "\n".join(captured).strip("\n")
    if extracted.strip():
        print(extracted)
        raise SystemExit(0)

output = str(payload.get("output") or "").replace("\r\n", "\n").replace("\r", "\n")
if output.strip():
    print(output)
    raise SystemExit(0)

parts = [payload.get("after", ""), payload.get("before", "")]
print("\n".join(str(part) for part in parts if part))
PY
}

load_meta_field() {
  python3 - <<'PY' "$1" "$2"
import json
import sys

with open(sys.argv[1], encoding='utf-8') as handle:
    payload = json.load(handle)
print(payload.get(sys.argv[2], ""))
PY
}

load_meta_json() {
  python3 - <<'PY' "$1"
import json
import sys

with open(sys.argv[1], encoding='utf-8') as handle:
    payload = json.load(handle)
print(json.dumps(payload, indent=2))
PY
}

run_remote_command() {
  bash "$SHELL_WRAPPER" "$1"
}

mkdir -p "$META_DIR"

subcommand="${1:-}"
case "$subcommand" in
  start)
    [[ $# -eq 4 ]] || usage
    job_name="$2"
    log_path="$3"
    remote_command="$4"
    safe_job_name="$(printf '%s' "$job_name" | tr -cs 'A-Za-z0-9._-' '-')"
    job_id="${safe_job_name}-$(date -u +%Y%m%dT%H%M%SZ)"
    meta_file="$META_DIR/${job_id}.json"
    escaped_remote_command="$(printf '%q' "$remote_command")"
    remote_launch="cd '$REMOTE_ROOT' && nohup bash -lc ${escaped_remote_command} > '$log_path' 2>&1 < /dev/null & pid=\$!; printf '__OPENCLAW_JOB__ id=$job_id pid=%s log=$log_path cwd=$REMOTE_ROOT\n' \"\$pid\""
    json_out="$(run_remote_command "$remote_launch")"
    primary_output="$(extract_primary_output "$json_out")"
    transcript="$(combine_transcript "$json_out")"
    python3 - <<'PY' "$meta_file" "$json_out" "$primary_output" "$transcript" "$job_id" "$job_name" "$log_path" "$remote_command" "$REMOTE_ROOT"
import json
import re
import sys
from datetime import datetime, timezone

meta_file, json_out, primary_output, transcript, job_id, job_name, log_path, remote_command, remote_root = sys.argv[1:10]

def normalize(text: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*[ -/]*[@-~]", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

marker_regex = rf"__OPENCLAW_JOB__\s*id={re.escape(job_id)}\s*pid=(\d+)"
match = re.search(marker_regex, normalize(primary_output))
if not match:
    match = re.search(marker_regex, normalize(transcript))
if not match:
    raise SystemExit(
        "Did not observe durable job marker in shell transcript.\n"
        f"--- primary_output ---\n{primary_output}\n"
        f"--- transcript ---\n{transcript}"
    )

payload = json.loads(json_out)
job_payload = {
    "job_id": job_id,
    "name": job_name,
    "pid": int(match.group(1)),
    "log_path": log_path,
    "remote_root": remote_root,
    "command": remote_command,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "transport": payload.get("transport"),
    "duration_ms": payload.get("durationMs"),
    "meta_file": meta_file,
}
with open(meta_file, 'w', encoding='utf-8') as handle:
    json.dump(job_payload, handle, indent=2)
print(json.dumps(job_payload, indent=2))
PY
    ;;
  show)
    [[ $# -eq 2 ]] || usage
    job_id="$2"
    meta_file="$META_DIR/${job_id}.json"
    [[ -f "$meta_file" ]] || { echo "unknown job: $job_id" >&2; exit 1; }
    load_meta_json "$meta_file"
    ;;
  latest)
    [[ $# -le 2 ]] || usage
    filter_text="${2:-}"
    python3 - <<'PY' "$META_DIR" "$filter_text"
import glob
import json
import os
import sys

meta_dir, filter_text = sys.argv[1:3]
items = []
for path in sorted(glob.glob(os.path.join(meta_dir, '*.json'))):
    with open(path, encoding='utf-8') as handle:
        payload = json.load(handle)
    if filter_text and filter_text not in str(payload.get("job_id", "")) and filter_text not in str(payload.get("name", "")):
        continue
    items.append(payload)

if not items:
    raise SystemExit(f"no jobs matched filter: {filter_text}" if filter_text else "no jobs found")

items.sort(key=lambda item: str(item.get("created_at") or item.get("job_id") or ""))
print(json.dumps(items[-1], indent=2))
PY
    ;;
  status|logs)
    [[ $# -ge 2 && $# -le 3 ]] || usage
    job_id="$2"
    tail_lines="${3:-$TAIL_LINES_DEFAULT}"
    meta_file="$META_DIR/${job_id}.json"
    [[ -f "$meta_file" ]] || { echo "unknown job: $job_id" >&2; exit 1; }
    pid="$(load_meta_field "$meta_file" pid)"
    log_path="$(load_meta_field "$meta_file" log_path)"
    remote_root="$(load_meta_field "$meta_file" remote_root)"
    remote_status="cd '$remote_root' && echo '__OPENCLAW_JOB_STATUS_BEGIN__'; if ps -p '$pid' -o pid=,stat=,etimes=,command= >/dev/null 2>&1; then echo '__OPENCLAW_JOB_STATUS__ running'; ps -p '$pid' -o pid=,stat=,etimes=,command=; else echo '__OPENCLAW_JOB_STATUS__ exited'; fi; echo '__OPENCLAW_JOB_STATUS_END__'; if [[ -f '$log_path' ]]; then echo '__OPENCLAW_JOB_LOG_BEGIN__'; tail -n '$tail_lines' '$log_path'; echo '__OPENCLAW_JOB_LOG_END__'; else echo '__OPENCLAW_JOB_LOG_MISSING__'; fi"
    json_out="$(run_remote_command "$remote_status")"
    primary_output="$(extract_primary_output "$json_out")"
    transcript="$(combine_transcript "$json_out")"
    python3 - <<'PY' "$meta_file" "$json_out" "$primary_output" "$transcript"
import json
import re
import sys

meta_file, json_out, primary_output, transcript = sys.argv[1:5]
with open(meta_file, encoding='utf-8') as handle:
    meta = json.load(handle)

def normalize(text: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*[ -/]*[@-~]", "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text

def extract_sections(text: str):
    normalized = normalize(text)
    status_begin = '__OPENCLAW_JOB_STATUS_BEGIN__'
    status_end = '__OPENCLAW_JOB_STATUS_END__'
    log_begin = '__OPENCLAW_JOB_LOG_BEGIN__'
    log_end = '__OPENCLAW_JOB_LOG_END__'

    if status_begin not in normalized:
        return None

    status_block = normalized.split(status_begin, 1)[1]
    if status_end in status_block:
        status_block = status_block.split(status_end, 1)[0]

    log_tail = ''
    if log_begin in normalized and log_end in normalized:
        log_tail = normalized.split(log_begin, 1)[1].split(log_end, 1)[0].strip()
    elif '__OPENCLAW_JOB_LOG_MISSING__' in normalized:
        log_tail = ''

    status = 'unknown'
    ps_lines = []
    for raw_line in status_block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith('__OPENCLAW_JOB_STATUS__'):
            status = line.split('__OPENCLAW_JOB_STATUS__', 1)[1].strip() or 'unknown'
            continue
        ps_lines.append(line)

    return {
        'status': status,
        'ps_lines': ps_lines,
        'log_tail': log_tail,
        'normalized': normalized,
    }

def extract_log_tail(normalized: str) -> str:
    log_begin = '__OPENCLAW_JOB_LOG_BEGIN__'
    log_end = '__OPENCLAW_JOB_LOG_END__'
    if log_begin in normalized and log_end in normalized:
        return normalized.split(log_begin, 1)[1].split(log_end, 1)[0].strip()
    if '__OPENCLAW_JOB_LOG_MISSING__' in normalized:
        return ''
    return normalized.strip()

def extract_status_without_boundaries(text: str):
    normalized = normalize(text)
    status = None
    ps_lines = []
    for raw_line in normalized.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith('__OPENCLAW_JOB_STATUS__'):
            status = line.split('__OPENCLAW_JOB_STATUS__', 1)[1].strip() or 'unknown'
            continue
        if line.startswith('__OPENCLAW_JOB_'):
            continue
        ps_lines.append(line)
    if status is None:
        return None
    return {
        'status': status,
        'ps_lines': ps_lines,
        'log_tail': extract_log_tail(normalized),
        'normalized': normalized,
        'status_source': 'status_line_fallback',
    }

def extract_completed_job_fallback(text: str):
    normalized = normalize(text)
    if not normalized.strip():
        return None
    completion_markers = (
        '"stage": "final_eval_done"',
        '"stage":"final_eval_done"',
        '"stage": "save_done"',
        '"stage":"save_done"',
    )
    has_metrics_summary = '"completed_steps"' in normalized and '"final_eval"' in normalized
    has_scorecard_summary = 'Scorecard written to:' in normalized and 'Overall:' in normalized
    if (
        not any(marker in normalized for marker in completion_markers)
        and not has_metrics_summary
        and not has_scorecard_summary
    ):
        return None
    status_source = 'completion_marker_fallback'
    if has_scorecard_summary and not any(marker in normalized for marker in completion_markers) and not has_metrics_summary:
        status_source = 'scorecard_summary_fallback'
    return {
        'status': 'exited',
        'ps_lines': [],
        'log_tail': extract_log_tail(normalized),
        'normalized': normalized,
        'status_source': status_source,
    }

sections = extract_sections(primary_output)
if sections is None:
    sections = extract_sections(transcript)
if sections is None:
    sections = extract_status_without_boundaries(primary_output)
if sections is None:
    sections = extract_status_without_boundaries(transcript)
if sections is None:
    sections = extract_completed_job_fallback(primary_output)
if sections is None:
    sections = extract_completed_job_fallback(transcript)
if sections is None:
    raise SystemExit(
        "Did not observe job status markers in shell output.\n"
        f"--- primary_output ---\n{primary_output}\n"
        f"--- transcript ---\n{transcript}"
    )

result = {
    **meta,
    'status': sections['status'],
    'ps': sections['ps_lines'],
    'log_tail': sections['log_tail'],
    'status_source': sections.get('status_source', 'status_markers'),
    'transport': json.loads(json_out).get('transport'),
    'duration_ms': json.loads(json_out).get('durationMs'),
}
print(json.dumps(result, indent=2))
PY
    ;;
  ps)
    [[ $# -le 2 ]] || usage
    pattern="${2:-torchrun|python3 .*training/|serve_openai_chat_adapter|run_hf_pass1_eval}"
    escaped_pattern="$(printf '%q' "$pattern")"
    remote_ps="cd '$REMOTE_ROOT' && echo '__OPENCLAW_REMOTE_PS_BEGIN__'; ps -eo pid=,stat=,etimes=,command= | sed 's/^ *//' | grep -E ${escaped_pattern} || true; echo '__OPENCLAW_REMOTE_PS_END__'"
    json_out="$(run_remote_command "$remote_ps")"
    primary_output="$(extract_primary_output "$json_out")"
    transcript="$(combine_transcript "$json_out")"
    python3 - <<'PY' "$json_out" "$primary_output" "$transcript" "$pattern"
import json
import re
import sys

json_out, primary_output, transcript, pattern = sys.argv[1:5]
payload = json.loads(json_out)

def normalize(text: str) -> str:
    text = re.sub(r"\x1b\[[0-9;]*[ -/]*[@-~]", "", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")

def extract_ps_lines(text: str):
    begin = "__OPENCLAW_REMOTE_PS_BEGIN__"
    end = "__OPENCLAW_REMOTE_PS_END__"
    lines = normalize(text).splitlines()
    begin_index = None
    end_index = None
    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if line == begin:
            begin_index = index
        elif begin_index is not None and line == end:
            end_index = index
            break
    if begin_index is None or end_index is None:
        return None
    return [line.strip() for line in lines[begin_index + 1:end_index] if line.strip()]

lines = []
for text in (primary_output, payload.get("after", ""), transcript):
    extracted = extract_ps_lines(str(text or ""))
    if extracted is None:
        continue
    lines = extracted
    break
result = {
    "pattern": pattern,
    "lines": lines,
    "transport": payload.get("transport"),
    "duration_ms": payload.get("durationMs"),
}
print(json.dumps(result, indent=2))
PY
    ;;
  stop)
    [[ $# -ge 2 && $# -le 3 ]] || usage
    job_id="$2"
    signal_name="${3:-TERM}"
    meta_file="$META_DIR/${job_id}.json"
    [[ -f "$meta_file" ]] || { echo "unknown job: $job_id" >&2; exit 1; }
    pid="$(load_meta_field "$meta_file" pid)"
    log_path="$(load_meta_field "$meta_file" log_path)"
    remote_root="$(load_meta_field "$meta_file" remote_root)"
    remote_stop="cd '$remote_root' && if ps -p '$pid' >/dev/null 2>&1; then kill -s '$signal_name' '$pid'; rc=\$?; sleep 1; if ps -p '$pid' >/dev/null 2>&1; then echo '__OPENCLAW_JOB_STOP__ still_running'; else echo '__OPENCLAW_JOB_STOP__ stopped'; fi; exit \$rc; else echo '__OPENCLAW_JOB_STOP__ missing'; fi; if [[ -f '$log_path' ]]; then echo '__OPENCLAW_JOB_LOG__'; tail -n '$TAIL_LINES_DEFAULT' '$log_path'; fi"
    json_out="$(run_remote_command "$remote_stop")"
    primary_output="$(extract_primary_output "$json_out")"
    transcript="$(combine_transcript "$json_out")"
    python3 - <<'PY' "$meta_file" "$json_out" "$primary_output" "$transcript" "$signal_name"
import json
import sys

meta_file, json_out, primary_output, transcript, signal_name = sys.argv[1:6]
with open(meta_file, encoding='utf-8') as handle:
    meta = json.load(handle)

result = {
    **meta,
    "signal": signal_name,
    "stop_result": "unknown",
    "transport": json.loads(json_out).get("transport"),
    "duration_ms": json.loads(json_out).get("durationMs"),
}

combined = "\n".join(part for part in (primary_output, transcript) if part)
if "__OPENCLAW_JOB_STOP__ stopped" in combined:
    result["stop_result"] = "stopped"
elif "__OPENCLAW_JOB_STOP__ still_running" in combined:
    result["stop_result"] = "still_running"
elif "__OPENCLAW_JOB_STOP__ missing" in combined:
    result["stop_result"] = "missing"
print(json.dumps(result, indent=2))
PY
    ;;
  list)
    python3 - <<'PY' "$META_DIR"
import glob
import json
import os
import sys

items = []
for path in sorted(glob.glob(os.path.join(sys.argv[1], '*.json'))):
    with open(path, encoding='utf-8') as handle:
        items.append(json.load(handle))
print(json.dumps(items, indent=2))
PY
    ;;
  *)
    usage
    ;;
esac
