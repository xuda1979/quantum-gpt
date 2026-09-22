#!/usr/bin/env python3
"""answer_question.py — convert high-level questions into data-collection scripts.

"Why is progress slow?" → runs scripts that measure: commits/day, eval pass rate,
training steps/hr, worker throughput, card churn rate, bounce rate.
"How to improve the algorithm?" → runs scripts that collect: reward curve,
loss curve, candidate dispersion, failure classification per task.

This script DOES NOT answer the question — it COLLECTS the data the LLM needs
to answer it. The LLM then iterates: write more scripts, run them, analyze.

Usage:
    python3 harness/scripts/answer_question.py "why is progress slow?"
    python3 harness/scripts/answer_question.py "how to improve the algorithm"
    python3 harness/scripts/answer_question.py --collect metrics
    python3 harness/scripts/answer_question.py --collect training_health
    python3 harness/scripts/answer_question.py --collect worker_throughput
    python3 harness/scripts/answer_question.py --collect card_churn
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
STATE = REPO / "harness" / "state"


def collect_metrics() -> dict:
    """Collect all objective metrics: eval pass rate, training status, commit rate."""
    # Eval pass rate from verdicts
    verdicts_dir = STATE / "verdicts"
    best_pass = 0
    total_verdicts = 0
    if verdicts_dir.exists():
        for f in verdicts_dir.glob("*.json"):
            try:
                d = json.loads(f.read_text())
                total_verdicts += 1
                pa = d.get("pass_adapter", "0/18")
                m = re.match(r"(\d+)/(\d+)", str(pa))
                if m and int(m.group(1)) > best_pass:
                    best_pass = int(m.group(1))
            except (json.JSONDecodeError, KeyError):
                pass

    # Commits today
    today = time.strftime("%Y-%m-%d")
    proc = subprocess.run(
        ["git", "log", "--oneline", f"--since={today}T00:00:00"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    commits_today = len(proc.stdout.strip().splitlines()) if proc.stdout.strip() else 0

    # Training probe
    train_probe = STATE / "probes" / "train.json"
    train_status = "UNKNOWN"
    if train_probe.exists():
        try:
            train_status = json.loads(train_probe.read_text()).get("status", "UNKNOWN")
        except (json.JSONDecodeError, KeyError):
            pass

    # Queue stats
    queue_path = STATE / "QUEUE.json"
    card_stats = {"total": 0, "running": 0, "bounced": 0, "done": 0, "blocked": 0, "dead": 0}
    if queue_path.exists():
        try:
            q = json.loads(queue_path.read_text())
            cards = q.get("cards", [])
            card_stats["total"] = len(cards)
            for c in cards:
                s = c.get("status", "unknown")
                if s in card_stats:
                    card_stats[s] += 1
        except (json.JSONDecodeError, KeyError):
            pass

    return {
        "best_eval_pass": f"{best_pass}/18",
        "total_verdicts": total_verdicts,
        "commits_today": commits_today,
        "training_status": train_status,
        "cards": card_stats,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def collect_training_health() -> dict:
    """Collect training health: reward curve, loss, step rate, dispersion."""
    # Check train probe
    train_probe = STATE / "probes" / "train.json"
    probe_data = {}
    if train_probe.exists():
        try:
            probe_data = json.loads(train_probe.read_text())
        except (json.JSONDecodeError, KeyError):
            pass

    # Check metrics log
    metrics_log = REPO / ".sapo-loop" / "metrics.md.log"
    recent_metrics = []
    if metrics_log.exists():
        lines = metrics_log.read_text(errors="replace").splitlines()
        for line in lines[-20:]:
            if line.strip():
                recent_metrics.append(line.strip())

    # Check trainer liveness log
    trainer_log = REPO / ".sapo-loop" / "trainer_liveness.log"
    trainer_events = []
    if trainer_log.exists():
        lines = trainer_log.read_text(errors="replace").splitlines()
        for line in lines[-10:]:
            if line.strip():
                trainer_events.append(line.strip())

    return {
        "probe": probe_data,
        "recent_metrics": recent_metrics[-10:],
        "trainer_liveness_tail": trainer_events[-5:],
    }


def collect_worker_throughput() -> dict:
    """Measure worker throughput: active agents, card completion rate, avg card lifetime."""
    # Count active claude worker processes
    proc = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    agent_count = sum(
        1
        for line in proc.stdout.splitlines()
        if "claude" in line
        and ("--print" in line or "--bare" in line or "-p " in line)
        and "grep" not in line
    )

    # Card throughput from queue
    queue_path = STATE / "QUEUE.json"
    done_count = 0
    bounced_count = 0
    total_cards = 0
    if queue_path.exists():
        try:
            q = json.loads(queue_path.read_text())
            for c in q.get("cards", []):
                total_cards += 1
                if c.get("status") == "done":
                    done_count += 1
                elif c.get("status") == "bounced":
                    bounced_count += 1
        except (json.JSONDecodeError, KeyError):
            pass

    # Events for completion rate
    events_path = STATE / "EVENTS.jsonl"
    recent_events = []
    if events_path.exists():
        lines = events_path.read_text(errors="replace").splitlines()
        for line in lines[-50:]:
            try:
                ev = json.loads(line)
                if ev.get("event") in ("card_done", "card_bounced", "card_spawned"):
                    recent_events.append(
                        {"event": ev["event"], "card": ev.get("card"), "ts": ev.get("ts", "")}
                    )
            except (json.JSONDecodeError, KeyError):
                pass

    return {
        "active_agents": agent_count,
        "cards_total": total_cards,
        "cards_done": done_count,
        "cards_bounced": bounced_count,
        "completion_rate": f"{done_count}/{total_cards}" if total_cards > 0 else "N/A",
        "bounce_rate": f"{bounced_count}/{total_cards}" if total_cards > 0 else "N/A",
        "recent_events": recent_events[-20:],
    }


def collect_card_churn() -> dict:
    """Measure card churn: how many cards are being created vs completed."""
    events_path = STATE / "EVENTS.jsonl"
    spawned = 0
    done = 0
    bounced = 0
    dead = 0
    if events_path.exists():
        for line in events_path.read_text(errors="replace").splitlines():
            try:
                ev = json.loads(line)
                etype = ev.get("event", "")
                if etype == "card_spawned":
                    spawned += 1
                elif etype == "card_done":
                    done += 1
                elif etype == "card_bounced":
                    bounced += 1
                elif etype == "card_dead":
                    dead += 1
            except (json.JSONDecodeError, KeyError):
                pass

    return {
        "total_spawned": spawned,
        "total_done": done,
        "total_bounced": bounced,
        "total_dead": dead,
        "churn_ratio": f"{(bounced + dead)}/{spawned}" if spawned > 0 else "N/A",
        "efficiency": f"{done}/{spawned}" if spawned > 0 else "N/A",
    }


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


def answer_question(question: str) -> dict:
    """Route a natural-language question to the right data collector."""
    q_lower = question.lower()
    collector_name = "metrics"  # default
    for keyword, collector in QUESTION_MAP.items():
        if keyword in q_lower:
            collector_name = collector
            break

    collectors = {
        "metrics": collect_metrics,
        "training_health": collect_training_health,
        "worker_throughput": collect_worker_throughput,
        "card_churn": collect_card_churn,
    }
    collector = collectors.get(collector_name, collect_metrics)
    data = collector()
    return {
        "question": question,
        "data_collected": collector_name,
        "data": data,
        "note": "This script COLLECTS data. The LLM must analyze this data and iterate: write more scripts to drill deeper.",
    }


def main():
    ap = argparse.ArgumentParser(description="Convert questions into data-collection scripts")
    ap.add_argument("question", nargs="?", help="natural-language question")
    ap.add_argument(
        "--collect",
        choices=["metrics", "training_health", "worker_throughput", "card_churn"],
        help="directly specify data collector",
    )
    ap.add_argument("--json", action="store_true", help="output JSON")
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

    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
