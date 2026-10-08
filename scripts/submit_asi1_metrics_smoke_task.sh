#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

default_train_dev_url() {
  python3 "$ROOT_DIR/scripts/huanxin_env_config.py" --env ASI1 --field train_dev_url
}

TASK_NAME="${ASI1_METRICS_SMOKE_TASK_NAME:-asi1-metric-smoke}"
IMAGE_NAME="${ASI1_METRICS_SMOKE_IMAGE_NAME:-qwen3.5-27B-35B-122B-397B-031626-zx}"
RESOURCE_GROUP="${ASI1_METRICS_SMOKE_RESOURCE_GROUP:-huanxin-all-resource}"
RESOURCE_GROUP_TYPE="${ASI1_METRICS_SMOKE_RESOURCE_GROUP_TYPE:-公共资源组}"
INSTANCE_COUNT="${ASI1_METRICS_SMOKE_INSTANCE_COUNT:-1}"
ACCELERATOR_CARDS="${ASI1_METRICS_SMOKE_ACCELERATOR_CARDS:-1}"
CPU_CORES="${ASI1_METRICS_SMOKE_CPU_CORES:-4}"
MEMORY_GB="${ASI1_METRICS_SMOKE_MEMORY_GB:-16}"
WAIT_MS="${ASI1_METRICS_SMOKE_WAIT_MS:-12000}"
ARTIFACT_STEM="${ASI1_METRICS_SMOKE_ARTIFACT_STEM:-huanxin-submit-task-run-asi1-metric-smoke}"
REMOTE_ROOT="${ASI1_METRICS_SMOKE_REMOTE_ROOT:-/tmp}"
TIMESTAMP="${ASI1_METRICS_SMOKE_TIMESTAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
REMOTE_OUTPUT_DIR="${ASI1_METRICS_SMOKE_OUTPUT_DIR:-/tmp/qg-asi1-metric-smoke-${TIMESTAMP}}"
TRAIN_DEV_URL="${ASI1_METRICS_SMOKE_URL:-}"
SUBMIT=0
PRINT_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  scripts/submit_asi1_metrics_smoke_task.sh [--submit] [options]

Submits a tiny ASI1 no-shell task that writes GRPO-like metric/eval artifacts
under /tmp. It proves task execution and dashboard ingestion without touching
the quota-broken remote repo.

Options:
  --submit
  --dry-run
  --task-name <name>
  --artifact-stem <stem>
  --remote-output-dir <path>
  --image-name <name>
  --wait-ms <ms>
EOF
}

shell_quote() {
  python3 -c 'import shlex,sys; print(" ".join(shlex.quote(arg) for arg in sys.argv[1:]))' "$@"
}

