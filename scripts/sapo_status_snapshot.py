#!/usr/bin/env python3
"""Compact live snapshot of the SAPO training process for chat display.

One small JSON (or text) block with everything the manager renders in the
standup: trainer alive?, latest steps (loss, rewards, reduction, drift,
zero-change alarm), newest checkpoint + drift verdict, train-log last stage.

Designed to run on the box (CPU, no imports beyond stdlib+safetensors-free).
"""
# ruff: noqa: UP038  # (X | Y) isinstance is py3.10-only; py3.9 .venv gate (precedent: training/grpo_trainer.py)

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

QG_ROOT = os.environ.get("QG_ROOT", "/root/work/software/quantum-gpt")


# Run/log naming families: the deployed ASI2 loop (asi2_watchdog_relaunch.sh /
# asi2_launch_grpo_27b_selfeval.sh) writes outputs/grpo-27b-selfeval-<ts> and
# logs/grpo_27b_selfeval/grpo_train_<ts>.log; the legacy direct launcher used
# outputs/sapo-27b-ai-<ts> and logs/sapo_27b_ai. Both are discovered and the
# newest wins by the trailing RUN_ID timestamp (%Y%m%dT%H%M%S[Z] — the final
# dash-segment of the name, identical across families; the family PREFIX must
# not take part in the sort, or a 2026-08-25 'grpo-27b-...' run would sort
# OLDER than a 2026-08-24 'sapo-27b-...' run). The newest run dir is selected
# regardless of whether its metrics file exists yet: a booting run (trainer
# still loading, first step not emitted) must be displayed with empty steps,
# never silently replaced by the PREVIOUS run's stale display.
_RUN_DIR_GLOBS = ("grpo-27b-selfeval-*", "sapo-27b-ai-*")
_TRAIN_LOG_GLOBS = ("logs/grpo_27b_selfeval/grpo_train_*.log", "logs/sapo_27b_ai/grpo_train_*.log")


def _run_ts_key(p: Path) -> tuple[str, str]:
    """(RUN_ID timestamp, full name) — sorts across naming families by the
    shared trailing timestamp segment first, ties broken by full name."""
    return (p.name.rsplit("-", 1)[-1], p.name)


def newest_run_dir(root: Path) -> Path | None:
    cands = sorted(
        (p for glob in _RUN_DIR_GLOBS for p in (root / "outputs").glob(glob) if p.is_dir()),
        key=_run_ts_key,
    )
    return cands[-1] if cands else None


def newest_train_log(root: Path, run_dir: Path | None) -> Path | None:
    logs = sorted(
        (p for glob in _TRAIN_LOG_GLOBS for p in root.glob(glob) if p.is_file()),
        key=_run_ts_key,
    )
    if not logs:
        return None
    # 2026-08-26 (code-review F14): match the log to the DISPLAYED run when
    # one is known (both carry the RUN_ID timestamp suffix); the global
    # newest is only a fallback for the no-run-dir display.
    if run_dir is not None:
        run_ts = str(run_dir.name).rsplit("-", 1)[-1]
        for log in reversed(logs):
            if run_ts in log.name:
                return log
    return logs[-1]


