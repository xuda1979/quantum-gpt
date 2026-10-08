#!/usr/bin/env python3
"""Refresh a local dashboard run directory from a remote Huanxin GRPO log."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", required=True)
    parser.add_argument("--remote-output-dir", required=True)
    parser.add_argument("--local-run-dir", type=Path, required=True)
    parser.add_argument("--timeout-sec", type=int, default=45)
    parser.add_argument("--tail-lines", type=int, default=80)
    return parser.parse_args()


def remote_probe_command(remote_output_dir: str, tail_lines: int) -> str:
    payload = r"""
from pathlib import Path
import base64
import json
import subprocess
import time

out = Path(__REMOTE_OUTPUT_DIR__)
tail_lines = int(__TAIL_LINES__)
log = out / "train.log"
metrics = out / "grpo_step_metrics.jsonl"
evalh = out / "online_eval_history.jsonl"
ckpt = out / "latest_checkpoint.json"
exitp = out / "remote_exit_status.json"
pidp = out / "pid"
pid = pidp.read_text().strip() if pidp.exists() else ""
ps = ""
if pid:
    ps = subprocess.run(
        ["bash", "-lc", f"ps -p {pid} -o pid,stat,etime --no-headers || true"],
        capture_output=True,
        text=True,
    ).stdout.strip()

def read_lines(path, limit):
    if not path.exists():
        return []
    return path.read_text(errors="replace").splitlines()[-limit:]

def read_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(errors="replace"))
    except Exception:
        return None

def read_jsonl(path, limit=20):
    rows = []
    if path.exists():
        for line in path.read_text(errors="replace").splitlines()[-500:]:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows[-limit:]

lines = read_lines(log, tail_lines)
payload = {
    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "remote_output_dir": str(out),
    "pid": pid,
    "process": ps,
    "alive": bool(ps) and " Z " not in f" {ps} ",
    "exit_status": read_json(exitp),
    "train_log_tail": lines,
    "metrics_tail": read_jsonl(metrics),
    "online_eval_tail": read_jsonl(evalh),
    "latest_checkpoint": read_json(ckpt),
    "files": {
        "train_log_bytes": log.stat().st_size if log.exists() else 0,
        "metrics_bytes": metrics.stat().st_size if metrics.exists() else 0,
        "online_eval_bytes": evalh.stat().st_size if evalh.exists() else 0,
        "checkpoint_exists": ckpt.exists(),
        "exit_exists": exitp.exists(),
    },
}
print("__QG_REMOTE_LOG_STATUS_BEGIN__")
print(base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("ascii"))
print("__QG_REMOTE_LOG_STATUS_END__")
"""
    code = payload.replace("__REMOTE_OUTPUT_DIR__", repr(remote_output_dir)).replace(
        "__TAIL_LINES__", repr(str(tail_lines))
    )
    return "python3 - <<'PY'\n" + code + "\nPY"


def extract_payload(raw: str) -> dict[str, Any]:
    match = re.search(
        r"__QG_REMOTE_LOG_STATUS_BEGIN__\s*([A-Za-z0-9+/=\s]+?)\s*__QG_REMOTE_LOG_STATUS_END__",
        raw,
        flags=re.S,
    )
    if not match:
        raise RuntimeError("remote log status markers not found")
    import base64

    return json.loads(base64.b64decode("".join(match.group(1).split())).decode("utf-8"))


def run_remote(env: str, command: str, timeout_sec: int) -> dict[str, Any]:
    proc = subprocess.run(
        ["bash", str(ROOT / "scripts" / "huanxin_shell.sh"), env, command],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"huanxin_shell failed rc={proc.returncode}: {proc.stderr[-1000:]}")
    try:
        wrapper = json.loads(proc.stdout)
        combined = "\n".join(str(wrapper.get(key, "")) for key in ("output", "after", "before"))
    except Exception:
        combined = proc.stdout
    return extract_payload(combined)


def status_from_payload(payload: dict[str, Any]) -> str:
    exit_status = payload.get("exit_status") or {}
    if exit_status:
        return "completed" if int(exit_status.get("exit_code", 1)) == 0 else "failed"
    if payload.get("alive"):
        return "running"
    return "unknown"


def write_local_artifacts(payload: dict[str, Any], local_run_dir: Path) -> None:
    local_run_dir.mkdir(parents=True, exist_ok=True)
    status = status_from_payload(payload)
    metrics_tail = list(payload.get("metrics_tail") or [])
    eval_tail = list(payload.get("online_eval_tail") or [])
    latest_metric = metrics_tail[-1] if metrics_tail else {}
    latest_eval = eval_tail[-1] if eval_tail else {}
    latest_checkpoint = payload.get("latest_checkpoint")
    files = dict(payload.get("files") or {})
    exit_status = payload.get("exit_status")

    (local_run_dir / "train_log_tail.txt").write_text(
        "\n".join(str(line) for line in payload.get("train_log_tail") or []) + "\n",
        encoding="utf-8",
    )
    if metrics_tail:
        (local_run_dir / "grpo_step_metrics.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in metrics_tail),
            encoding="utf-8",
        )
    if eval_tail:
        (local_run_dir / "online_eval_history.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in eval_tail),
            encoding="utf-8",
        )
    if latest_checkpoint:
        (local_run_dir / "latest_checkpoint.json").write_text(
            json.dumps(latest_checkpoint, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    run_config = {
        "run_id": local_run_dir.name,
        "environment": "ASI1",
        "remote_output_dir": payload.get("remote_output_dir"),
        "source": "remote_train_log",
    }
    existing_config = local_run_dir / "run_config.json"
    if existing_config.exists():
        try:
            run_config = {**json.loads(existing_config.read_text(encoding="utf-8")), **run_config}
        except Exception:
            pass
    (local_run_dir / "run_config.json").write_text(
        json.dumps(run_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    live_status = {
        "status": status,
        "updated_at": payload.get("timestamp_utc"),
        "remote_output_dir": payload.get("remote_output_dir"),
        "summary": {
            "recorded_steps": len(metrics_tail),
            "updated_steps": sum(1 for row in metrics_tail if not row.get("skipped")),
            "skipped_steps": sum(1 for row in metrics_tail if row.get("skipped")),
        },
        "last_record": latest_metric,
        "online_eval_latest": latest_eval,
        "latest_checkpoint": latest_checkpoint or {},
        "job_health": {
            "state": status,
            "remote_pid": payload.get("pid"),
            "remote_process": payload.get("process"),
            "train_log_bytes": files.get("train_log_bytes"),
            "metrics_bytes": files.get("metrics_bytes"),
            "remote_exit_status": exit_status,
            "checkpoint_interval_seconds": run_config.get("checkpoint_interval_seconds", 3600),
        },
        "recent": {
            "source": "training log file",
            "last_log_line": (payload.get("train_log_tail") or [""])[-1],
        },
    }
    (local_run_dir / "live_status.json").write_text(
        json.dumps(live_status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (local_run_dir / "huanxin_log_refresh.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    payload = run_remote(
        args.env, remote_probe_command(args.remote_output_dir, args.tail_lines), args.timeout_sec
    )
    write_local_artifacts(payload, args.local_run_dir)
    print(
        json.dumps(
            {
                "ok": True,
                "status": status_from_payload(payload),
                "local_run_dir": str(args.local_run_dir),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
