#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def format_percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{100.0 * float(value):.1f}%"


def render(output_dir: Path) -> str:
    live = load_json(output_dir / "live_status.json")
    if live is None:
        return f"missing {output_dir / 'live_status.json'}"

    summary = dict(live.get("summary") or {})
    recent = dict(live.get("recent") or {})
    checkpoint = dict(live.get("latest_checkpoint") or {})
    online_eval = dict(live.get("online_eval_latest") or {})
    last_record = dict(live.get("last_record") or {})

    lines = [
        f"status: {live.get('status', 'unknown')}",
        f"elapsed_seconds: {live.get('elapsed_seconds', 'n/a')}",
        (
            "steps: "
            f"{summary.get('recorded_steps', 0)}/{live.get('planned_steps', '?')} "
            f"(updated={summary.get('updated_steps', 0)} skipped={summary.get('skipped_steps', 0)})"
        ),
        f"recent_mean_reward: {recent.get('mean_reward', 'n/a')}",
        f"recent_mean_pass_rate: {format_percent(recent.get('mean_pass_rate'))}",
        f"recent_mean_loss: {recent.get('mean_loss', 'n/a')}",
        f"recent_read_before_write_rate: {format_percent(recent.get('mean_read_before_write_rate'))}",
        f"recent_tests_before_final_rate: {format_percent(recent.get('mean_tests_before_final_rate'))}",
        f"recent_no_tool_call_rate: {format_percent(recent.get('mean_no_tool_call_rate'))}",
        f"recent_think_call_rate: {recent.get('mean_think_call_rate', 'n/a')}",
        f"skip_reasons: {summary.get('skip_reasons', {})}",
        f"termination_counts: {recent.get('termination_counts', {})}",
        f"trajectory_tool_counts: {last_record.get('trajectory_tool_counts', {})}",
        (
            "last_record: "
            f"step={last_record.get('step', 'n/a')} "
            f"task={last_record.get('task', 'n/a')} "
            f"reward={last_record.get('mean_reward', 'n/a')} "
            f"pass_rate={format_percent(last_record.get('pass_rate'))}"
        ),
        (
            "latest_checkpoint: "
            f"step={checkpoint.get('step', 'n/a')} "
            f"saved_count={checkpoint.get('saved_count', 'n/a')} "
            f"dir={checkpoint.get('checkpoint_dir', 'n/a')}"
        ),
    ]

    alerts = list(live.get("alerts") or [])
    if alerts:
        lines.append(f"alerts: {len(alerts)}")
        for alert in alerts[:5]:
            lines.append(f"alert: {alert}")
    else:
        lines.append("alerts: none")

    if online_eval:
        lines.extend(
            [
                (
                    "online_eval: "
                    f"step={online_eval.get('step', 'n/a')} "
                    f"tasks={online_eval.get('task_count', 'n/a')} "
                    f"pass_rate={format_percent(online_eval.get('pass_rate'))} "
                    f"mean_reward={online_eval.get('mean_total_reward', 'n/a')}"
                ),
                f"online_eval_failure_categories: {online_eval.get('failure_categories', {})}",
                f"online_eval_termination_counts: {online_eval.get('termination_counts', {})}",
            ]
        )
    else:
        lines.append("online_eval: n/a")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the latest agentic GRPO training status.")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--watch", type=float, default=0.0, help="Refresh every N seconds until interrupted."
    )
    args = parser.parse_args()

    while True:
        print(render(args.output_dir), flush=True)
        if args.watch <= 0:
            break
        print("", flush=True)
        time.sleep(args.watch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
