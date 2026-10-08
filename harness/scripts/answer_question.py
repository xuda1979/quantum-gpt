#!/usr/bin/env python3
"""answer_question.py — convert high-level questions into data-collection.

"Why is progress slow?" → collect_metrics
"How to improve the algorithm?" → collect_training_health
"throughput?" → collect_worker_throughput
"churn/waste?" → collect_card_churn

This script COLLECTS data. The LLM analyzes and iterates.

Usage:
    python3 harness/scripts/answer_question.py "why is progress slow?"
    python3 harness/scripts/answer_question.py --collect metrics
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"
sys.path.insert(0, str(REPO / "harness" / "scripts"))
from status_collectors import (  # noqa: E402
    collect_eval,
    collect_queue,
    collect_training,
)

QUESTION_MAP = {
    "slow": "metrics",
    "progress": "metrics",
    "improve": "training_health",
    "algorithm": "training_health",
    "throughput": "worker_throughput",
    "worker": "worker_throughput",
    "churn": "card_churn",
    "waste": "card_churn",
}


def collect_metrics() -> dict:
    """Objective metrics: eval, commits, training, cards. <3s."""
    today = time.strftime("%Y-%m-%d")
    proc = subprocess.run(
        ["git", "log", "--oneline", f"--since={today}T00:00:00"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=5,
    )
    commits = len(proc.stdout.strip().splitlines()) if proc.stdout.strip() else 0
    return {
        "best_eval_pass": collect_eval()["best_pass"],
        "commits_today": commits,
        "training": collect_training(),
        "cards": collect_queue()["by_status"],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def collect_training_health() -> dict:
    """Training health: probe + metrics + liveness tail. <2s."""
    return {"probe": collect_training()}


def collect_worker_throughput() -> dict:
    """Worker throughput: agents, card completion. <3s."""
    proc = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
    agents = sum(
        1
        for line in proc.stdout.splitlines()
        if "claude" in line
        and ("--print" in line or "--bare" in line or "-p " in line)
        and "grep" not in line
    )
    q = collect_queue()
    return {
        "active_agents": agents,
        "cards_total": q["total_cards"],
        "completion_rate": f"{q['by_status'].get('done', 0)}/{q['total_cards']}"
        if q["total_cards"]
        else "N/A",
        "bounce_rate": f"{q['by_status'].get('bounced', 0)}/{q['total_cards']}"
        if q["total_cards"]
        else "N/A",
    }


def collect_card_churn() -> dict:
    """Card churn: spawned vs done vs bounced. <2s."""
    q = collect_queue()
    s = q["by_status"]
    spawned = q["total_cards"]
    done = s.get("done", 0)
    bounced = s.get("bounced", 0)
    dead = s.get("dead", 0)
    return {
        "total_spawned": spawned,
        "total_done": done,
        "total_bounced": bounced,
        "total_dead": dead,
        "churn_ratio": f"{bounced + dead}/{spawned}" if spawned else "N/A",
        "efficiency": f"{done}/{spawned}" if spawned else "N/A",
    }


def answer_question(question: str) -> dict:
    """Route question to collector. <1s."""
    q_lower = question.lower()
    name = "metrics"
    for kw, collector in QUESTION_MAP.items():
        if kw in q_lower:
            name = collector
            break
    collectors = {
        "metrics": collect_metrics,
        "training_health": collect_training_health,
        "worker_throughput": collect_worker_throughput,
        "card_churn": collect_card_churn,
    }
    return {"question": question, "data_collected": name, "data": collectors[name]()}


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Questions → data collection")
    ap.add_argument("question", nargs="?")
    ap.add_argument(
        "--collect", choices=["metrics", "training_health", "worker_throughput", "card_churn"]
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.collect:
        collectors = {
            "metrics": collect_metrics,
            "training_health": collect_training_health,
            "worker_throughput": collect_worker_throughput,
            "card_churn": collect_card_churn,
        }
        data = collectors[args.collect]()
    elif args.question:
        data = answer_question(args.question)
    else:
        ap.print_help()
        sys.exit(1)
    print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