render_launch_spec() {
  python3 - "$REMOTE_OUTPUT_DIR" "$TIMESTAMP" <<'PY'
import json
import shlex
import sys

output_dir, timestamp = sys.argv[1:3]
script = r"""
import json
import os
import shutil
import time
from pathlib import Path

out = Path(os.environ["ASI1_METRICS_SMOKE_OUTPUT_DIR"])
out.mkdir(parents=True, exist_ok=True)
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
metrics = []
evals = []
for step in range(1, 4):
    row = {
        "step": step,
        "mean_reward": round(0.20 + 0.08 * step, 4),
        "reward_signal_std": round(0.03 + 0.01 * step, 4),
        "pass_rate": round(0.25 + 0.10 * step, 4),
        "loss": round(1.20 - 0.07 * step, 4),
        "kl_coeff": 0.02,
        "skipped": False,
        "termination_counts": {"final_answer": step},
        "trajectory_tool_counts": {"search_repo": step, "read_file": step + 1, "write_file": 1, "run_tests": 1, "final_answer": 1},
        "timestamp_utc": now,
    }
    metrics.append(row)
    with (out / "grpo_step_metrics.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    ev = {
        "step": step,
        "pass_rate": round(0.20 + 0.09 * step, 4),
        "mean_total_reward": round(0.30 + 0.08 * step, 4),
        "task_count": 2,
        "domain_metrics": {
            "quantum": {"pass_rate": round(0.15 + 0.10 * step, 4), "task_count": 1},
            "software": {"pass_rate": round(0.25 + 0.08 * step, 4), "task_count": 1},
        },
        "failure_categories": {},
        "timestamp_utc": now,
    }
    evals.append(ev)
    with (out / "online_eval_history.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(ev, sort_keys=True) + "\n")
live = {
    "schema_version": 1,
    "status": "running",
    "planned_steps": 3,
    "summary": {"planned_steps": 3, "recorded_steps": 3, "updated_steps": 3, "skipped_steps": 0, "skip_reasons": {}},
    "recent": {"window": 3, "recorded_steps": 3, "updated_steps": 3, "mean_reward": metrics[-1]["mean_reward"], "mean_pass_rate": metrics[-1]["pass_rate"], "mean_loss": metrics[-1]["loss"], "termination_counts": metrics[-1]["termination_counts"]},
    "last_record": metrics[-1],
    "online_eval_latest": evals[-1],
    "latest_checkpoint": {"step": 3, "checkpoint_dir": str(out / "checkpoint-3"), "saved_count": 1},
    "alerts": [],
    "job_health": {"environment": "ASI1", "huanxin_task_name": os.environ.get("ASI1_METRICS_SMOKE_TASK_NAME"), "huanxin_task_status": "running", "remote_path": str(out), "last_metric_age_sec": 0, "last_log_age_sec": 0, "npu_visible": "not sampled in metrics smoke", "updated_at_utc": now},
    "updated_at_utc": now,
}
(out / "live_status.json").write_text(json.dumps(live, indent=2, sort_keys=True) + "\n", encoding="utf-8")
(out / "job_health.json").write_text(json.dumps(live["job_health"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
(out / "run_config.json").write_text(json.dumps({"schema_version": 1, "environment": "ASI1", "model_name": "metrics-smoke-no-model", "grpo_steps": 3, "remote_output_dir": str(out), "benchmark_file": "metrics_smoke", "online_eval_benchmark_file": "metrics_smoke_quantum_software"}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
(out / "run_manifest.json").write_text(json.dumps({"schema_version": 1, "run_id": out.name, "environment": "ASI1", "model_name": "metrics-smoke-no-model", "remote_output_dir": str(out)}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
(out / "safety_report.json").write_text(json.dumps({"schema_version": 1, "unsafe_tool_events": 0, "prompt_injection_events": 0, "secrets_events": 0, "destructive_command_blocks": 0, "status": "smoke"}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
(out / "train_log_tail.txt").write_text("__ASI1_METRICS_SMOKE_START__\nmetrics_written=3\n__ASI1_METRICS_SMOKE_DONE__\n", encoding="utf-8")
print("__ASI1_METRICS_SMOKE_START__")
print("output_dir=" + str(out))
print("disk=" + shutil.disk_usage(str(out)).__repr__())
print("__ASI1_METRICS_SMOKE_DONE__")
"""
commands = [
    "set -euo pipefail",
    "echo __ASI1_METRICS_SMOKE_BOOT__",
    "python3 --version",
    f"export ASI1_METRICS_SMOKE_OUTPUT_DIR={shlex.quote(output_dir)}",
    "export ASI1_METRICS_SMOKE_TASK_NAME=${ASI1_METRICS_SMOKE_TASK_NAME:-asi1-metric-smoke}",
    "python3 -c " + shlex.quote(script),
]
execution_command = "\n".join(commands)
print(
    json.dumps(
        {
            "remote_root": "/tmp",
            "output_dir": output_dir,
            "log_path": f"{output_dir}/train_log_tail.txt",
            "job_name": "asi1-metric-smoke",
            "remote_command": execution_command,
            "execution_command": execution_command,
        },
        indent=2,
    )
)
PY
}

if [[ "${1:-}" == "--dry-run" && "${2:-}" == "__launch-spec" ]]; then
  render_launch_spec
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --submit) SUBMIT=1; shift ;;
    --dry-run) PRINT_ONLY=1; shift ;;
    --task-name) TASK_NAME="${2:-}"; shift 2 ;;
    --artifact-stem) ARTIFACT_STEM="${2:-}"; shift 2 ;;
    --remote-output-dir) REMOTE_OUTPUT_DIR="${2:-}"; shift 2 ;;
    --image-name) IMAGE_NAME="${2:-}"; shift 2 ;;
    --wait-ms) WAIT_MS="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$TRAIN_DEV_URL" ]]; then
  TRAIN_DEV_URL="$(default_train_dev_url)"
fi

export ASI1_METRICS_SMOKE_OUTPUT_DIR="$REMOTE_OUTPUT_DIR"
export ASI1_METRICS_SMOKE_TASK_NAME="$TASK_NAME"

CMD=(
  node
  "$ROOT_DIR/browser-automation/huanxin_submit_task_run.js"
  --url "$TRAIN_DEV_URL"
  --wait-ms "$WAIT_MS"
  --task-name "$TASK_NAME"
  --image-name "$IMAGE_NAME"
  --resource-group "$RESOURCE_GROUP"
  --resource-group-type "$RESOURCE_GROUP_TYPE"
  --instance-count "$INSTANCE_COUNT"
  --accelerator-cards "$ACCELERATOR_CARDS"
  --cpu-cores "$CPU_CORES"
  --memory-gb "$MEMORY_GB"
  --remote-root "$REMOTE_ROOT"
  --launcher-script "$ROOT_DIR/scripts/submit_asi1_metrics_smoke_task.sh"
  --launcher-arg "__launch-spec"
  --screenshot "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.png"
  --dump-html "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.html"
  --dump-json "$ROOT_DIR/browser-automation/${ARTIFACT_STEM}.json"
)

if [[ "$SUBMIT" == "1" ]]; then
  CMD+=(--submit)
fi

if [[ "$PRINT_ONLY" == "1" ]]; then
  shell_quote "${CMD[@]}"
  exit 0
fi

cd "$ROOT_DIR"
exec "${CMD[@]}"