def last_stage_line(log: Path) -> str | None:
    """Last json-ish stage line in the train log (skip tqdm noise)."""
    last = None  # a stage-less boot log is honest None, never a crash
    try:
        with open(log, errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("{") and '"stage"' in line:
                    last = line
        return last
    except OSError:
        return None


def snapshot(run_dir: Path | None, root: Path, steps: int = 3) -> dict:
    # Discovery lives HERE (not just in main()) so every caller gets the
    # same newest-run selection; None means "no run dir found at all".
    if run_dir is None:
        run_dir = newest_run_dir(root)
    out: dict = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "trainer_alive": False,
        "run_dir": str(run_dir) if run_dir else None,
        "steps": [],
        "train_log_tail_stage": None,
        "zero_change_alarm": False,
        "newest_checkpoint": None,
        "drift": None,
    }
    if run_dir is None:
        return out

    metrics = run_dir / "grpo_step_metrics.jsonl"
    records: list[dict] = []
    if metrics.exists():
        try:
            with open(metrics, errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("{"):
                        # Per-line tolerance: a torn mid-append line must not
                        # truncate the displayed tail (same rule the drift
                        # watcher uses on drift.jsonl).
                        try:
                            parsed = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(parsed, dict):
                            records.append(parsed)
        except OSError as exc:
            # bug-hunter 2026-09-01: a metrics file that EXISTS but cannot be
            # READ silently produced "0 steps, reason hidden" — the display
            # lie class. Surface the read failure instead.
            out["metrics_read_error"] = f"{type(exc).__name__}: {exc}"
    # 2026-08-26 (code-review F13): the header alarm scans the ENTIRE
    # history, not just the displayed tail window — an alarm older than the
    # window must not silently vanish from the header.
    out["zero_change_alarm"] = any(bool(rec.get("zero_change_alarm")) for rec in records)
    out["steps"] = []
    for rec in records[-steps:]:
        out["steps"].append(
            {
                "step": rec.get("step"),
                "ts_utc": rec.get("timestamp_utc") or rec.get("ts"),
                "loss": rec.get("loss"),
                "loss_recomputed": (rec.get("loss_breakdown") or {}).get("loss_recomputed"),
                "mean_reward": rec.get("mean_reward"),
                "pass_rate": rec.get("pass_rate"),
                "rollout_rewards": rec.get("rollout_rewards"),
                "per_candidate_losses": rec.get("per_candidate_losses"),
                "loss_reduction": rec.get("loss_reduction"),
                "lora_b_max_delta": rec.get("lora_b_max_delta"),
                "zero_change_alarm": bool(rec.get("zero_change_alarm")),
                "skipped": rec.get("skipped"),
                "reason": rec.get("reason"),
            }
        )

    # newest checkpoint (atomic step_*_adapter) + drift verdicts
    ckpts = sorted(
        (p for p in run_dir.glob("step_*_adapter") if (p / "adapter_config.json").exists()),
        key=lambda p: p.name,
    )
    if ckpts:
        out["newest_checkpoint"] = ckpts[-1].name
    # 2026-08-26 (code-review F15): the drift verdict must belong to the
    # DISPLAYED run (the precheck files carry the run ts in their name); the
    # global newest-mtime fallback only applies when no run matches — a
    # booting run must not display the previous run's verdict.
    deltas = sorted(
        (root / "outputs").glob("adapter_delta_*.json"), key=lambda p: p.stat().st_mtime
    )
    drift_file = None
    if deltas:
        run_ts = str(run_dir.name).rsplit("-", 1)[-1]
        drift_file = next((p for p in reversed(deltas) if run_ts in p.name), deltas[-1])
    if drift_file is not None:
        try:
            d = json.loads(drift_file.read_text())
            out["drift"] = {
                "file": drift_file.name,
                "verdict": d.get("verdict"),
                "max_abs_diff": d.get("max_abs_diff"),
                "max_abs_lora_b": d.get("max_abs_lora_b"),
                "any_active": d.get("any_active"),
            }
        except (OSError, json.JSONDecodeError) as exc:
            # bug-hunter 2026-09-01: a corrupt/unreadable delta file silently
            # showed "no drift" — surface the read failure instead.
            out["drift_read_error"] = f"{type(exc).__name__}: {exc}"
    driftl = run_dir / "drift.jsonl"
    if driftl.exists():
        drift_lines: list[dict] = []
        n_skipped = 0
        try:
            for line in driftl.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError:
                    n_skipped += 1
                    continue
                if isinstance(parsed, dict):
                    drift_lines.append(parsed)
        except OSError as exc:
            # bug-hunter 2026-09-01: same lie class — a drift_watch file that
            # cannot be read must not silently erase the whole display block.
            out["drift_watch_read_error"] = f"{type(exc).__name__}: {exc}"
        # bug-hunter 2026-09-01: per-line tolerance (same rule as the metrics
        # read) — a torn mid-append line must not wipe the displayed tail.
        out["drift_watch"] = drift_lines[-1] if drift_lines else None
        if n_skipped:
            out["drift_watch_lines_skipped"] = n_skipped

    log = newest_train_log(root, run_dir)
    if log is not None:
        out["train_log"] = str(log)
        out["train_log_tail_stage"] = last_stage_line(log)

    # trainer alive check (bracket trick so the pgrep wrapper can't self-match)
    try:
        pids = os.popen("pgrep -f 'python3.*grpo[_]trainer'").read().split()
        out["trainer_alive"] = len([p for p in pids if p.strip()]) > 0
    except OSError:
        pass
    return out


def render_text(snap: dict) -> str:
    lines = [f"SAPO TRAINING DISPLAY {snap['generated_at_utc'][:19]}Z"]
    lines.append(f"trainer_alive: {snap['trainer_alive']}  run: {snap['run_dir'] or 'none'}")
    for s in snap["steps"]:
        rw = s.get("rollout_rewards")
        rw_txt = ""
        if isinstance(rw, list):
            rw_txt = (
                " rewards="
                + ",".join(
                    str(
                        (
                            r.get("pass"),
                            round(r.get("total_reward"), 3)
                            if isinstance(r.get("total_reward"), (int, float))
                            else r.get("total_reward"),
                        )
                    )
                    for r in rw
                    if isinstance(r, dict)
                )[:160]
            )
        lines.append(
            f"  step {s['step']} ts={s['ts_utc']} loss={s['loss']} recomputed={s['loss_recomputed']} "
            f"pass={s['pass_rate']} mean_reward={s['mean_reward']} skipped={s['skipped']} "
            f"zero_change={s['zero_change_alarm']} loraB_delta={s['lora_b_max_delta']}{rw_txt}"
        )
        # full per-step number set: per-candidate losses + advantages + reduction
        pcl = s.get("per_candidate_losses")
        if isinstance(pcl, list) and pcl:
            losses = ",".join(
                str(
                    round(c.get("loss_i"), 3)
                    if isinstance(c.get("loss_i"), (int, float))
                    else c.get("loss_i")
                )
                for c in pcl
                if isinstance(c, dict)
            )[:160]
            advs = ",".join(
                str(
                    round(c.get("advantage"), 3)
                    if isinstance(c.get("advantage"), (int, float))
                    else c.get("advantage")
                )
                for c in pcl
                if isinstance(c, dict)
            )[:160]
            if losses:
                lines.append(f"    per_candidate_losses=[{losses}]")
            if advs:
                lines.append(f"    advantages=[{advs}]")
        if s.get("loss_reduction"):
            lines.append(f"    reduction: {s['loss_reduction'][:140]}")
    lines.append(f"newest_checkpoint: {snap['newest_checkpoint']}")
    if snap.get("drift"):
        d = snap["drift"]
        lines.append(
            f"drift: {d['file']} verdict={d['verdict']} max_abs_diff={d['max_abs_diff']} any_active={d['any_active']}"
        )
    lines.append(f"train_log_tail_stage: {str(snap['train_log_tail_stage'])[:200]}")
    # bug-hunter 2026-09-01: read failures must be VISIBLE in the text
    # display, never silently degrade to "no data".
    for marker in (
        "metrics_read_error",
        "drift_read_error",
        "drift_watch_read_error",
    ):
        if snap.get(marker):
            lines.append(f"WARN {marker}: {snap[marker]}")
    if snap.get("drift_watch_lines_skipped"):
        lines.append(f"WARN drift_watch: {snap['drift_watch_lines_skipped']} torn line(s) skipped")
    if snap["zero_change_alarm"]:
        lines.append("*** ZERO_CHANGE_ALARM IN HISTORY — SEE RECORDS ***")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--root", default=QG_ROOT)
    ap.add_argument("--steps", type=int, default=3)
    ap.add_argument("--format", choices=["json", "text"], default="json")
    args = ap.parse_args()
    root = Path(args.root)
    run_dir = Path(args.run_dir) if args.run_dir else newest_run_dir(root)
    snap = snapshot(run_dir, root, args.steps)
    if args.format == "text":
        print(render_text(snap))
    else:
        print(json.dumps(snap, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
